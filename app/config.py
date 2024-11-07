import os

from dotenv import load_dotenv
from patisson_request.core import SelfAsyncService, Service

load_dotenv()

SERVICE_NAME = Service.BOOKS.value
SERVICE_HOST: str = os.getenv("SERVICE_HOST_")  # type: ignore[reportArgumentType]

DATABASE_URL: str = os.getenv("DATABASE_URL")  # type: ignore[reportArgumentType]

SelfService = SelfAsyncService(
    self_service=Service(SERVICE_NAME),
    login=os.getenv("LOGIN"),  # type: ignore[reportArgumentType]
    password=os.getenv("PASSWORD"),  # type: ignore[reportArgumentType]
    external_services=[]
)