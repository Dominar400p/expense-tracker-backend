from flask import Flask
from flask_cors import CORS

from routes.expense_routes import expense_bp
from routes.income_routes import income_bp
from routes.auth_routes import auth_bp

app = Flask(__name__)

# Enable CORS
CORS(
    app,
    origins=[
        "http://localhost:5173",
        "https://expense-tracker-frontend-bc5t.onrender.com",
    ],
    supports_credentials=True,
)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(expense_bp)
app.register_blueprint(income_bp)

@app.route("/")
def home():
    return {
        "message": "Expense Tracker API is Running"
    }

if __name__ == "__main__":
    app.run(debug=True)