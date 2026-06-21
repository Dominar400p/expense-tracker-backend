from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://levakupradeepkumar:January%4025p@cluster0.oa6xmtw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

try:
    client.admin.command("ping")
    print("✅ Connected Successfully")
except Exception as e:
    print("❌ Error:")
    print(e)