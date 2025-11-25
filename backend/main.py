from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv
from config.db import get_connection
import re
import os
import shutil
import random
import json

load_dotenv()

app = FastAPI()

# Mount uploads directory
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


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
    tag_number: str
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
        
        # Fetch all cattle that are not archived
        cursor.execute("SELECT Name, weight, tag_number, breed, current_weight, photo_path FROM cattles WHERE is_archived = FALSE OR is_archived IS NULL")
        cattle_records = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Format the results
        cattle_list = [
            {
                "name": record[0],
                "weight": float(record[1]) if record[1] is not None else None,
                "tag_number": record[2],
                "breed": record[3],
                "current_weight": float(record[4]) if record[4] is not None else None,
                "photo_path": record[5]
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


@app.get("/cattle/archived")
def get_archived_cattle():
    """Get all archived cattle from the cattles table"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Fetch all cattle that are archived
        cursor.execute("SELECT Name, weight, tag_number, breed, current_weight, photo_path FROM cattles WHERE is_archived = TRUE")
        cattle_records = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Format the results
        cattle_list = [
            {
                "name": record[0],
                "weight": float(record[1]) if record[1] is not None else None,
                "tag_number": record[2],
                "breed": record[3],
                "current_weight": float(record[4]) if record[4] is not None else None,
                "photo_path": record[5]
            }
            for record in cattle_records
        ]
        
        return {
            "status": "success",
            "message": "Archived cattle retrieved successfully",
            "data": cattle_list,
            "count": len(cattle_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/cattle")
def add_cattle(
    name: str = Form(...),
    breed: str = Form(None),
    purpose: str = Form(None),
    gender: str = Form(None),
    dob: str = Form(None),
    entry_date: str = Form(None),
    initial_weight: float = Form(None),
    current_weight: float = Form(None),
    seller_name: str = Form(None),
    seller_address: str = Form(None),
    seller_phone: str = Form(None),
    health_notes: str = Form(None),
    medical_history: str = Form(None),
    photo: UploadFile = File(None),
    documents: UploadFile = File(None)
):
    """Add a new cattle to the cattles table"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Generate Tag Number
        tag_number = str(random.randint(100000, 999999))
        
        # Handle File Uploads
        photo_path = None
        documents_path = None
        
        if photo or documents:
            upload_dir = f"uploads/{tag_number}"
            os.makedirs(upload_dir, exist_ok=True)
            
            if photo:
                file_location = f"{upload_dir}/{photo.filename}"
                with open(file_location, "wb+") as file_object:
                    shutil.copyfileobj(photo.file, file_object)
                photo_path = file_location
                
            if documents:
                file_location = f"{upload_dir}/{documents.filename}"
                with open(file_location, "wb+") as file_object:
                    shutil.copyfileobj(documents.file, file_object)
                documents_path = file_location

        # Insert new cattle
        query = """
            INSERT INTO cattles (
                Name, weight, tag_number, breed, purpose, gender, dob, entry_date, 
                initial_weight, current_weight, health_notes, seller_name, 
                seller_address, seller_phone, photo_path, documents_path
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            name, current_weight, tag_number, breed, purpose, gender, dob, entry_date,
            initial_weight, current_weight, health_notes, seller_name,
            seller_address, seller_phone, photo_path, documents_path
        )
        
        cursor.execute(query, values)
        cattle_id = cursor.lastrowid
        conn.commit()
        
        # Insert Medical History
        if medical_history:
            try:
                history_list = json.loads(medical_history)
                if history_list:
                    mh_query = "INSERT INTO medical_history (cattle_id, date, name, diagnosis) VALUES (%s, %s, %s, %s)"
                    mh_values = []
                    for item in history_list:
                        mh_values.append((cattle_id, item['date'], item['name'], item['diagnosis']))
                    
                    cursor.executemany(mh_query, mh_values)
                    conn.commit()
            except json.JSONDecodeError:
                print("Error decoding medical history JSON")
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Cattle added successfully",
            "data": {
                "name": name,
                "tag_number": tag_number,
                "weight": current_weight,
                "photo_path": photo_path
            }
        }
    except Exception as e:
        print(f"Error adding cattle: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.patch("/cattle/archive")
def update_cattle_archive_status(request: CattleArchiveRequest):
    """Update the is_archived status of a cattle"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Update the is_archived status
        cursor.execute(
            "UPDATE cattles SET is_archived = %s WHERE tag_number = %s",
            (request.is_archived, request.tag_number)
        )
        conn.commit()
        
        # Check if any row was updated
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"Cattle with tag_number '{request.tag_number}' not found")
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Cattle archive status updated successfully",
            "data": {
                "tag_number": request.tag_number,
                "is_archived": request.is_archived
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.put("/cattle/{tag_number}")
def update_cattle(
    tag_number: str,
    name: str = Form(...),
    breed: str = Form(None),
    purpose: str = Form(None),
    gender: str = Form(None),
    dob: str = Form(None),
    entry_date: str = Form(None),
    initial_weight: float = Form(None),
    current_weight: float = Form(None),
    seller_name: str = Form(None),
    seller_address: str = Form(None),
    seller_phone: str = Form(None),
    health_notes: str = Form(None)
):
    """Update an existing cattle record"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Update cattle
        query = """
            UPDATE cattles SET
                Name = %s, breed = %s, purpose = %s, gender = %s, dob = %s, 
                entry_date = %s, initial_weight = %s, current_weight = %s, 
                health_notes = %s, seller_name = %s, seller_address = %s, 
                seller_phone = %s
            WHERE tag_number = %s
        """
        values = (
            name, breed, purpose, gender, dob, entry_date,
            initial_weight, current_weight, health_notes, seller_name,
            seller_address, seller_phone, tag_number
        )
        
        cursor.execute(query, values)
        conn.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Cattle not found")
            
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Cattle updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/cattle/{tag_number}")
def get_cattle_details(tag_number: str):
    """Get full details of a specific cattle"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True) # Use dictionary cursor for easier mapping
        
        cursor.execute("SELECT * FROM cattles WHERE tag_number = %s", (tag_number,))
        cattle = cursor.fetchone()
        
        if not cattle:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Cattle not found")
            
        # Normalize the 'Name' field to lowercase 'name' for frontend consistency
        if 'Name' in cattle:
            cattle['name'] = cattle['Name']
            
        # Fetch medical history
        cursor.execute("SELECT * FROM medical_history WHERE cattle_id = %s", (cattle['id'],))
        history = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        cattle['medical_history'] = history
        
        return {
            "status": "success",
            "data": cattle
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
