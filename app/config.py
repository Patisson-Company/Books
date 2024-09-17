import os
from dotenv import load_dotenv

load_dotenv()

SERVICE_NAME = 'books'
SERVICE_HOST: str = os.getenv("SERVICE_HOST_")  # type: ignore[reportArgumentType]

DATABASE_URL: str = os.getenv("DATABASE_URL")  # type: ignore[reportArgumentType]