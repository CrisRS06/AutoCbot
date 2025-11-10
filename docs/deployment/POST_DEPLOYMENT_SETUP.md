# POST-DEPLOYMENT SETUP GUIDE
**AutoCbot MVP - Production Monitoring & Maintenance**

**Date:** 2025-11-10
**Status:** Required for Production

---

## 1. TOKEN BLACKLIST CLEANUP (REQUIRED)

### Purpose
Prevent the token_blacklist table from growing indefinitely by removing expired tokens.

### Setup Cron Job

**Option A: Daily Cleanup (Recommended)**
```bash
# Run at 2 AM daily
0 2 * * * cd /path/to/AutoCbot/backend && python scripts/cleanup_token_blacklist.py >> /var/log/autocbot/cleanup.log 2>&1
```

**Option B: Weekly Cleanup (Minimal)**
```bash
# Run at 3 AM every Sunday
0 3 * * 0 cd /path/to/AutoCbot/backend && python scripts/cleanup_token_blacklist.py >> /var/log/autocbot/cleanup.log 2>&1
```

### Manual Execution
```bash
# Dry run (see what would be deleted)
cd backend
python scripts/cleanup_token_blacklist.py --dry-run

# Show statistics only
python scripts/cleanup_token_blacklist.py --stats-only

# Actual cleanup
python scripts/cleanup_token_blacklist.py
```

### Expected Output
```
2025-11-10 02:00:01 - __main__ - INFO - 🧹 Starting token blacklist cleanup...
2025-11-10 02:00:01 - __main__ - INFO - Token Blacklist Statistics:
2025-11-10 02:00:01 - __main__ - INFO -   Total tokens: 1250
2025-11-10 02:00:01 - __main__ - INFO -   Active (not expired): 45
2025-11-10 02:00:01 - __main__ - INFO -   Expired: 1205
2025-11-10 02:00:01 - __main__ - INFO -   Expired percentage: 96.4%
2025-11-10 02:00:01 - __main__ - INFO - ✅ Successfully deleted 1205 expired tokens from blacklist
2025-11-10 02:00:01 - __main__ - INFO - Cleanup complete. Removed 1205 expired tokens.
```

---

## 2. ERROR TRACKING WITH SENTRY (RECOMMENDED)

### Setup Steps

1. **Install Sentry SDK**
```bash
cd backend
pip install sentry-sdk[fastapi]
```

2. **Update requirements.txt**
```
# Add to backend/requirements.txt
sentry-sdk[fastapi]==1.40.0
```

3. **Configure Sentry in main.py**
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Add after imports
if not settings.DEBUG and settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment="production",
        traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
        profiles_sample_rate=0.1,  # 10% for profiling
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        # Set release version for tracking
        release=f"autocbot@{app.version}",
        # Don't send PII data
        send_default_pii=False,
    )
    logger.info("✅ Sentry error tracking initialized")
```

4. **Set Environment Variable**
```bash
# In .env or production environment
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

### What Gets Tracked
- ✅ Unhandled exceptions
- ✅ HTTP 500 errors
- ✅ Database query errors
- ✅ Authentication failures (configurable)
- ✅ Performance metrics
- ✅ User context (non-PII)

---

## 3. AUTHENTICATION FAILURE MONITORING

### Setup Logging

**Add to backend/utils/auth.py**
```python
# After failed login attempts
logger.warning(
    f"Failed login attempt for email: {user_data.email} "
    f"from IP: {request.client.host if request.client else 'unknown'}"
)

# After rate limit exceeded
logger.warning(
    f"Rate limit exceeded for IP: {get_identifier(request)} "
    f"on endpoint: {request.url.path}"
)
```

### Log Aggregation (Optional)

**Option A: Simple File Monitoring**
```bash
# Monitor authentication failures
tail -f /var/log/autocbot/app.log | grep "Failed login"

# Count failures per hour
grep "Failed login" /var/log/autocbot/app.log | \
  awk '{print $1" "$2}' | uniq -c
```

**Option B: ELK Stack (Advanced)**
- Elasticsearch for log storage
- Logstash for log processing
- Kibana for visualization

**Option C: CloudWatch (AWS)**
```bash
# Send logs to CloudWatch
pip install watchtower

# Configure in logging setup
import watchtower
logging.getLogger().addHandler(
    watchtower.CloudWatchLogHandler(log_group="autocbot-production")
)
```

---

## 4. RATE LIMITING HEADERS

Rate limit information is automatically added to responses:

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 4
X-RateLimit-Reset: 1699632060
```

### Monitor Rate Limit Violations
```bash
# Count 429 responses
tail -f /var/log/nginx/access.log | grep " 429 "

# Alert on excessive rate limiting
# (indicates potential attack or misconfigured client)
```

---

## 5. DATABASE MONITORING

### Monitor Token Blacklist Growth
```sql
-- Check blacklist size
SELECT COUNT(*) as total_tokens,
       COUNT(*) FILTER (WHERE expires_at < NOW()) as expired_tokens,
       COUNT(*) FILTER (WHERE expires_at >= NOW()) as active_tokens
FROM token_blacklist;

