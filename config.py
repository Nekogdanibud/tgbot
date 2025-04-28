import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    MARZBAN_URL = os.getenv("MARZBAN_URL")
    MARZBAN_USERNAME = os.getenv("MARZBAN_USERNAME")
    MARZBAN_PASSWORD = os.getenv("MARZBAN_PASSWORD")
    ADMIN_ID = os.getenv("ADMIN_ID")

    @classmethod
    def validate(cls):
        required = ["BOT_TOKEN", "MARZBAN_URL", "MARZBAN_USERNAME", "MARZBAN_PASSWORD", "ADMIN_ID"]
        missing = [var for var in required if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# Validate config on import
Config.validate()
