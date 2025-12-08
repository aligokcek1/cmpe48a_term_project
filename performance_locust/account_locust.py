# Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from locust import HttpUser, task, SequentialTaskSet, between
from api_urls import ApiUrls
import random
from faker import Faker
import time

fake = Faker()

# Shared state to track registration completion
registration_complete = {"count": 0, "target": 0, "initialized": False}


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
            # Initialize target on first user
            if not registration_complete["initialized"]:
                registration_complete["target"] = self.user.environment.runner.target_user_count
                registration_complete["initialized"] = True
            
            # Create fake account data
            self.user_data = {
                "name": fake.unique.name(),
                "email_id": fake.unique.email(),
                "account_type": random.choice(
                    ["Checking", "Savings", "Money Market", "Investment"]
                ),
                "government_id_type": random.choice(
                    ["Driver's License", "Passport", "SSN"]
                ),
                "govt_id_number": fake.unique.ssn(),
                "address": fake.unique.address(),
                "valid": False  # Default to invalid
            }

            # Create a new account - with error handling
            try:
                response = self.client.post(
                    "/api/accountcreate",
                    data=self.user_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    name="/api/accountcreate (Create Account)"
                )
                if response.status_code == 201 or response.status_code == 200:
                    self.user_data["valid"] = True
                    registration_complete["count"] += 1
                    # Wait for account creation to complete in DB
                    time.sleep(2)
                    
                    # If this is the last user to register, wait extra time
                    if registration_complete["count"] >= registration_complete["target"]:
                        time.sleep(3)
            except Exception as e:
                # Account creation failed, user remains invalid
                self.user_data["valid"] = False
            
            # Wait for all registrations to complete before proceeding
            while registration_complete["count"] < registration_complete["target"]:
                time.sleep(0.5)

        @task
        def get_all_accounts(self):
            # Only if account is valid
            if not self.user_data.get("valid", False):
                return
            
            self.client.post(
                "/api/accountallaccounts",
                data={"email_id": self.user_data["email_id"]},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                name="/api/accountallaccounts (Get All Accounts)"
            )

        @task
        def get_particular_account(self):
            # Only if account is valid
            if not self.user_data.get("valid", False):
                return
            
            self.client.get(
                "/api/accountdetail",
                data={"email": self.user_data["email_id"]},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                name="/api/accountdetail (Get Account Detail)"
            )
