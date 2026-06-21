from flask import Blueprint, request
from bson import ObjectId
from datetime import datetime
from database import expense_collection
from utils.auth import token_required

expense_bp = Blueprint("expense_bp", __name__)

# =========================
# ADD EXPENSE
# =========================
@expense_bp.route("/addExpense", methods=["POST"])
@token_required
def add_expense():

    user_id = request.user_id
    data = request.json

    data["amount"] = float(data["amount"])

    expense_date = datetime.strptime(data["date"], "%Y-%m-%d")

    data["month"] = expense_date.strftime("%B")
    data["year"] = expense_date.year

    data["user_id"] = user_id

    expense_collection.insert_one(data)

    return {"message": "Expense Added Successfully"}


# =========================
# GET ALL EXPENSES
# =========================
@expense_bp.route("/getExpenses", methods=["GET"])
@token_required
def get_expenses():

    user_id = request.user_id

    expenses = expense_collection.find({"user_id": user_id})

    return [
        {**e, "_id": str(e["_id"])}
        for e in expenses
    ]


# =========================
# GET SINGLE EXPENSE
# =========================
@expense_bp.route("/getSingleExpense/<id>", methods=["GET"])
@token_required
def get_single_expense(id):

    user_id = request.user_id

    expense = expense_collection.find_one({
        "_id": ObjectId(id),
        "user_id": user_id
    })

    if not expense:
        return {"message": "Expense Not Found"}, 404

    expense["_id"] = str(expense["_id"])
    return expense


# =========================
# UPDATE EXPENSE
# =========================
@expense_bp.route("/updateExpense/<id>", methods=["PUT"])
@token_required
def update_expense(id):

    user_id = request.user_id
    data = request.json

    if "amount" in data:
        data["amount"] = float(data["amount"])

    if "date" in data:
        d = datetime.strptime(data["date"], "%Y-%m-%d")
        data["month"] = d.strftime("%B")
        data["year"] = d.year

    result = expense_collection.update_one(
        {"_id": ObjectId(id), "user_id": user_id},
        {"$set": data}
    )

    if result.modified_count > 0:
        return {"message": "Expense Updated Successfully"}

    return {"message": "No Changes Made"}, 404


# =========================
# DELETE EXPENSE
# =========================
@expense_bp.route("/deleteExpense/<id>", methods=["DELETE"])
@token_required
def delete_expense(id):

    user_id = request.user_id

    result = expense_collection.delete_one({
        "_id": ObjectId(id),
        "user_id": user_id
    })

    if result.deleted_count > 0:
        return {"message": "Expense Deleted"}

    return {"message": "Expense Not Found"}, 404


# =========================
# MONTHLY SUMMARY
# =========================
@expense_bp.route("/monthlySummary", methods=["GET"])
@token_required
def monthly_summary():

    user_id = request.user_id

    data = list(expense_collection.aggregate([
        {"$match": {"user_id": user_id}},
        {
            "$group": {
                "_id": {"month": "$month", "year": "$year"},
                "total": {"$sum": "$amount"}
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]))

    return [
        {
            "month": d["_id"]["month"],
            "year": d["_id"]["year"],
            "total": d["total"]
        }
        for d in data
    ]


# =========================
# CATEGORY SUMMARY
# =========================
@expense_bp.route("/categorySummary/<month>/<int:year>", methods=["GET"])
@token_required
def category_summary(month, year):

    user_id = request.user_id

    data = list(expense_collection.aggregate([
        {"$match": {
            "user_id": user_id,
            "month": month,
            "year": year
        }},
        {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
        {"$sort": {"total": -1}}
    ]))

    return [
        {"category": d["_id"], "total": d["total"]}
        for d in data
    ]


# =========================
# MONTHLY EXPENSE DRILL DOWN
# =========================
@expense_bp.route("/expenses/<month>/<int:year>", methods=["GET"])
@token_required
def get_monthly_expenses(month, year):

    user_id = request.user_id

    expenses = expense_collection.find({
        "user_id": user_id,
        "month": month,
        "year": year
    })

    transactions = [
        {**e, "_id": str(e["_id"])}
        for e in expenses
    ]

    return {
        "month": month,
        "year": year,
        "transactions": transactions,
        "totalExpense": sum(t["amount"] for t in transactions)
    }


# =========================
# DASHBOARD
# =========================
@expense_bp.route("/dashboard", methods=["GET"])
@token_required
def dashboard():

    user_id = request.user_id

    total_expense = expense_collection.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ])

    total_expense = list(total_expense)
    total_expense = total_expense[0]["total"] if total_expense else 0

    transactions = expense_collection.count_documents({"user_id": user_id})

    current = datetime.now()
    month = current.strftime("%B")
    year = current.year

    this_month = expense_collection.aggregate([
        {"$match": {
            "user_id": user_id,
            "month": month,
            "year": year
        }},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ])

    this_month = list(this_month)
    this_month_expense = this_month[0]["total"] if this_month else 0

    highest = list(expense_collection.aggregate([
        {"$match": {"user_id": user_id}},
        {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
        {"$sort": {"total": -1}},
        {"$limit": 1}
    ]))

    return {
        "totalExpenses": total_expense,
        "totalTransactions": transactions,
        "thisMonthExpense": this_month_expense,
        "highestCategory": highest[0]["_id"] if highest else "-"
    }