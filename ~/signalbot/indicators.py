import pandas as pd
import numpy as np


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def evaluate(df: pd.DataFrame, cfg) -> dict:
    close = df["close"]

    r = rsi(close, cfg.RSI_PERIOD).iloc[-1]
    if r < cfg.RSI_OVERSOLD:
        rsi_signal = "CALL"
    elif r > cfg.RSI_OVERBOUGHT:
        rsi_signal = "PUT"
    else:
        rsi_signal = "NEUTRAL"

    macd_line, signal_line, hist = macd(close, cfg.MACD_FAST, cfg.MACD_SLOW, cfg.MACD_SIGNAL)
    macd_now = macd_line.iloc[-1]
    sig_now = signal_line.iloc[-1]
    macd_prev = macd_line.iloc[-2]
    sig_prev = signal_line.iloc[-2]

    if macd_prev < sig_prev and macd_now > sig_now:
        macd_signal = "CALL"
    elif macd_prev > sig_prev and macd_now < sig_now:
        macd_signal = "PUT"
    else:
        macd_signal = "NEUTRAL"

    ema_f = ema(close, cfg.EMA_FAST)
    ema_s = ema(close, cfg.EMA_SLOW)
    ema_signal = "NEUTRAL"
    if ema_f.iloc[-2] < ema_s.iloc[-2] and ema_f.iloc[-1] > ema_s.iloc[-1]:
        ema_signal = "CALL"
    elif ema_f.iloc[-2] > ema_s.iloc[-2] and ema_f.iloc[-1] < ema_s.iloc[-1]:
        ema_signal = "PUT"

    signals = {"RSI": rsi_signal, "MACD": macd_signal, "EMA": ema_signal}

    calls = sum(1 for v in signals.values() if v == "CALL")
    puts = sum(1 for v in signals.values() if v == "PUT")

    if calls >= cfg.MIN_AGREEING_INDICATORS and calls > puts:
        final = "CALL"
    elif puts >= cfg.MIN_AGREEING_INDICATORS and puts > calls:
        final = "PUT"
    else:
        final = "NEUTRAL"

    return {
        "final": final,
        "per_indicator": signals,
        "rsi_value": round(float(r), 2),
        "macd_hist": round(float(hist.iloc[-1]), 6),
        "price": float(close.iloc[-1]),
  }