-- Check oldest expired token
SELECT MIN(expires_at) as oldest_expired
FROM token_blacklist
WHERE expires_at < NOW();
```

### Alert Thresholds
- ⚠️ Warning: > 10,000 total tokens
- 🔴 Critical: > 50,000 total tokens
- ⚠️ Warning: > 80% expired tokens (cleanup not running)

---

## 6. HEALTH CHECK MONITORING

### Endpoint
```
GET /health
```

### Response
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "services": {
    "market_data": {"status": "running"},
    "sentiment": {"status": "running"},
    "fundamental": {"status": "running"},
    "database": {"status": "connected"}
  },
  "features": {
    "rate_limiting": true,
    "security_headers": true,
    "request_id_tracking": true
  }
}
```

### Setup Uptime Monitoring

**Option A: UptimeRobot (Free)**
- Monitor `/health` endpoint every 5 minutes
- Alert via email/Slack on downtime

**Option B: Pingdom (Paid)**
- Advanced monitoring with RUM
- Performance metrics
- Multi-location checks

**Option C: Custom Script**
```bash
#!/bin/bash
# /usr/local/bin/check_autocbot_health.sh

HEALTH_URL="https://your-domain.com/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -ne 200 ]; then
    echo "⚠️ AutoCbot health check failed with status $RESPONSE"
    # Send alert (email, Slack, PagerDuty, etc.)
    /usr/local/bin/send_alert.sh "AutoCbot down: HTTP $RESPONSE"
fi
```

---

## 7. SECURITY MONITORING

### Failed Authentication Attempts
```bash
# Create alert for brute force attempts
# Alert if > 10 failed logins from same IP in 5 minutes
grep "Failed login" /var/log/autocbot/app.log | \
  awk '{print $NF}' | sort | uniq -c | \
  awk '$1 > 10 {print "⚠️ Potential brute force from IP: " $2}'
```

### Rate Limit Violations
```bash
# Monitor for API abuse
# Alert if > 100 rate limit violations in 1 hour
grep "Rate limit exceeded" /var/log/autocbot/app.log | \
  tail -n 1000 | wc -l
```

### Suspicious Activity Indicators
- Multiple failed login attempts from single IP
- Rapid token refresh requests
- Unusual geographic access patterns
- High rate of 401/403 errors

---

## 8. BACKUP & DISASTER RECOVERY

### Database Backups

**Daily Backup Script**
```bash
#!/bin/bash
# /usr/local/bin/backup_autocbot_db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/autocbot"
DB_PATH="/path/to/autocbot.db"

# Create backup
mkdir -p $BACKUP_DIR
sqlite3 $DB_PATH ".backup $BACKUP_DIR/autocbot_$DATE.db"

# Compress
gzip $BACKUP_DIR/autocbot_$DATE.db

# Keep only last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "✅ Backup completed: autocbot_$DATE.db.gz"
```

**Cron Schedule**
```bash
# Run at 1 AM daily
0 1 * * * /usr/local/bin/backup_autocbot_db.sh >> /var/log/autocbot/backup.log 2>&1
```

### Test Restore Procedure
```bash
# Test restore quarterly
gunzip -c /backups/autocbot/autocbot_20251110.db.gz > /tmp/test_restore.db
sqlite3 /tmp/test_restore.db "SELECT COUNT(*) FROM users;"
```

---

## 9. PERFORMANCE MONITORING

### Metrics to Track
1. **Response Times**
   - P50, P95, P99 latencies
   - Target: P95 < 500ms

2. **Request Rate**
   - Requests per second
   - Peak load capacity

3. **Error Rate**
   - 4xx and 5xx responses
   - Target: < 1% error rate

4. **Database Performance**
   - Query execution time
   - Connection pool utilization

### Tools
- **FastAPI Prometheus Exporter**
- **Grafana Dashboards**
- **New Relic / DataDog (Paid)**

---

## 10. ALERTING RULES

### Critical Alerts (Immediate Response)
- 🔴 Service down (health check fails)
- 🔴 Database connection lost
- 🔴 Error rate > 5%
- 🔴 Disk space < 10%

### Warning Alerts (Review within 24h)
- ⚠️ Token blacklist > 10,000 entries
- ⚠️ Error rate > 1%
- ⚠️ Response time P95 > 1s
- ⚠️ Rate limit violations > 1000/day

### Info Alerts (Weekly Review)
- ℹ️ New user registrations
- ℹ️ Token cleanup statistics
- ℹ️ Active user count
- ℹ️ API usage trends

---

## CHECKLIST

### Immediate (Day 1)
- [ ] Set up token blacklist cleanup cron job
- [ ] Configure Sentry error tracking
- [ ] Set up basic health check monitoring
- [ ] Configure log rotation
- [ ] Test backup/restore procedure

### Week 1
- [ ] Review authentication failure logs
- [ ] Monitor rate limit violations
- [ ] Check token blacklist growth
- [ ] Verify cleanup script ran successfully

### Ongoing
- [ ] Weekly: Review error logs and metrics
- [ ] Monthly: Test backup restore
- [ ] Quarterly: Security audit
- [ ] Quarterly: Performance review

---

**For Questions or Issues:**
- Check logs: `/var/log/autocbot/`
- Review health endpoint: `/health`
- Run cleanup script: `python scripts/cleanup_token_blacklist.py --stats-only`

---

**Document Version:** 1.0
**Last Updated:** 2025-11-10
