# Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from locust import HttpUser, task, SequentialTaskSet, between
from api_urls import ApiUrls
import random
from faker import Faker
import time
import json

fake = Faker()


class MyUser(HttpUser):
    host = "http://136.119.54.74:8080"
    wait_time = between(2, 3)
    
    # Set connection and read timeout for the HTTP client
    connection_timeout = 60.0
    network_timeout = 60.0
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configure the client with proper timeout settings
        self.client.timeout = (30.0, 60.0)  # (connect timeout, read timeout)

    @task
    class MyUserTasks(SequentialTaskSet):
        wait_time = between(2, 3)

        def on_start(self):
            ##### FIRST USER #####

            # Create fake checking account data
            self.first_user = {
                "name": fake.unique.name(),
                "email_id": fake.unique.email(),
                "account_type": "Checking",
                "government_id_type": random.choice(
                    ["Driver's License", "Passport", "SSN"]
                ),
                "govt_id_number": fake.unique.ssn(),
                "address": fake.unique.address(),
            }
            self.client.post(
                "/api/accountcreate",
                data=self.first_user,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            # Create another fake account
            self.first_user["account_type"] = random.choice(
                ["Savings", "Money Market", "Investment"]
            )
            self.client.post(
                "/api/accountcreate",
                data=self.first_user,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            # Get all accounts
            response = self.client.post(
                "/api/accountallaccounts",
                data={"email_id": self.first_user["email_id"]},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            self.account_numbers = [
                account["account_number"] for account in response.json()["response"]
            ]

            ##### SECOND USER #####

            self.second_user = {
                "name": fake.unique.name(),
                "email_id": fake.unique.email(),
                "account_type": "Checking",
                "government_id_type": random.choice(
                    ["Driver's License", "Passport", "SSN"]
                ),
                "govt_id_number": fake.unique.ssn(),
                "address": fake.unique.address(),
            }
            self.client.post(
                "/api/accountcreate",
                data=self.second_user,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        @task
        def internal_transfer(self):
            self.client.post(
                "/api/transaction",
                data={
                    "sender_account_number": self.account_numbers[0],
                    "receiver_account_number": self.account_numbers[1],
                    "amount": fake.random_int(min=1, max=3),
                    "reason": "Internal Transfer",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        @task
        def external_transfer(self):
            self.client.post(
                "/api/transactionzelle/",
                data={
                    "sender_email": self.first_user["email_id"],
                    "receiver_email": self.second_user["email_id"],
                    "amount": fake.random_int(min=1, max=3),
                    "reason": "External Transfer",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        @task
        def transaction_history(self):
            self.client.post(
                "/api/transactionhistory",
                data={"account_number": self.account_numbers[0]},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
