from pymongo import MongoClient

# MongoDB Atlas Connection
client = MongoClient(
    "mongodb+srv://levakupradeepkumar:Test%401234@cluster0.oa6xmtw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

# Database
db = client["expense_tracker"]

# Collections
expense_collection = db["expense"]

income_collection = db["income"]

user_collection = db["users"]