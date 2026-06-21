from flask import Blueprint, request
from database import user_collection

import bcrypt
import jwt
import datetime

from utils.auth import SECRET_KEY

auth_bp = Blueprint("auth_bp", __name__)


# =====================================================================
# Register
# =====================================================================

@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.json

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return {
            "message": "All fields are required"
        }, 400

    existing = user_collection.find_one({
        "email": email
    })

    if existing:
        return {
            "message": "Email already exists"
        }, 400

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    user_collection.insert_one({
        "name": name,
        "email": email,
        "password": hashed_password
    })

    return {
        "message": "Registration Successful"
    }, 201

# ==================================================================================================================

# =====================================================================
# Login
# =====================================================================

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.json

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return {
            "message": "Email and Password are required"
        }, 400

    user = user_collection.find_one({
        "email": email
    })

    if not user:
        return {
            "message": "Invalid Email or Password"
        }, 401

    if not bcrypt.checkpw(
        password.encode("utf-8"),
        user["password"]
    ):
        return {
            "message": "Invalid Email or Password"
        }, 401

    token = jwt.encode(
        {
            "user_id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    return {
        "message": "Login Successful",
        "token": token,
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"]
        }
    }, 200