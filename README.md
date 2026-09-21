# signalbot

Technical signal generator for Pocket Broker.

Fires CALL/PUT signals when RSI + MACD + EMA agree. Sends to Telegram. Logs to CSV.

**No auto-trading.** You see the signal, you decide.

## Setup

```bash
git clone <your-repo>
cd signalbot
pip install -r requirements.txt
```

Edit `config.py`:
- `POCKET_SSID` — your SSID cookie (F12 → Application → Cookies → `ssid`)
- `ASSET` — exact asset name, e.g. `EURUSD_otc`
- `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` — optional, for phone alerts

## Run

```bash
python3 signalbot.py
```

Signals print to console and (if configured) go to Telegram.

## Signal rules

- RSI below 30 → CALL bias; above 70 → PUT bias
- MACD line crosses signal line → direction of cross
- EMA 9 crosses EMA 21 → direction of cross
- Fires when **2 of 3** agree

## Log

Every fired signal lands in `signals/signals.csv`.

## Reality check

This is technical analysis automation. **It does not predict the market.**

Binary options on OTC pairs are near-random. Break-even needs >55% win rate (typical 80% payout). Indicator agreement does not guarantee edge — it just filters noise.

Run this on **demo** first. Log 100+ signals. Count how many were correct. If it's not above break-even, it's not a strategy — it's coin-flipping with extra steps.
