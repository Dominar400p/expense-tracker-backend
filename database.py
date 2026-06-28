from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# MongoDB Connection
client = MongoClient(os.getenv("MONGO_URI"))

# Database
db = client["expense_tracker"]

# Existing Collections
expense_collection = db["expense"]
income_collection = db["income"]
user_collection = db["users"]

# Ledger Collections
borrower_collection = db["borrower"]
ledger_collection = db["ledger"]