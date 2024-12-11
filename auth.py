import json
from datetime import datetime
from passlib.context import CryptContext
from fastapi import HTTPException, Form, Request, Depends
from fastapi.responses import RedirectResponse
import os
from users_db import add_user, get_user, user_exists
from pathlib import Path
from typing import Optional


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
sessions = {}

# Log file path
LOGS_FILE = Path("logs.json")


# Function to log events directly
def log_event(event: str, username: str, status: Optional[str] = None):
    log_entry = {
        "event": event,
        "username": username,
        "timestamp": datetime.now().isoformat()
    }
    if status:
        log_entry["status"] = status

    # Append or create the logs file
    if LOGS_FILE.exists() and LOGS_FILE.stat().st_size > 0:
        with open(LOGS_FILE, "r+") as file:
            logs = json.load(file)
            logs.append(log_entry)
            file.seek(0)
            json.dump(logs, file, indent=4)
    else:
        with open(LOGS_FILE, "w") as file:
            json.dump([log_entry], file, indent=4)

# Getting authenticated user
def get_authenticated_user(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return RedirectResponse(url="/login", status_code=302)
    return sessions[session_id]


# Handling login
def handle_login(email: str = Form(...), password: str = Form(...)):
    user = get_user(email)

    if user and pwd_context.verify(password, user["password"]):
        session_id = email
        sessions[session_id] = user
        log_event("login", email, "success")
        return session_id
    log_event("login", email, "failed")
    raise HTTPException(status_code=401, detail="Invalid email or password!")


# Handling registration
def handle_registration(name: str, email: str, password: str):
    if user_exists(email):
        raise HTTPException(status_code=400, detail="User with this email already exists!")
    add_user(name, email, password)
    log_event("register", email)


# Handling logout
def handle_logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id and session_id in sessions:
        sessions.pop(session_id)
    log_event("logout", session_id)
    return RedirectResponse(url="/login", status_code=302)


