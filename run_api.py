#!/usr/bin/env python
"""Start the FastAPI admin dashboard server."""
import uvicorn
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "twi_bot"))

if __name__ == "__main__":
    uvicorn.run(
        "twi_bot.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
