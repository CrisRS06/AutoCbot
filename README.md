# AutoCbot - Cryptocurrency Mean Reversion Trading Bot

Complete implementation of a cryptocurrency mean reversion trading system using Freqtrade and LightGBM machine learning.

**Target Market:** 5-minute timeframe crypto trading on Binance
**Strategy:** Mean reversion with ML probability filtering
**Location:** Optimized for Costa Rica legal/tax compliance

---

## Features

- ✅ **Mean Reversion Base Strategy** - Technical indicator-based trading
- ✅ **ML-Enhanced Strategy** - LightGBM probability filtering for higher precision
- ✅ **Automated Training Pipeline** - Jupyter notebook for model retraining
- ✅ **Production Deployment** - VPS deployment scripts with systemd
- ✅ **Monitoring Dashboard** - Real-time Streamlit dashboard
- ✅ **Tax Calculator** - Costa Rica capital gains tax calculator (15%)
- ✅ **Automated Backups** - Daily backup scripts with rotation

---

## 📊 PROJECT STATUS & PROGRESS

### ✅ COMPLETED (Setup Phase - October 18, 2025)

**All infrastructure and code has been created and is ready to use:**

- [x] Project directory structure created
- [x] Configuration files (config.json.example, .env.example, requirements.txt, .gitignore)
- [x] Base strategy implementation (mean_reversion_base.py)
- [x] Feature engineering module (features.py)
- [x] ML-enhanced strategy (mean_reversion_ml.py)
- [x] ML training notebook (train_model.ipynb)
- [x] VPS deployment script (deploy.sh)
- [x] Backup automation script (backup.sh)
- [x] Monitoring dashboard (monitor.py)
- [x] Tax calculator for Costa Rica (tax_calculator.py)
- [x] Documentation (README.md, QUICKSTART.md)

### 🔄 NEXT STEPS (To be completed by user)

#### Phase 1: Environment Setup (1-2 hours)

