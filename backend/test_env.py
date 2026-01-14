import os
from dotenv import load_dotenv

print("Before load:", os.getenv("TEST_MESSAGE"))

load_dotenv()

print("After load:", os.getenv("TEST_MESSAGE"))
print("DATABASE_URL:", os.getenv("DATABASE_URL"))