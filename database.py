# from pymongo import MongoClient

# # MongoDB Atlas Connection
# client = MongoClient(
#     "mongodb+srv://levakupradeepkumar:Test%401234@cluster0.oa6xmtw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# )

# # Database
# db = client["expense_tracker"]

# # Collections
# expense_collection = db["expense"]

# income_collection = db["income"]

# user_collection = db["users"]



from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# from pymongo import MongoClient

# # MongoDB Atlas Connection
# client = MongoClient(
#     "mongodb+srv://levakupradeepkumar:Test%401234@cluster0.oa6xmtw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# )

# # Database
# db = client["expense_tracker"]

# # Collections
# expense_collection = db["expense"]

# income_collection = db["income"]

# user_collection = db["users"]



from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# MongoDB Connection
client = MongoClient(os.getenv("MONGO_URI"))

# Database
db = client["expense_tracker"]

# Collections
expense_collection = db["expense"]
income_collection = db["income"]
user_collection = db["users"]
loan_collection = db["loan"]
repayment_collection = db["repayment"]

# MongoDB Connection
client = MongoClient(os.getenv("MONGO_URI"))

# Database
db = client["expense_tracker"]

# Collections
expense_collection = db["expense"]
income_collection = db["income"]
user_collection = db["users"]