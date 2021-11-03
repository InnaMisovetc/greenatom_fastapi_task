from starlette.config import Config

config = Config(".env_dev")

DATABASE_URL = config("INBOX_DATABASE_URL", cast=str, default="")
TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=str, default="")
TEST_MODE = config("TEST_MODE", cast=bool, default=False)
