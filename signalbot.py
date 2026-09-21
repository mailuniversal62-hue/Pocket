#!/usr/bin/env python3
"""
signalbot — Pocket Broker technical signal generator
Fires RSI/MACD/EMA signals to Telegram.
No auto-trading. You see the signal, you decide.
"""

import os
import csv
import sys
import json
import asyncio
import datetime
import requests
from colorama import Fore, Style, init

import config
from indicators import evaluate
from pocket_client import PocketClient

init(autoreset=True)

SIGNAL_DIR = "signals"
os.makedirs(SIGNAL_DIR, exist_ok=True)

# Track last fired signal to avoid spamming
last_signal = {"direction": None, "time": None}


def send_telegram(text: str):
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": config.TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "Markdown",
            },
            timeout=5,
        )
    except Exception as e:
        print(f"{Fore.RED}[!] Telegram send failed: {e}{Style.RESET_ALL}")


def log_signal(record: dict):
    if not config.LOG_SIGNALS:
        return
    path = config.SIGNAL_LOG
    new = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=record.keys())
        if new:
            w.writeheader()
        w.writerow(record)


def format_signal(sig: dict, asset: str) -> str:
    d = sig["final"]
    arrow = "🟢" if d == "CALL" else "🔴" if d == "PUT" else "⚪"
    lines = [
        f"{arrow} *{d}* — `{asset}`",
        f"Price: `{sig['price']}`",
        f"RSI: `{sig['rsi_value']}`",
        f"MACD hist: `{sig['macd_hist']}`",
        f"Indicators: RSI={sig['per_indicator']['RSI']} "
        f"MACD={sig['per_indicator']['MACD']} "
        f"EMA={sig['per_indicator']['EMA']}",
        f"Time: `{datetime.datetime.utcnow().strftime('%H:%M:%S')} UTC`",
    ]
    return "\n".join(lines)


async def run():
    print(f"{Fore.CYAN}signalbot{Style.RESET_ALL} — Pocket Broker signal generator")
    print(f"Asset     : {config.ASSET}")
    print(f"Timeframe : {config.TIMEFRAME}s")
    print(f"Rule      : {config.MIN_AGREEING_INDICATORS}/3 indicators must agree")
    print(f"{Fore.YELLOW}[*] No auto-trading. Signals only.{Style.RESET_ALL}\n")

    client = PocketClient(config.POCKET_SSID)
    await client.connect()
    print(f"{Fore.GREEN}[+] Connected. Streaming candles...{Style.RESET_ALL}\n")

    try:
        while True:
            df = await client.get_candles(config.ASSET, config.TIMEFRAME, config.CANDLE_COUNT)
            if df.empty or len(df) < config.CANDLE_COUNT // 2:
                await asyncio.sleep(config.TIMEFRAME)
                continue

            sig = evaluate(df, config)
            now = datetime.datetime.utcnow()

            # Fire only on change or every 3 candles
            fire = (
                sig["final"] != "NEUTRAL"
                and (
                    last_signal["direction"] != sig["final"]
                    or last_signal["time"] is None
                    or (now - last_signal["time"]).total_seconds() > config.TIMEFRAME * 3
                )
            )

            if fire:
                msg = format_signal(sig, config.ASSET)
                print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}\n")
                send_telegram(msg)
                log_signal({
                    "time": now.isoformat(),
                    "asset": config.ASSET,
                    "direction": sig["final"],
                    "price": sig["price"],
                    "rsi": sig["rsi_value"],
                    "macd_hist": sig["macd_hist"],
                    "rsi_sig": sig["per_indicator"]["RSI"],
                    "macd_sig": sig["per_indicator"]["MACD"],
                    "ema_sig": sig["per_indicator"]["EMA"],
                })
                last_signal["direction"] = sig["final"]
                last_signal["time"] = now

            await asyncio.sleep(config.TIMEFRAME)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[*] Stopping.{Style.RESET_ALL}")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(run())
