# Quick Start Guide - AutoCbot

Get up and running in 30 minutes!

---

## Prerequisites

- Python 3.11 or higher
- Binance account with KYC verified
- $100-1000 starting capital
- Basic command-line knowledge

---

## Step 1: Installation (5 minutes)

```bash
# Navigate to project directory
cd AutoCbot

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
freqtrade --version
```

Expected output: `freqtrade 2024.10` or higher

---

## Step 2: Binance Setup (10 minutes)

### Create API Keys

1. Login to [Binance](https://www.binance.com)
2. Go to **Profile > API Management**
3. Create new API key
4. **IMPORTANT:** Enable only:
   - ✅ Enable Reading
   - ✅ Enable Spot & Margin Trading
   - ❌ **DISABLE** Enable Withdrawals
5. Save your API Key and Secret

### Configure IP Whitelist (Optional but recommended)

1. In API settings, add your IP address
2. This prevents unauthorized access

---

## Step 3: Configuration (5 minutes)

### Setup Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit with your API keys
nano .env
```

Add your Binance credentials:
```
BINANCE_API_KEY=your_actual_api_key_here
BINANCE_API_SECRET=your_actual_secret_here
```

### Setup Freqtrade Config

```bash
# Copy template
cp config.json.example config.json

# Edit config.json
nano config.json
```

Update these fields:
```json
{
  "dry_run": true,  // Keep true for paper trading
  "exchange": {
    "name": "binance",
    "key": "your_api_key",
    "secret": "your_api_secret"
  }
}
```

---

## Step 4: Download Data (5 minutes)

```bash
# Download historical data for backtesting
freqtrade download-data \
    --exchange binance \
    --pairs BTC/USDT ETH/USDT \
    --timeframe 5m \
    --days 180
```

This downloads ~180 days of 5-minute candles for BTC and ETH.

---

## Step 5: Backtest (5 minutes)

```bash
# Test the base strategy
freqtrade backtesting \
    --strategy MeanReversionBase \
    --timerange 20240101-20241001
```

**Look for:**
- ✅ Total profit > 0%
- ✅ Win rate > 55%
- ✅ Sharpe ratio > 1.0
- ✅ Max drawdown < 20%

**Example good results:**
```
Total Profit: 45.23%
Win Rate: 61.2%
Sharpe Ratio: 1.45
Max Drawdown: 12.3%
```

---

## Step 6: Paper Trading (2+ weeks)

```bash
# Start bot in dry-run mode (paper trading)
freqtrade trade \
    --config config.json \
    --strategy MeanReversionBase
```

**Monitor for at least 2 weeks:**
- No crashes
- Reasonable number of trades (5-20 per day)
- Positive or break-even performance
- Stop-losses working correctly

**Stop with:** `Ctrl+C`

---

## Step 7: Monitor Performance

### Terminal Monitoring

```bash
# In a new terminal window
freqtrade status
freqtrade profit
```

### Dashboard (Optional)

```bash
# Start Streamlit dashboard
streamlit run scripts/monitor.py

# Open browser to http://localhost:8501
```

---

## Optional: ML-Enhanced Strategy

If you want to use the machine learning enhanced strategy:

### Train Model

```bash
# Open Jupyter notebook
jupyter notebook user_data/notebooks/train_model.ipynb
```

1. Run all cells in order
2. Wait for training to complete (~10-30 minutes)
3. Model saved to `user_data/models/`

### Use ML Strategy

```bash
# Use ML-enhanced strategy instead
freqtrade trade \
    --config config.json \
    --strategy MeanReversionML
```

---

## Going Live Checklist

Only proceed after 2+ weeks successful paper trading!

- [ ] Paper trading profitable or break-even
- [ ] No technical issues
- [ ] Understand all commands
- [ ] API keys have NO withdrawal permissions
- [ ] Start with $100-200 only

### Go Live

1. **Stop paper trading:** `Ctrl+C`

2. **Update config.json:**
   ```json
   {
     "dry_run": false,
     "stake_amount": "unlimited",
     "max_open_trades": 3
   }
   ```

3. **Start live trading:**
   ```bash
   freqtrade trade \
       --config config.json \
       --strategy MeanReversionBase
   ```

4. **Monitor closely** for first 24-48 hours

---

## Daily Routine

1. **Morning:** Check status and profit
   ```bash
   freqtrade status
   freqtrade profit
   ```

2. **Evening:** Review trades
   ```bash
   freqtrade show-trades --days 1
   ```

3. **Watch for alerts:**
   - Drawdown > 15%: Consider pausing
   - Multiple losses: Review strategy
   - No trades for days: Check configuration

---

## Emergency Stop

If you need to stop immediately:

```bash
# Stop all trading
Ctrl+C

# Close all positions (if needed)
freqtrade forceexit all
```

---

## Common Issues

### "No trades being made"

**Solutions:**
1. Check market volatility - mean reversion needs ranging markets
2. Lower ADX threshold in strategy (default: 25)
3. Verify data is downloading: `ls -la user_data/data/binance/`

### "API rate limit exceeded"

**Solution:** Increase rate limit in config.json:
```json
{
  "exchange": {
    "ccxt_config": {
      "rateLimit": 100
    }
  }
}
```

### "Strategy not found"

**Solution:** Verify strategy files exist:
```bash
ls -la user_data/strategies/
freqtrade list-strategies
```

---

## Next Steps

After 1 month of successful live trading:

1. **Scale up** - Increase capital gradually
2. **Optimize** - Run hyperparameter optimization
3. **Retrain ML** - Update model with recent data
4. **Diversify** - Add more pairs
5. **Tax planning** - Track for Costa Rica taxes

---

## Support

- **Freqtrade Docs:** https://www.freqtrade.io/
- **Discord:** https://discord.gg/p7nuUNVfP7
- **Issues:** Check logs in terminal

---

## Tips for Success

1. **Start small** - $100-200 is plenty to learn
2. **Be patient** - Mean reversion needs time
3. **Monitor daily** - But don't overtrade manually
4. **Keep records** - For taxes and analysis
5. **Scale slowly** - Only after consistent profits

---

**You're ready! Good luck! 🚀**