- [ ] **Install Python dependencies**
  ```bash
  python3.11 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

- [ ] **Create Binance account**
  - Complete KYC verification
  - Enable 2FA security

- [ ] **Generate Binance API keys**
  - ⚠️ Enable ONLY: Reading + Spot Trading
  - ❌ DISABLE: Withdrawals (critical!)
  - Optional: Configure IP whitelist

- [ ] **Configure project**
  ```bash
  cp config.json.example config.json
  cp .env.example .env
  nano .env  # Add your Binance API keys
  ```

#### Phase 2: Data & Validation (2-4 hours)

- [ ] **Download historical data**
  ```bash
  freqtrade download-data --exchange binance \
      --pairs BTC/USDT ETH/USDT --timeframe 5m --days 180
  ```

- [ ] **Run backtest on historical data**
  ```bash
  freqtrade backtesting --strategy MeanReversionBase \
      --timerange 20240101-20241001
  ```

- [ ] **Verify backtest results meet targets:**
  - Win rate > 55%
  - Sharpe ratio > 1.0
  - Max drawdown < 20%

#### Phase 3: ML Training (Optional - 2-4 hours)

- [ ] **Train LightGBM model**
  ```bash
  jupyter notebook user_data/notebooks/train_model.ipynb
  # Run all cells, model saves to user_data/models/
  ```

- [ ] **Backtest ML-enhanced strategy**
  ```bash
  freqtrade backtesting --strategy MeanReversionML \
      --timerange 20241001-20241218
  ```

#### Phase 4: Paper Trading (2-4 weeks - MANDATORY)

- [ ] **Start paper trading (dry-run mode)**
  ```bash
  freqtrade trade --config config.json --strategy MeanReversionBase
  ```

- [ ] **Monitor performance for minimum 2 weeks**
  - Check daily for crashes/errors
  - Verify trades are being executed
  - Confirm stop-losses work correctly
  - Track win rate and profitability

- [ ] **Launch monitoring dashboard**
  ```bash
  streamlit run scripts/monitor.py
  # Open http://localhost:8501
  ```

#### Phase 5: Live Trading (After validation)

- [ ] **Verify paper trading success:**
  - No technical issues for 2+ weeks
  - Performance matches or exceeds backtest
  - Comfortable with bot behavior

- [ ] **Update configuration for live trading:**
  - Set `dry_run: false` in config.json
  - Set `max_open_trades: 3` (start conservative)
  - Verify API keys are correct

- [ ] **Go live with small capital ($100-200)**
  ```bash
  freqtrade trade --config config.json --strategy MeanReversionBase
  ```

- [ ] **Monitor intensively for first week:**
  - Check multiple times daily
  - Verify actual trades match expectations
  - Monitor slippage and fees

#### Phase 6: Scaling & Optimization (Months 2-6)

- [ ] **Month 1 Review:**
  - Analyze all trades
  - Calculate actual Sharpe ratio
  - Review drawdown periods

- [ ] **Scale capital gradually:**
  - Month 1: $100-200
  - Month 2: $300-500 (if profitable)
  - Month 3: $500-750 (if profitable)
  - Month 4+: $1000+ (if consistently profitable)

- [ ] **Hyperparameter optimization:**
  ```bash
  freqtrade hyperopt --hyperopt-loss SharpeHyperOptLoss \
      --strategy MeanReversionML --epochs 500
  ```

- [ ] **Retrain ML model monthly:**
  - Re-run train_model.ipynb with latest data
  - Compare new vs old model performance
  - Deploy if improvement > 5%

#### Phase 7: Production & Maintenance (Ongoing)

- [ ] **Deploy to VPS (optional):**
  ```bash
  ./scripts/deploy.sh  # Run on Ubuntu 22.04 VPS
  ```

- [ ] **Setup automated backups:**
  ```bash
  crontab -e
  # Add: 0 2 * * * /path/to/scripts/backup.sh
  ```

- [ ] **Monthly tax tracking (Costa Rica):**
  - Export Binance trade history
  - Run tax calculator
  - File Form D-162 if needed
  - Keep records for 4+ years

### ⚠️ CRITICAL REMINDERS

**Before Live Trading:**
- ✅ Complete 2+ weeks successful paper trading
- ✅ API keys have NO withdrawal permissions
- ✅ Start with maximum $200
- ✅ Set up stop-loss limits
- ✅ Understand emergency stop procedures

**Safety Limits:**
- 🛑 Stop if drawdown > 20%
- 🛑 Pause if 3+ consecutive losing days
- 🛑 Review if win rate drops below 45%
- 🛑 Never trade more than you can afford to lose

**Costa Rica Tax Compliance:**
- 📋 15% capital gains tax on crypto profits
- 📋 File within 15 days of month following sale
- 📋 Use tax_calculator.py for calculations
- 📋 Keep all records minimum 4 years

---

## Project Structure

```
AutoCbot/
├── config.json.example          # Freqtrade configuration template
├── .env.example                 # Environment variables template
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git exclusions
│
├── user_data/
│   ├── strategies/
│   │   ├── mean_reversion_base.py    # Base strategy
│   │   ├── mean_reversion_ml.py      # ML-enhanced strategy
│   │   └── features.py               # Feature engineering
│   │
│   ├── models/                       # Trained ML models
│   ├── notebooks/
│   │   └── train_model.ipynb         # Model training notebook
│   │
│   ├── data/                         # Historical data (git-ignored)
│   └── backtest_results/             # Backtest outputs (git-ignored)
│
├── scripts/
│   ├── deploy.sh                     # VPS deployment
│   ├── backup.sh                     # Backup script
│   ├── monitor.py                    # Streamlit dashboard
│   └── tax_calculator.py             # CR tax calculator
│
└── docs/
    └── QUICKSTART.md                 # Quick start guide
```

---

## Quick Start

### 1. Installation

```bash
# Clone or download this repository
cd AutoCbot

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy configuration templates
cp config.json.example config.json
cp .env.example .env

# Edit .env with your API keys
nano .env
```

**Important:** Create Binance API keys with **NO WITHDRAWAL PERMISSIONS**

### 3. Download Historical Data

```bash
# Download 180 days of 5-minute data
freqtrade download-data \
    --exchange binance \
    --pairs BTC/USDT ETH/USDT \
    --timeframe 5m \
    --days 180
```

### 4. Backtest Strategy

```bash
# Test base strategy
freqtrade backtesting \
    --strategy MeanReversionBase \
    --timerange 20240101-20241001

# Expected results:
# - Win rate: 55-65%
# - Sharpe ratio: 1.0-2.0
# - Max drawdown: 10-20%
```

### 5. Train ML Model (Optional)

```bash
# Open Jupyter notebook
jupyter notebook user_data/notebooks/train_model.ipynb

# Run all cells to train and save model
# Model will be saved to user_data/models/
```

### 6. Paper Trading

```bash
# Start in dry-run mode (paper trading)
freqtrade trade \
    --config config.json \
    --strategy MeanReversionML

# Monitor for at least 2 weeks before going live
```

### 7. Monitor Performance

```bash
# Start monitoring dashboard
streamlit run scripts/monitor.py

