# Pocket Broker connection
POCKET_SSID = ""  # your SSID cookie from the browser session

# Asset pair (exact name from Pocket Broker asset list)
ASSET = "EURUSD_otc"
TIMEFRAME = 60          # seconds (1M candles)
CANDLE_COUNT = 200      # rolling window size

# Indicator settings
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

EMA_FAST = 9
EMA_SLOW = 21

# Signal rules
MIN_AGREEING_INDICATORS = 2   # need at least 2 of 3 to fire

# Telegram
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""

# Logging
LOG_SIGNALS = True
SIGNAL_LOG = "signals/signals.csv"
