import os
import asyncpg
import logging
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
logger = logging.getLogger("db")

NEON_DATABASE_URL = os.getenv("NEON_DATABASE_URL")

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if not NEON_DATABASE_URL:
            logger.error("NEON_DATABASE_URL is not set. Database will not be connected.")
            return
        try:
            self.pool = await asyncpg.create_pool(dsn=NEON_DATABASE_URL, min_size=1, max_size=10)
            logger.info("Successfully connected to NeonDB pool.")
        except Exception as e:
            logger.error(f"Failed to connect to NeonDB: {e}")

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            logger.info("Disconnected from NeonDB pool.")

db = Database()
