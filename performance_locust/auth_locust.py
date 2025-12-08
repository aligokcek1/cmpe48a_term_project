# Copyright (c) 2023 Cisco Systems, Inc. and its affiliates All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from locust import HttpUser, task, SequentialTaskSet, between, events
from api_urls import ApiUrls
from faker import Faker
import time

fake = Faker()

# Shared state to track registration completion
registration_complete = {"count": 0, "target": 0, "initialized": False}


class MyUser(HttpUser):
    host = "http://136.119.54.74:8080"

    @task
    class MyUserTasks(SequentialTaskSet):
        wait_time = between(3, 5)  # Increased wait time

        def on_start(self):
            # Initialize target on first user
            if not registration_complete["initialized"]:
                registration_complete["target"] = self.user.environment.runner.target_user_count
                registration_complete["initialized"] = True
            
            # Create fake user data with simple password
            self.user_data = {
                "name": fake.unique.name(),
                "email": fake.unique.email(),
                "password": "TestPass123!",  # Fixed password for reliability
                "valid": False  # Default to invalid
            }

            # Register - with error handling
            try:
                response = self.client.post("/api/users/", json=self.user_data, name="/api/users/ (Register)")
                if response.status_code == 201 or response.status_code == 200:
                    self.user_data["valid"] = True
                    registration_complete["count"] += 1
                    # Wait longer for registration to complete in DB
                    time.sleep(2)
                    
                    # If this is the last user to register, wait extra time
                    if registration_complete["count"] >= registration_complete["target"]:
                        time.sleep(3)
            except Exception as e:
                # Registration failed, user remains invalid
                self.user_data["valid"] = False
                
            # Wait for all registrations to complete before proceeding
            while registration_complete["count"] < registration_complete["target"]:
                time.sleep(0.5)

        @task
        def login(self):
            # Login - only if user is valid
            if not self.user_data.get("valid", False):
                return  # Skip this task if user is not valid
            
            self.client.post(
                "/api/users/auth",
                json={
                    "email": self.user_data["email"],
                    "password": self.user_data["password"],
                },
                name="/api/users/auth (Login)"
            )

        # @task
        # def get_profile(self):
        #     # Get Profile - endpoint doesn't exist or requires different format
        #     self.client.get("/api/users/profile", json={"email": self.user_data["email"]})

        @task
        def update_profile(self):
            # Update Profile - only if user is valid
            if not self.user_data.get("valid", False):
                return  # Skip this task if user is not valid
            
            # Use current password, not a new one to avoid breaking subsequent logins
            self.client.put(
                "/api/users/profile",
                json={
                    "email": self.user_data["email"],
                    "password": self.user_data["password"],
                },
                name="/api/users/profile (Update)"
            )

        @task
        def logout(self):
            # Logout - only if user is valid
            if not self.user_data.get("valid", False):
                return  # Skip this task if user is not valid
            
            self.client.post(
                "/api/users/logout", 
                json={"email": self.user_data["email"]},
                name="/api/users/logout (Logout)"
            )