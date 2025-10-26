from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
from config.db import get_connection
import hashlib
from datetime import datetime

load_dotenv()

app = FastAPI()


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@app.get("/")
def app_root():
    return {"status": "ok", "message": "Server is running"}


@app.post("/signup")
def signup(request: SignupRequest):
    """Signup endpoint that creates a new user with name and email"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (request.email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Insert new user
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (request.name, request.email, request.password)
        )
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "User registered successfully",
            "data": {
                "name": request.name,
                "email": request.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/login")
def login(request: LoginRequest):
    """Login endpoint that authenticates a user with email"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT name, email, password FROM users WHERE email = %s", (request.email,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user[2] != request.password:
            raise HTTPException(status_code=401, detail="Invalid password")
        
        return {
            "status": "success",
            "message": "Login successful",
            "data": {
                "name": user[0],
                "email": user[1]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
