import os
import jwt
from functools import wraps
from flask import request
from dotenv import load_dotenv

load_dotenv()

# FIX: match .env key name
# SECRET_KEY = os.getenv("JWT_SECRET")

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")


def token_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if "Authorization" in request.headers:
            bearer = request.headers["Authorization"]

            if bearer.startswith("Bearer "):
                token = bearer.split(" ")[1]

        if not token:
            return {"message": "Token is missing"}, 401

        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=["HS256"]
            )

            request.user_id = payload["user_id"]
            request.user_name = payload["name"]
            request.user_email = payload["email"]

        except jwt.ExpiredSignatureError:
            return {"message": "Token Expired"}, 401

        except jwt.InvalidTokenError:
            return {"message": "Invalid Token"}, 401

        return f(*args, **kwargs)

    return decorated