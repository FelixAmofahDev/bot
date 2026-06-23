import asyncio
import aiohttp
from datetime import datetime

async def ping_health():
    """Ping the health endpoint every 10 minutes to keep service alive on Render free tier"""
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8000/health', timeout=5) as resp:
                    status = resp.status
                    print(f"[{datetime.now()}] Health check: {status} ✓")
        except Exception as e:
            print(f"[{datetime.now()}] Health check failed: {e}")
        
        # Wait 10 minutes before next check
        await asyncio.sleep(600)

if __name__ == '__main__':
    asyncio.run(ping_health())
