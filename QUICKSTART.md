# 🚀 AutoCbot Quick Start Guide

Get your AI-powered crypto trading system running in 5 minutes!

## ⚡ Fastest Way to Start (Docker)

### 1. Prerequisites
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- That's it! 🎉

### 2. Clone and Configure
```bash
cd AutoCbot
cp .env.example .env
```

### 3. Start the System
```bash
docker-compose up -d
```

### 4. Access the Application
- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs

---

## 📱 What You'll See

### Dashboard Features
1. **Market Overview** - Global crypto market stats
2. **Fear & Greed Meter** - Sentiment indicator (0-100)
3. **Portfolio Summary** - Your trading portfolio
4. **Live Prices** - Real-time crypto prices
5. **Trading Signals** - AI-powered buy/sell signals
6. **Open Positions** - Active trades

---

## 🎮 First Steps

### 1. Explore the Dashboard
- Everything works in **paper trading mode** by default (safe!)
- No API keys needed to start
- Uses free data sources (CoinGecko, Alternative.me)

### 2. Check Market Data
- View live prices for BTC, ETH, SOL, and more
- See 24h price changes
- Monitor market trends

### 3. Review Trading Signals
- AI analyzes technical + sentiment data
- See confidence scores (0-100%)
- Entry/exit prices included

### 4. Monitor Portfolio (Demo)
- $10,000 demo balance
- Track P&L in real-time
- View open positions

---

## 🔑 Adding API Keys (Optional)

### Free Tier (No Cost)
Everything works without API keys! Using:
- ✅ CoinGecko Free API
- ✅ Alternative.me Fear & Greed Index
- ✅ Messari Free Tier

### Exchange Integration (For Live Trading)
To enable real trading, add Binance API keys to `.env`:

```bash
# Edit .env
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET=your_secret_here
```

**⚠️ CRITICAL**: Create API keys with:
- ✅ Enable: Spot Trading, Reading
- ❌ Disable: Withdrawals (NEVER enable!)

---

## 🎨 Customization

### Change Trading Pairs
Edit `.env`:
```bash
DEFAULT_PAIRS=BTC/USDT,ETH/USDT,SOL/USDT,AVAX/USDT
```

### Adjust Risk Parameters
```bash
MAX_OPEN_TRADES=5
DEFAULT_STOPLOSS=-0.05  # 5% stop loss
DEFAULT_TAKEPROFIT=0.03  # 3% take profit
```

### Update Intervals
```bash
PRICE_UPDATE_INTERVAL=5      # Update prices every 5 seconds
SENTIMENT_UPDATE_INTERVAL=300  # Update sentiment every 5 minutes
```

---

## 📊 Understanding the UI

### Market Overview Card
- **Total Market Cap**: Entire crypto market value
- **BTC Dominance**: Bitcoin's market share %
- **24h Volume**: Total trading volume

### Fear & Greed Meter
- **0-24**: Extreme Fear (potential buying opportunity)
- **25-49**: Fear
- **50**: Neutral
- **51-75**: Greed
- **76-100**: Extreme Greed (potential selling opportunity)

### Trading Signals
- **Signal**: Buy, Sell, or Hold
- **Confidence**: AI confidence (higher is better)
- **Entry Price**: Suggested entry point
- **Take Profit**: Target sell price
- **Stop Loss**: Risk management level

---

## 🔧 Troubleshooting

### Backend not starting?
```bash
# Check logs
docker-compose logs backend

# Restart
docker-compose restart backend
```

### Frontend not loading?
```bash
# Check logs
docker-compose logs frontend

# Restart
docker-compose restart frontend
```

### Can't connect to API?
- Make sure backend is running: http://localhost:8000/health
- Check CORS settings in `.env`
- Verify Docker containers are up: `docker-compose ps`

### No data showing?
- Wait 30 seconds for initial data load
- Check browser console for errors (F12)
- Verify internet connection (needs to fetch from APIs)

---

## 🚦 Next Steps

### 1. Learn More
- Read `COMPLETE_SYSTEM_README.md` for full documentation
- Explore API docs at http://localhost:8000/docs
- Check out the original Freqtrade strategies in `user_data/strategies/`

### 2. Customize Strategies
- Edit strategy files in `user_data/strategies/`
- Run backtests via API
- Optimize parameters

### 3. Enable Live Trading (When Ready)
1. Complete paper trading for 2+ weeks
2. Add exchange API keys
3. Set `DRY_RUN=false` in `.env`
4. Start with small amounts ($100-200)
5. Monitor closely!

### 4. Advanced Features
- Train ML models (see `user_data/notebooks/`)
- Add custom indicators
- Integrate additional data sources
- Set up Telegram notifications

---

## ⚠️ Important Reminders

### Before Going Live
- ✅ Test in paper mode for 2+ weeks
- ✅ Understand all signals and indicators
- ✅ Set up proper risk management
- ✅ API keys have NO withdrawal permissions
- ✅ Start with small amounts only

### Safety Rules
- 🛑 Never enable withdrawals on API keys
- 🛑 Don't invest more than you can afford to lose
- 🛑 Always use stop-losses
- 🛑 Don't chase losses
- 🛑 Monitor your bot daily

---

## 📞 Getting Help

### Resources
- **API Documentation**: http://localhost:8000/docs
- **Freqtrade Docs**: https://www.freqtrade.io/
- **Discord**: https://discord.gg/p7nuUNVfP7
- **r/algotrading**: https://reddit.com/r/algotrading

### Common Questions

**Q: Is this free?**
A: Yes! The complete system works with free tier APIs. Paid services are optional.

**Q: Can I lose money?**
A: In paper mode, no. With live trading, yes. Only trade what you can afford to lose.

**Q: Do I need coding skills?**
A: No for basic use. Yes for custom strategies and advanced features.

**Q: What exchanges are supported?**
A: Binance is preconfigured. Freqtrade supports 100+ exchanges via CCXT.

**Q: Can I run this 24/7?**
A: Yes! That's the point. Use Docker or deploy to a VPS for continuous operation.

---

## 🎯 Success Checklist

- [ ] Docker running
- [ ] Containers started (`docker-compose up -d`)
- [ ] Frontend accessible (localhost:3000)
- [ ] Backend accessible (localhost:8000)
- [ ] Dashboard showing data
- [ ] Trading signals appearing
- [ ] Paper trading active

**All checked? You're ready! 🚀**

---

## 🌟 What Makes This Special?

### The Ultimate Stack
✅ **Multi-layer analysis**: Technical + Fundamental + Sentiment
✅ **AI-powered**: Machine learning signals
✅ **Real-time**: WebSocket updates
✅ **Modern UI**: Next.js + Tailwind + Framer Motion
✅ **Production-ready**: Docker, FastAPI, TypeScript
✅ **Free tier**: No API keys needed to start
✅ **Comprehensive**: Complete trading system

### World-Class Design
- Beautiful animations
- Responsive layout
- Dark mode optimized
- Intuitive navigation
- Real-time updates

---

**Happy Trading! 🎉**

Remember: Start small, test thoroughly, and never invest more than you can afford to lose.
