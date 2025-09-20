#!/bin/bash

# Wait for database to be ready
echo "Waiting for database to be ready..."
python -c "
import time
import asyncio
import asyncpg
import os
import sys

async def wait_for_db():
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print('DATABASE_URL not set')
        sys.exit(1)

    # Convert to asyncpg format if needed
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')

    # Parse the URL for asyncpg
    from urllib.parse import urlparse
    parsed = urlparse(database_url.replace('postgresql+asyncpg://', 'postgresql://'))

    for attempt in range(30):
        try:
            conn = await asyncpg.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                user=parsed.username,
                password=parsed.password,
                database=parsed.path[1:] if parsed.path else None
            )
            await conn.close()
            print('Database is ready!')
            break
        except Exception as e:
            print(f'Database not ready (attempt {attempt + 1}/30): {e}')
            if attempt == 29:
                print('Database connection timeout')
                sys.exit(1)
            time.sleep(2)

asyncio.run(wait_for_db())
"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting the application..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT