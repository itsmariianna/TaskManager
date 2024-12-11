import json
from pathlib import Path
from passlib.context import CryptContext
from fastapi import HTTPException
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
USERS_FILE = os.getenv("USERS_FILE", "users.json")



# Reading users data
def read_users_data():
    users_file = Path(USERS_FILE)
    if not users_file.exists():
        return {}

    with users_file.open("r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="User data corrupted! Please contact support.")



# Writing users data
def write_users_data(users_data):
    with open(USERS_FILE, "w") as file:
        json.dump(users_data, file, indent=4)



# Check if a user exists
def user_exists(email: str):
    users = read_users_data()
    return email in users



# Adding new user to database
def add_user(name: str, email: str, password: str):
    if user_exists(email):
        raise HTTPException(status_code=400, detail="User with this email already exists!")
    
    users = read_users_data()
    hashed_password = pwd_context.hash(password)
    users[email] = {
        "username": name,
        "password": hashed_password
    }
    write_users_data(users)



# Geting user data by email
def get_user(email: str):
    users = read_users_data()
    return users.get(email)