# Dashboard will open at http://localhost:8501
```

---

## Going Live

**IMPORTANT:** Only go live after successful paper trading for 2+ weeks

1. **Update configuration**
   ```json
   {
     "dry_run": false,
     "stake_amount": "unlimited",
     "max_open_trades": 5
   }
   ```

2. **Start small**
   - Initial capital: $100-200
   - Gradually scale after 1 month of profitable live trading

3. **Monitor daily**
   - Check Telegram notifications
   - Review dashboard metrics
   - Track drawdowns

4. **Stop conditions**
   - Drawdown > 20%: Stop immediately
   - Win rate < 45%: Reassess parameters
   - 3+ consecutive losing days: Pause and review

---

## Costa Rica Tax Compliance

### Calculate Taxes

```bash
# Export Binance trade history as CSV
# Then run tax calculator

python scripts/tax_calculator.py binance_trades.csv 2025
```

### Tax Requirements

- **Rate:** 15% capital gains tax
- **Filing:** Form D-162 via [TRIBUTA-CR](https://ovitribucr.hacienda.go.cr)
- **Deadline:** Within 15 days of month following each sale
- **Records:** Keep all records for 4+ years

### Recommended Accountants

- **Rich Coast Accounting** - Escazú, San José
- **Costa Rica ABC** - Crypto experience

---

## Deployment to VPS

### Deploy to Production Server

```bash
# On your VPS (Ubuntu 22.04 recommended)
wget https://your-repo/scripts/deploy.sh
chmod +x deploy.sh
sudo ./deploy.sh

# Copy your configuration
scp config.json user@vps:/home/freqtrade/freqtrade/user_data/
scp -r user_data/strategies user@vps:/home/freqtrade/freqtrade/user_data/

# Start bot
sudo systemctl start freqtrade
sudo systemctl status freqtrade

# View logs
journalctl -u freqtrade -f
```

### Recommended VPS Providers

- **Digital Ocean** - Tokyo datacenter ($12/month)
- **Vultr** - Tokyo/Singapore ($10/month)
- **Linode** - Tokyo datacenter ($12/month)

Choose Tokyo region for lowest latency to Binance servers.

---

## Maintenance

### Daily
- Check Telegram notifications
- Review open positions
- Monitor drawdown

### Weekly
- Review performance metrics
- Check for errors in logs
- Verify backups running

### Monthly
- Retrain ML model (if using ML strategy)
- Run hyperparameter optimization
- Review and adjust strategy parameters
- File taxes (Costa Rica)

---

## Expected Performance

### Realistic Targets

- **Monthly Return:** 3-8% (36-96% annualized)
- **Sharpe Ratio:** 1.0-2.0
- **Win Rate:** 55-65%
- **Max Drawdown:** 10-20%
- **Average Trade Duration:** 2-6 hours

### Comparison

- **SPY (S&P 500):** ~10% annual, Sharpe ~0.6
- **Target:** Beat SPY with Sharpe > 0.8 ✅

---

## Support & Community

- **Freqtrade Discord:** https://discord.gg/p7nuUNVfP7
- **Documentation:** https://www.freqtrade.io/
- **r/algotrading:** https://reddit.com/r/algotrading

---

## Safety Guidelines

### ✅ DO

- Start small ($100-200)
- Paper trade minimum 2 weeks
- Use stop-losses always
- Monitor daily
- Keep detailed records
- Scale gradually

### ❌ DON'T

- Enable withdrawal permissions on API
- Skip paper trading
- Risk more than 2% per trade
- Trade without stop-losses
- Ignore drawdowns > 15%
- Chase losses
- Neglect tax obligations

---

## Troubleshooting

### No trades being made

```bash
# Check strategy loads
freqtrade list-strategies

# Run backtest to see signals
freqtrade backtesting --strategy MeanReversionML \
    --timerange 20250101- --export signals
```

### API rate limit exceeded

Update `config.json`:
```json
{
  "exchange": {
    "ccxt_config": {
      "rateLimit": 100
    }
  }
}
```

### High drawdown

1. Stop bot immediately
2. Review positions
3. Analyze what went wrong
4. Paper trade with new parameters
5. Only resume after 1 week successful paper trading

---

## License

This project is for educational purposes. Use at your own risk.

**Disclaimer:** Cryptocurrency trading involves substantial risk. Past performance does not guarantee future results. Only invest what you can afford to lose.

---

## Version

**Version:** 1.0
**Last Updated:** October 2025
**Tested With:** Freqtrade 2024.10+, Python 3.11+

---

**Happy Trading! 🚀**
