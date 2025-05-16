from dotenv import load_dotenv
import os

load_dotenv()

e = os.getenv

config = {
    "database_name": e("DATABASE_NAME"),
}
