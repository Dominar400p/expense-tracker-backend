from flask import Blueprint, request
from datetime import datetime

from utils.auth import token_required
from bson import ObjectId

from database import loan_collection, repayment_collection

loan_bp = Blueprint("loan_bp", __name__)


# =========================
# ADD LOAN
# =========================
@loan_bp.route("/addLoan", methods=["POST"])
@token_required
def add_loan():

    user_id = request.user_id
    data = request.json

    data["loanAmount"] = float(data["loanAmount"])
    data["user_id"] = user_id
    data["status"] = "Pending"

    loan_date = datetime.strptime(data["loanDate"], "%Y-%m-%d")

    data["month"] = loan_date.strftime("%B")
    data["year"] = loan_date.year

    loan_collection.insert_one(data)

    return {
        "message": "Loan Added Successfully"
    }


# =========================
# GET ALL LOANS
# =========================
@loan_bp.route("/getLoans", methods=["GET"])
@token_required
def get_loans():

    user_id = request.user_id

    loans = loan_collection.find({
        "user_id": user_id
    })

    return [
        {**loan, "_id": str(loan["_id"])}
        for loan in loans
    ]


# =========================
# ADD REPAYMENT
# =========================
@loan_bp.route("/addRepayment/<loan_id>", methods=["POST"])
@token_required
def add_repayment(loan_id):

    user_id = request.user_id
    data = request.json

    loan = loan_collection.find_one({
        "_id": ObjectId(loan_id),
        "user_id": user_id
    })

    if not loan:
        return {
            "message": "Loan Not Found"
        }, 404

    amount = float(data["amount"])

    if amount <= 0:
        return {
            "message": "Repayment amount must be greater than 0"
        }, 400

    loan_date = datetime.strptime(
        loan["loanDate"],
        "%Y-%m-%d"
    )

    repayment_date = datetime.strptime(
        data["date"],
        "%Y-%m-%d"
    )

    if repayment_date < loan_date:
        return {
            "message": "Repayment date cannot be before loan date."
        }, 400

    repayment = {
        "loan_id": loan_id,
        "user_id": user_id,
        "amount": amount,
        "date": data["date"]
    }

    repayment_collection.insert_one(repayment)

    return {
        "message": "Repayment Added Successfully"
    }


# =========================
# GET SINGLE LOAN DETAILS
# =========================
@loan_bp.route("/loanDetails/<loan_id>", methods=["GET"])
@token_required
def loan_details(loan_id):

    user_id = request.user_id

    loan = loan_collection.find_one({
        "_id": ObjectId(loan_id),
        "user_id": user_id
    })

    if not loan:
        return {"message": "Loan Not Found"}, 404

    repayments = list(
        repayment_collection.find({
            "loan_id": loan_id,
            "user_id": user_id
        })
    )

    total_repaid = sum(r["amount"] for r in repayments)

    remaining = loan["loanAmount"] - total_repaid

    status = "Completed" if remaining <= 0 else "Pending"

    loan_collection.update_one(
        {"_id": ObjectId(loan_id)},
        {
            "$set": {
                "status": status
            }
        }
    )

    return {
        "_id": str(loan["_id"]),
        "personName": loan["personName"],
        "mobile": loan.get("mobile", ""),
        "loanAmount": loan["loanAmount"],
        "loanDate": loan["loanDate"],
        "status": status,
        "totalRepaid": total_repaid,
        "remaining": remaining,
        "repayments": [
            {
                "_id": str(r["_id"]),
                "amount": r["amount"],
                "date": r["date"]
            }
            for r in repayments
        ]
    }


# =========================
# LOAN DASHBOARD
# =========================
@loan_bp.route("/loanDashboard", methods=["GET"])
@token_required
def loan_dashboard():

    user_id = request.user_id

    loans = list(
        loan_collection.find({
            "user_id": user_id
        })
    )

    total_given = 0
    total_repaid = 0
    pending = 0
    completed = 0

    for loan in loans:

        total_given += loan["loanAmount"]

        repayments = list(
            repayment_collection.find({
                "loan_id": str(loan["_id"]),
                "user_id": user_id
            })
        )

        repaid = sum(r["amount"] for r in repayments)

        total_repaid += repaid

        if repaid >= loan["loanAmount"]:
            completed += 1
        else:
            pending += 1

    return {
        "totalGiven": total_given,
        "totalRepaid": total_repaid,
        "remaining": total_given - total_repaid,
        "pendingLoans": pending,
        "completedLoans": completed,
        "totalPersons": len(loans)
    }


# =========================
# DELETE REPAYMENT
# =========================
@loan_bp.route("/deleteRepayment/<repayment_id>", methods=["DELETE"])
@token_required
def delete_repayment(repayment_id):

    user_id = request.user_id

    result = repayment_collection.delete_one({
        "_id": ObjectId(repayment_id),
        "user_id": user_id
    })

    if result.deleted_count > 0:
        return {
            "message": "Repayment Deleted Successfully"
        }

    return {
        "message": "Repayment Not Found"
    }, 404


# =========================
# UPDATE LOAN
# =========================
@loan_bp.route("/updateLoan/<loan_id>", methods=["PUT"])
@token_required
def update_loan(loan_id):

    user_id = request.user_id
    data = request.json

    if "loanAmount" in data:
        data["loanAmount"] = float(data["loanAmount"])

    if "loanDate" in data:

        d = datetime.strptime(data["loanDate"], "%Y-%m-%d")

        data["month"] = d.strftime("%B")
        data["year"] = d.year

    result = loan_collection.update_one(
        {
            "_id": ObjectId(loan_id),
            "user_id": user_id
        },
        {
            "$set": data
        }
    )

    if result.modified_count > 0:
        return {
            "message": "Loan Updated Successfully"
        }

    return {
        "message": "No Changes Made"
    }, 404


# =========================
# DELETE LOAN
# =========================
@loan_bp.route("/deleteLoan/<loan_id>", methods=["DELETE"])
@token_required
def delete_loan(loan_id):

    user_id = request.user_id

    loan = loan_collection.find_one({
        "_id": ObjectId(loan_id),
        "user_id": user_id
    })

    if not loan:
        return {
            "message": "Loan Not Found"
        }, 404

    repayment_collection.delete_many({
        "loan_id": loan_id,
        "user_id": user_id
    })

    loan_collection.delete_one({
        "_id": ObjectId(loan_id),
        "user_id": user_id
    })

    return {
        "message": "Loan Deleted Successfully"
    }