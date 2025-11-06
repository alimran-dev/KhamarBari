from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
from config.db import get_connection
import re

load_dotenv()

app = FastAPI()


class SignupRequest(BaseModel):
    owner_name: str
    farm_name: str
    phone_number: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class CattleRequest(BaseModel):
    name: str
    weight: float


class CattleArchiveRequest(BaseModel):
    name: str
    is_archived: bool

@app.get("/")
def app_root():
    return {"status": "ok", "message": "Server is running"}


@app.post("/signup")
def signup(request: SignupRequest):
    """Signup endpoint that creates a new user with owner_name, farm_name, phone_number, email and password"""
    try:
        # Validate phone number
        cleaned_phone = re.sub(r'[\s\-]', '', request.phone_number)
        phone_pattern = r'^01[3-9]\d{8}$'
        
        if not re.match(phone_pattern, cleaned_phone):
            raise HTTPException(
                status_code=400, 
                detail="Invalid phone number."
            )
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (request.email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Insert new user with cleaned phone number
        cursor.execute(
            "INSERT INTO users (owner_name, farm_name, phone_number, email, password) VALUES (%s, %s, %s, %s, %s)",
            (request.owner_name, request.farm_name, cleaned_phone, request.email, request.password)
        )
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "User registered successfully",
            "data": {
                "owner_name": request.owner_name,
                "farm_name": request.farm_name,
                "phone_number": cleaned_phone,
                "email": request.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/login")
def login(request: LoginRequest):
    """Login endpoint that authenticates a user with email and password"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT owner_name, farm_name, phone_number, email, password FROM users WHERE email = %s", (request.email,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user[4] != request.password:
            raise HTTPException(status_code=401, detail="Invalid password")
        
        return {
            "status": "success",
            "message": "Login successful",
            "data": {
                "owner_name": user[0],
                "farm_name": user[1],
                "phone_number": user[2],
                "email": user[3]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/cattle")
def get_all_cattle():
    """Get all cattle from the cattles table"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Fetch all cattle
        cursor.execute("SELECT Name, weight FROM cattles")
        cattle_records = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Format the results
        cattle_list = [
            {
                "name": record[0],
                "weight": float(record[1]) if record[1] is not None else None
            }
            for record in cattle_records
        ]
        
        return {
            "status": "success",
            "message": "Cattle retrieved successfully",
            "data": cattle_list,
            "count": len(cattle_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/cattle")
def add_cattle(request: CattleRequest):
    """Add a new cattle to the cattles table"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Insert new cattle
        cursor.execute(
            "INSERT INTO cattles (Name, weight) VALUES (%s, %s)",
            (request.name, request.weight)
        )
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Cattle added successfully",
            "data": {
                "name": request.name,
                "weight": request.weight
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.patch("/cattle/archive")
def update_cattle_archive_status(request: CattleArchiveRequest):
    """Update the is_archived status of a cattle"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Update the is_archived status
        cursor.execute(
            "UPDATE cattles SET is_archived = %s WHERE Name = %s",
            (request.is_archived, request.name)
        )
        conn.commit()
        
        # Check if any row was updated
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"Cattle with name '{request.name}' not found")
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Cattle archive status updated successfully",
            "data": {
                "name": request.name,
                "is_archived": request.is_archived
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
