# Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import functions_framework
from flask import jsonify
import os
from pymongo import MongoClient
import datetime
import logging

logging.basicConfig(level=logging.DEBUG)

# MongoDB connection
DB_URL = os.environ.get('DB_URL')
if DB_URL is None:
    raise Exception("DB_URL environment variable is not set")

client = MongoClient(DB_URL)
db = client["bank"]
collection_accounts = db["accounts"]
collection_loans = db["loans"]

class LoanGeneric:
    def ProcessLoanRequest(self, request_data):
        name = request_data["name"]
        email = request_data["email"]
        account_type = request_data["account_type"]
        account_number = request_data["account_number"]
        govt_id_type = request_data["govt_id_type"]
        govt_id_number = request_data["govt_id_number"]
        loan_type = request_data["loan_type"]
        loan_amount = float(request_data["loan_amount"])
        interest_rate = float(request_data["interest_rate"])
        time_period = request_data["time_period"]
        
        user_account = self.__getAccount(account_number)
        count = collection_accounts.count_documents({"email_id": email, 'account_number': account_number})

        logging.debug(f"user account: {user_account}")
        logging.debug(f"Count: {count}")
        
        if count == 0:
            return {"approved": False, "message": "Email or Account number not found."}
        
        result = self.__approveLoan(user_account, loan_amount)
        message = "Loan Approved" if result else "Loan Rejected"
        
        loan_request = {
            "name": name,
            "email": email,
            "account_type": account_type,
            "account_number": account_number,
            "govt_id_type": govt_id_type,
            "govt_id_number": govt_id_number,
            "loan_type": loan_type,
            "loan_amount": loan_amount,
            "interest_rate": interest_rate,
            "time_period": time_period,
            "status": "Approved" if result else "Declined",
            "timestamp": datetime.datetime.now(),
        }

        collection_loans.insert_one(loan_request)
        return {"approved": result, "message": message}

    def getLoanHistory(self, request_data):
        email = request_data["email"]
        loans = collection_loans.find({"email": email})
        loan_history = []

        for l in loans:
            loan_history.append({
                "name": l["name"],
                "email": l["email"],
                "account_type": l["account_type"],
                "account_number": l["account_number"],
                "govt_id_type": l["govt_id_type"],
                "govt_id_number": l["govt_id_number"],
                "loan_type": l["loan_type"],
                "loan_amount": l["loan_amount"],
                "interest_rate": l["interest_rate"],
                "time_period": l["time_period"],
                "status": l["status"],
                "timestamp": f"{l['timestamp']}",
            })

        return loan_history

    def __getAccount(self, account_num):
        accounts = collection_accounts.find()
        for acc in accounts:
            if acc["account_number"] == account_num:
                return acc
        return None

    def __approveLoan(self, account, amount):
        if amount < 1:
            return False

        account["balance"] += amount
        collection_accounts.update_one(
            {"account_number": account["account_number"]},
            {"$set": {"balance": account["balance"]}},
        )
        return True

# Initialize loan service
loan_service = LoanGeneric()

@functions_framework.http
def process_loan_request(request):
    """Process loan application request"""
    # Handle CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        return ('', 204, headers)
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    }
    
    try:
        request_json = request.get_json(silent=True)
        if not request_json:
            return (jsonify({"error": "Invalid request body"}), 400, headers)
        
        result = loan_service.ProcessLoanRequest(request_json)
        return (jsonify(result), 200, headers)
    
    except KeyError as e:
        logging.error(f"Missing field: {str(e)}")
        return (jsonify({"error": f"Missing field: {str(e)}"}), 400, headers)
    except Exception as e:
        logging.exception("Loan processing error")
        return (jsonify({"error": str(e)}), 500, headers)

@functions_framework.http
def get_loan_history(request):
    """Get loan history"""
    # Handle CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        return ('', 204, headers)
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    }
    
    try:
        request_json = request.get_json(silent=True)
        if not request_json or "email" not in request_json:
            return (jsonify({"error": "Email is required"}), 400, headers)
        
        result = loan_service.getLoanHistory(request_json)
        return (jsonify({"history": result}), 200, headers)
    
    except Exception as e:
        logging.exception("History retrieval error")
        return (jsonify({"error": str(e)}), 500, headers)
