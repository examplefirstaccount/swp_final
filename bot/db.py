from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from .settings import Settings
from .state import ChatState, UserPM


async def main(settings: Settings):
    host = settings.mongo_host
    port = settings.mongo_port
    username = settings.mongo_username
    password = settings.mongo_password

    client: AsyncIOMotorClient = AsyncIOMotorClient(
        f"mongodb://{username}:{password}@{host}:{port}", tz_aware=True
    )

    db = client["bot_states"]

    await init_beanie(database=db, document_models=[ChatState, UserPM])
