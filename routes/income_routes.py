from flask import Blueprint, request
from datetime import datetime
from bson import ObjectId

from database import db
from utils.auth import token_required

income_collection = db["income"]

income_bp = Blueprint("income_bp", __name__)

# =========================
# ADD INCOME
# =========================
@income_bp.route("/addIncome", methods=["POST"])
@token_required
def add_income():

    user_id = request.user_id
    data = request.json

    data["amount"] = float(data["amount"])

    income_date = datetime.strptime(data["date"], "%Y-%m-%d")

    data["month"] = income_date.strftime("%B")
    data["year"] = income_date.year
    data["user_id"] = user_id

    income_collection.insert_one(data)

    return {"message": "Income Added Successfully"}


# =========================
# GET INCOME (USER ONLY)
# =========================
@income_bp.route("/getIncome", methods=["GET"])
@token_required
def get_income():

    user_id = request.user_id

    incomes = income_collection.find({"user_id": user_id})

    return [
        {**i, "_id": str(i["_id"])}
        for i in incomes
    ]


# =========================
# DELETE INCOME
# =========================
@income_bp.route("/deleteIncome/<id>", methods=["DELETE"])
@token_required
def delete_income(id):

    user_id = request.user_id

    result = income_collection.delete_one({
        "_id": ObjectId(id),
        "user_id": user_id
    })

    if result.deleted_count > 0:
        return {"message": "Income Deleted Successfully"}

    return {"message": "Income Not Found"}, 404


# =========================
# UPDATE INCOME
# =========================
@income_bp.route("/updateIncome/<id>", methods=["PUT"])
@token_required
def update_income(id):

    user_id = request.user_id
    data = request.json

    if "amount" in data:
        data["amount"] = float(data["amount"])

    if "date" in data:
        d = datetime.strptime(data["date"], "%Y-%m-%d")
        data["month"] = d.strftime("%B")
        data["year"] = d.year

    result = income_collection.update_one(
        {"_id": ObjectId(id), "user_id": user_id},
        {"$set": data}
    )

    if result.modified_count > 0:
        return {"message": "Income Updated Successfully"}

    return {"message": "No Changes Made"}, 404


# =========================
# MONTHLY INCOME
# =========================
@income_bp.route("/income/<month>/<int:year>", methods=["GET"])
@token_required
def monthly_income(month, year):

    user_id = request.user_id

    incomes = income_collection.find({
        "user_id": user_id,
        "month": month,
        "year": year
    })

    return [
        {**i, "_id": str(i["_id"])}
        for i in incomes
    ]


# =========================
# MONTHLY BALANCE
# =========================
@income_bp.route("/monthlyBalance/<month>/<int:year>", methods=["GET"])
@token_required
def monthly_balance(month, year):

    user_id = request.user_id

    income_data = list(income_collection.aggregate([
        {"$match": {
            "user_id": user_id,
            "month": month,
            "year": year
        }},
        {"$group": {"_id": None, "income": {"$sum": "$amount"}}}
    ]))

    income = income_data[0]["income"] if income_data else 0

    expense_data = list(db["expense"].aggregate([
        {"$match": {
            "user_id": user_id,
            "month": month,
            "year": year
        }},
        {"$group": {"_id": None, "expense": {"$sum": "$amount"}}}
    ]))

    expense = expense_data[0]["expense"] if expense_data else 0

    return {
        "income": income,
        "expense": expense,
        "remaining": income - expense,
        "transactions": []
    }


# =========================
# OVERALL BALANCE (USER FIXED)
# =========================
@income_bp.route("/overallBalance", methods=["GET"])
@token_required
def overall_balance():

    user_id = request.user_id

    income_data = list(income_collection.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": None, "income": {"$sum": "$amount"}}}
    ]))

    expense_data = list(db["expense"].aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": None, "expense": {"$sum": "$amount"}}}
    ]))

    income = income_data[0]["income"] if income_data else 0
    expense = expense_data[0]["expense"] if expense_data else 0

    return {
        "income": income,
        "expense": expense,
        "remaining": income - expense
    }