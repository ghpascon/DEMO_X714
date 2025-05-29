from app.schemas.X714 import reader

async def connect_serial():
    await reader.connect()

