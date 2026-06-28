from flask import Blueprint, request
from bson import ObjectId
from datetime import datetime

from database import borrower_collection, ledger_collection
from utils.auth import token_required

ledger_bp = Blueprint("ledger_bp", __name__)


# =========================
# ADD BORROWER
# =========================
@ledger_bp.route("/addBorrower", methods=["POST"])
@token_required
def add_borrower():

    user_id = request.user_id
    data = request.json

    person_name = data.get("personName", "").strip()
    mobile = data.get("mobile", "").strip()

    if not person_name:
        return {"message": "Person name is required"}, 400

    borrower = {
        "personName": person_name,
        "mobile": mobile,
        "user_id": user_id
    }

    borrower_collection.insert_one(borrower)

    return {
        "message": "Borrower Added Successfully"
    }


# =========================
# GET ALL BORROWERS
# =========================
@ledger_bp.route("/getBorrowers", methods=["GET"])
@token_required
def get_borrowers():

    user_id = request.user_id

    borrowers = list(
        borrower_collection.find({
            "user_id": user_id
        })
    )

    result = []

    for borrower in borrowers:

        borrower_id = str(borrower["_id"])

        entries = list(
            ledger_collection.find({
                "borrower_id": borrower_id,
                "user_id": user_id
            })
        )

        total_given = sum(
            entry["amount"]
            for entry in entries
            if entry["type"] == "GIVEN"
        )

        total_received = sum(
            entry["amount"]
            for entry in entries
            if entry["type"] == "RECEIVED"
        )

        balance = total_given - total_received

        result.append({
            "_id": borrower_id,
            "personName": borrower["personName"],
            "mobile": borrower.get("mobile", ""),
            "totalGiven": total_given,
            "totalReceived": total_received,
            "balance": balance,
            "status": "Completed" if balance <= 0 else "Pending"
        })

    return result


# =========================
# ADD LEDGER ENTRY
# =========================
@ledger_bp.route("/addLedgerEntry/<borrower_id>", methods=["POST"])
@token_required
def add_ledger_entry(borrower_id):

    user_id = request.user_id
    data = request.json

    borrower = borrower_collection.find_one({
        "_id": ObjectId(borrower_id),
        "user_id": user_id
    })

    if not borrower:
        return {"message": "Borrower Not Found"}, 404

    entry_type = data.get("type", "").upper()
    amount = float(data.get("amount", 0))
    date = data.get("date", "")
    description = data.get("description", "").strip()

    if entry_type not in ["GIVEN", "RECEIVED"]:
        return {"message": "Type must be GIVEN or RECEIVED"}, 400

    if amount <= 0:
        return {"message": "Amount must be greater than 0"}, 400

    if not date:
        return {"message": "Date is required"}, 400

    datetime.strptime(date, "%Y-%m-%d")

    

    if not description:
        description = (
            "Loan Given"
            if entry_type == "GIVEN"
            else "Repayment Received"
        )

    ledger_collection.insert_one({
        "borrower_id": borrower_id,
        "user_id": user_id,
        "type": entry_type,
        "amount": amount,
        "date": date,
        "description": description
    })

    return {
        "message": "Ledger Entry Added Successfully"
    }


# =========================
# LEDGER DETAILS
# =========================
@ledger_bp.route("/ledgerDetails/<borrower_id>", methods=["GET"])
@token_required
def ledger_details(borrower_id):

    user_id = request.user_id

    borrower = borrower_collection.find_one({
        "_id": ObjectId(borrower_id),
        "user_id": user_id
    })

    if not borrower:
        return {"message": "Borrower Not Found"}, 404

    entries = list(
        ledger_collection.find({
            "borrower_id": borrower_id,
            "user_id": user_id
        }).sort("date", 1)
    )

    running_balance = 0
    total_given = 0
    total_received = 0
    ledger_entries = []

    for entry in entries:

        if entry["type"] == "GIVEN":
            given = entry["amount"]
            received = 0
            running_balance += given
            total_given += given
        else:
            given = 0
            received = entry["amount"]
            running_balance -= received
            total_received += received

        ledger_entries.append({
            "_id": str(entry["_id"]),
            "date": entry["date"],
            "description": entry["description"],
            "type": entry["type"],
            "given": given,
            "received": received,
            "balance": running_balance
        })

    return {
        "_id": str(borrower["_id"]),
        "personName": borrower["personName"],
        "mobile": borrower.get("mobile", ""),
        "totalGiven": total_given,
        "totalReceived": total_received,
        "balance": total_given - total_received,
        "status": "Completed" if total_given - total_received <= 0 else "Pending",
        "entries": ledger_entries
    }


# =========================
# DELETE LEDGER ENTRY
# =========================
@ledger_bp.route("/deleteLedgerEntry/<entry_id>", methods=["DELETE"])
@token_required
def delete_ledger_entry(entry_id):

    user_id = request.user_id

    result = ledger_collection.delete_one({
        "_id": ObjectId(entry_id),
        "user_id": user_id
    })

    if result.deleted_count > 0:
        return {
            "message": "Ledger Entry Deleted Successfully"
        }

    return {
        "message": "Ledger Entry Not Found"
    }, 404


# =========================
# DELETE BORROWER
# =========================
@ledger_bp.route("/deleteBorrower/<borrower_id>", methods=["DELETE"])
@token_required
def delete_borrower(borrower_id):

    user_id = request.user_id

    borrower = borrower_collection.find_one({
        "_id": ObjectId(borrower_id),
        "user_id": user_id
    })

    if not borrower:
        return {"message": "Borrower Not Found"}, 404

    ledger_collection.delete_many({
        "borrower_id": borrower_id,
        "user_id": user_id
    })

    borrower_collection.delete_one({
        "_id": ObjectId(borrower_id),
        "user_id": user_id
    })

    return {
        "message": "Borrower Deleted Successfully"
    }

# =========================
# UPDATE LEDGER ENTRY
# =========================
@ledger_bp.route("/updateLedgerEntry/<entry_id>", methods=["PUT"])
@token_required
def update_ledger_entry(entry_id):

    user_id = request.user_id
    data = request.json

    entry_type = data.get("type", "").upper()
    amount = float(data.get("amount", 0))
    date = data.get("date", "")
    description = data.get("description", "").strip()

    if entry_type not in ["GIVEN", "RECEIVED"]:
        return {"message": "Type must be GIVEN or RECEIVED"}, 400

    if amount <= 0:
        return {"message": "Amount must be greater than 0"}, 400

    if not date:
        return {"message": "Date is required"}, 400

    datetime.strptime(date, "%Y-%m-%d")

    if not description:
        description = (
            "Loan Given"
            if entry_type == "GIVEN"
            else "Repayment Received"
        )

    result = ledger_collection.update_one(
        {
            "_id": ObjectId(entry_id),
            "user_id": user_id
        },
        {
            "$set": {
                "type": entry_type,
                "amount": amount,
                "date": date,
                "description": description
            }
        }
    )

    if result.modified_count > 0:
        return {
            "message": "Ledger Entry Updated Successfully"
        }

    return {
        "message": "No Changes Made"
    }, 404