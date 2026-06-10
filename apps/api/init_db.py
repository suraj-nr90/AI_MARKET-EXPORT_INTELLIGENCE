import asyncio
import asyncpg
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

async def main():
    db_url = os.environ.get('NEON_DATABASE_URL')
    print(f"Connecting to NeonDB...")
    try:
        conn = await asyncpg.connect(db_url)
        with open('../../db/001_initial.sql', 'r') as f:
            sql = f.read()
        await conn.execute(sql)
        print("Database tables created successfully!")
        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
