 'PYEOF'
"""
Pocket Broker WebSocket client.
Pulls live candles via BinaryOptionsToolsV2.
"""

import asyncio
import pandas as pd
from BinaryOptionsToolsV2.pocketoption import PocketOptionAsync


class PocketClient:
    def __init__(self, ssid: str):
        self.ssid = ssid
        self.api = None

    async def connect(self):
        self.api = PocketOptionAsync(self.ssid)
        await self.api.wait_for_assets()
        return self.api

    async def get_candles(self, asset: str, timeframe: int, count: int) -> pd.DataFrame:
        """
        Returns DataFrame with columns: time, open, high, low, close
        """
        raw = await self.api.get_candles(asset, timeframe, count)

        rows = []
        for c in raw:
            rows.append({
                "time": c.get("time") or c.get("timestamp"),
                "open": float(c["open"]),
                "high": float(c["high"]),
                "low": float(c["low"]),
                "close": float(c["close"]),
            })

        df = pd.DataFrame(rows).sort_values("time").reset_index(drop=True)
        return df

    async def close(self):
        if self.api:
            try:
                await self.api.close()
            except Exception:
                pass
PYEOF
