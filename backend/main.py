from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import Optional
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


class OrderItemRequest(BaseModel):
    product_type: str
    quantity: float
    unit: str
    price_per_unit: float = 0.0
    notes: str = None


class OrderRequest(BaseModel):
    customer_name: str
    customer_email: str = None
    customer_phone: str = None
    items: list[OrderItemRequest]
    delivery_date: str = None
    notes: str = None


class OrderStatusUpdate(BaseModel):
    status: str


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
        cursor.execute("SELECT owner_name, farm_name, phone_number, email, password, photo_url FROM users WHERE email = %s", (request.email,))
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
                "email": user[3],
                "photo_url": user[5]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/owner/{email}")
def get_owner_profile(email: str):
    """Get owner profile information"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT owner_name, farm_name, phone_number, email, photo_url FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "status": "success",
            "data": {
                "owner_name": user[0],
                "farm_name": user[1],
                "phone_number": user[2],
                "email": user[3],
                "photo_url": user[4]
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.put("/owner/{email}")
def update_owner_profile(email: str, request: dict):
    """Update owner profile information"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # First check if user exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="User not found. Please check the email address.")
        
        # Build dynamic update query
        update_fields = []
        params = []
        
        if "owner_name" in request:
            update_fields.append("owner_name = %s")
            params.append(request["owner_name"])
        
        if "farm_name" in request:
            update_fields.append("farm_name = %s")
            params.append(request["farm_name"])
        
        if "phone_number" in request:
            update_fields.append("phone_number = %s")
            params.append(request["phone_number"])
        
        if "photo_url" in request:
            update_fields.append("photo_url = %s")
            params.append(request["photo_url"])
        
        if not update_fields:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="No fields to update")
        
        params.append(email)
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE email = %s"
        
        cursor.execute(query, tuple(params))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Profile updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/owner/{email}/upload-photo")
async def upload_profile_photo(email: str, photo: UploadFile = File(...)):
    """Upload profile photo for owner"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create profile photos directory
        profile_dir = "uploads/profiles"
        os.makedirs(profile_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(photo.filename)[1]
        safe_email = email.replace("@", "_at_").replace(".", "_")
        filename = f"{safe_email}_profile{file_extension}"
        file_path = os.path.join(profile_dir, filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        
        # Update database with photo URL
        photo_url = f"/uploads/profiles/{filename}"
        cursor.execute(
            "UPDATE users SET photo_url = %s WHERE email = %s",
            (photo_url, email)
        )
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Profile photo uploaded successfully",
            "photo_url": photo_url
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/owner/{email}/photo")
def delete_profile_photo(email: str):
    """Delete profile photo for owner"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get current photo URL
        cursor.execute("SELECT photo_url FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        photo_url = result[0]
        
        # Delete file if exists
        if photo_url:
            file_path = photo_url.lstrip("/")
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Update database
        cursor.execute(
            "UPDATE users SET photo_url = NULL WHERE email = %s",
            (email,)
        )
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Profile photo deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/cattle")
def get_all_cattle(user_email: str = None):
    """Get all cattle from the cattles table"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Fetch all cattle that are not archived
        if user_email:
            cursor.execute("SELECT Name, weight, tag_number, breed, current_weight, photo_path FROM cattles WHERE (is_archived = FALSE OR is_archived IS NULL) AND user_email = %s", (user_email,))
        else:
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
def get_archived_cattle(user_email: str = None):
    """Get all archived cattle from the cattles table"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Fetch all cattle that are archived
        if user_email:
            cursor.execute("SELECT Name, weight, tag_number, breed, current_weight, photo_path FROM cattles WHERE is_archived = TRUE AND user_email = %s", (user_email,))
        else:
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
    user_email: str = Form(...),
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
                Name, user_email, weight, tag_number, breed, purpose, gender, dob, entry_date, 
                initial_weight, current_weight, health_notes, seller_name, 
                seller_address, seller_phone, photo_path, documents_path
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            name, user_email, current_weight, tag_number, breed, purpose, gender, dob, entry_date,
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


# ==================== Production Endpoints ====================

class ProductionEntryRequest(BaseModel):
    animal_tag: str
    animal_name: str
    product_type: str
    quantity: float
    unit: str
    time: str
    notes: str = ""
    date: str


@app.post("/production/entry")
def create_production_entry(request: ProductionEntryRequest):
    """Creates a new production entry"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if the animal exists
        cursor.execute("SELECT id FROM cattles WHERE tag_number = %s", (request.animal_tag,))
        cattle = cursor.fetchone()
        
        if not cattle:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Animal not found with the given tag")
        
        cattle_id = cattle[0]
        
        # Insert production entry
        cursor.execute(
            """INSERT INTO production_entries 
               (cattle_id, animal_tag, animal_name, product_type, quantity, unit, entry_time, entry_date, notes) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (cattle_id, request.animal_tag, request.animal_name, request.product_type, 
             request.quantity, request.unit, request.time, request.date, request.notes)
        )
        conn.commit()
        
        entry_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Production entry created successfully",
            "data": {
                "id": entry_id,
                "animal_tag": request.animal_tag,
                "product_type": request.product_type,
                "quantity": request.quantity,
                "unit": request.unit
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/production/entries")
def get_production_entries(limit: int = 10):
    """Get recent production entries"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT * FROM production_entries 
               ORDER BY created_at DESC 
               LIMIT %s""",
            (limit,)
        )
        entries = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": entries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/production/summary")
def get_production_summary():
    """Get production summary for today"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get today's date
        from datetime import date
        today = date.today().strftime("%m/%d/%y")
        
        # Get total milk production
        cursor.execute(
            """SELECT SUM(quantity) as total FROM production_entries 
               WHERE product_type = 'Milk' AND entry_date = %s""",
            (today,)
        )
        milk_result = cursor.fetchone()
        total_milk = milk_result['total'] if milk_result['total'] else 0
        
        # Get total eggs
        cursor.execute(
            """SELECT SUM(quantity) as total FROM production_entries 
               WHERE product_type = 'Eggs' AND entry_date = %s""",
            (today,)
        )
        eggs_result = cursor.fetchone()
        total_eggs = eggs_result['total'] if eggs_result['total'] else 0
        
        # Get total other products (Wool bale + Waste bin)
        cursor.execute(
            """SELECT SUM(quantity) as total FROM production_entries 
               WHERE product_type IN ('Wool bale', 'Waste bin') AND entry_date = %s""",
            (today,)
        )
        other_result = cursor.fetchone()
        total_other = other_result['total'] if other_result['total'] else 0
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": {
                "milk": total_milk,
                "eggs": total_eggs,
                "other": total_other,
                "date": today
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ===================== ORDER ENDPOINTS =====================

@app.post("/orders")
def create_order(request: OrderRequest):
    """Create a new order"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Generate order ID
        order_id = f"ORD-{random.randint(10000, 99999):05d}"
        
        # Calculate total amount (quantity * price_per_unit for each item)
        total_amount = sum(item.quantity * item.price_per_unit for item in request.items)
        
        # Insert order
        cursor.execute(
            """INSERT INTO orders 
               (order_id, customer_name, customer_email, customer_phone, total_amount, delivery_date, notes, status) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')""",
            (order_id, request.customer_name, request.customer_email, request.customer_phone, 
             total_amount, request.delivery_date, request.notes)
        )
        
        # Insert order items with price
        for item in request.items:
            cursor.execute(
                """INSERT INTO order_items 
                   (order_id, product_type, quantity, unit, price_per_unit, notes) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (order_id, item.product_type, item.quantity, item.unit, item.price_per_unit, item.notes)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Order created successfully",
            "data": {
                "order_id": order_id,
                "customer_name": request.customer_name,
                "total_amount": total_amount
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/orders")
def get_orders(
    status: str = None,
    search: str = None,
    product_type: str = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 100
):
    """Get all orders with optional filters"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Build query
        query = """
            SELECT o.*, 
                   GROUP_CONCAT(DISTINCT oi.product_type SEPARATOR ', ') as products,
                   COALESCE(SUM(oi.quantity), 0) as total_quantity
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE 1=1
        """
        params = []
        
        if status and status != "All":
            query += " AND o.status = %s"
            params.append(status)
        
        if search:
            query += " AND (o.order_id LIKE %s OR o.customer_name LIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term])
        
        if product_type and product_type != "All":
            query += " AND oi.product_type = %s"
            params.append(product_type)
        
        if start_date and end_date:
            query += " AND o.created_at BETWEEN %s AND %s"
            params.extend([start_date, end_date])
        
        query += " GROUP BY o.id ORDER BY o.created_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, tuple(params))
        orders = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": orders,
            "count": len(orders)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/orders/{order_id}")
def get_order_details(order_id: str):
    """Get detailed information about a specific order"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get order details
        cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
        order = cursor.fetchone()
        
        if not order:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Get order items
        cursor.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
        items = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        order['items'] = items
        
        return {
            "status": "success",
            "data": order
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.put("/orders/{order_id}/status")
def update_order_status(order_id: str, request: OrderStatusUpdate):
    """Update order status"""
    try:
        from datetime import datetime
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if order exists
        cursor.execute("SELECT id FROM orders WHERE order_id = %s", (order_id,))
        order = cursor.fetchone()
        
        if not order:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Update status and timestamp based on status
        timestamp_field = None
        if request.status == "Packed":
            timestamp_field = "packed_at"
        elif request.status == "Out for Delivery":
            timestamp_field = "out_for_delivery_at"
        elif request.status == "Delivered":
            timestamp_field = "delivered_at"
        
        if timestamp_field:
            cursor.execute(
                f"UPDATE orders SET status = %s, {timestamp_field} = %s WHERE order_id = %s",
                (request.status, datetime.now(), order_id)
            )
        else:
            cursor.execute(
                "UPDATE orders SET status = %s WHERE order_id = %s",
                (request.status, order_id)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Order status updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/orders/{order_id}")
def delete_order(order_id: str):
    """Delete an order (sets status to Cancelled)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if order exists
        cursor.execute("SELECT id FROM orders WHERE order_id = %s", (order_id,))
        order = cursor.fetchone()
        
        if not order:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Update status to cancelled
        cursor.execute(
            "UPDATE orders SET status = 'Cancelled' WHERE order_id = %s",
            (order_id,)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Order cancelled successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/orders/stats/summary")
def get_orders_stats():
    """Get order statistics"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get total orders by status
        cursor.execute("""
            SELECT 
                COUNT(*) as total_orders,
                SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending_orders,
                SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) as delivered_orders,
                SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled_orders,
                SUM(total_amount) as total_revenue
            FROM orders
        """)
        stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ===================== LABOUR MANAGEMENT ENDPOINTS =====================

class LabourerRequest(BaseModel):
    full_name: str
    phone_number: str = None
    national_id: str = None
    address: str = None
    photo_url: str = None
    position: str
    joining_date: str
    status: str = "Active"
    pay_type: str  # Monthly_Salary or Daily_Wage
    base_rate: float


class AttendanceRequest(BaseModel):
    labour_id: int
    date: str
    status: str  # Present, Absent, Half-Day
    overtime_hours: int = 0
    notes: str = None


class BulkAttendanceRequest(BaseModel):
    date: str
    attendance_records: list  # List of {labour_id, status, overtime_hours, notes}


class PayrollRequest(BaseModel):
    labour_id: int
    month: int
    year: int
    bonus_amount: float = 0.0
    deduction_amount: float = 0.0
    notes: str = None


class PayrollUpdateRequest(BaseModel):
    payment_status: str = None
    payment_date: str = None
    bonus_amount: float = None
    deduction_amount: float = None
    total_payable: float = None


@app.post("/labourers")
def create_labourer(request: LabourerRequest):
    """Create a new labourer"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO labourers 
               (full_name, phone_number, national_id, address, photo_url, position, 
                joining_date, status, pay_type, base_rate) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (request.full_name, request.phone_number, request.national_id, request.address,
             request.photo_url, request.position, request.joining_date, request.status,
             request.pay_type, request.base_rate)
        )
        
        labourer_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Labourer created successfully",
            "data": {"id": labourer_id}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/labourers")
def get_labourers(status: str = None, position: str = None):
    """Get all labourers with optional filters"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM labourers WHERE 1=1"
        params = []
        
        if status and status != "All":
            query += " AND status = %s"
            params.append(status)
        
        if position and position != "All":
            query += " AND position = %s"
            params.append(position)
        
        query += " ORDER BY full_name ASC"
        
        cursor.execute(query, tuple(params))
        labourers = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": labourers,
            "count": len(labourers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/labourers/{labour_id}")
def get_labourer(labour_id: int):
    """Get a specific labourer by ID"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM labourers WHERE id = %s", (labour_id,))
        labourer = cursor.fetchone()
        
        if not labourer:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Labourer not found")
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": labourer
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.put("/labourers/{labour_id}")
def update_labourer(labour_id: int, request: LabourerRequest):
    """Update a labourer's information"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """UPDATE labourers 
               SET full_name = %s, phone_number = %s, national_id = %s, address = %s,
                   photo_url = %s, position = %s, joining_date = %s, status = %s,
                   pay_type = %s, base_rate = %s
               WHERE id = %s""",
            (request.full_name, request.phone_number, request.national_id, request.address,
             request.photo_url, request.position, request.joining_date, request.status,
             request.pay_type, request.base_rate, labour_id)
        )
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Labourer not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Labourer updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/labourers/{labour_id}")
def delete_labourer(labour_id: int):
    """Soft delete a labourer (set status to Inactive)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE labourers SET status = 'Inactive' WHERE id = %s",
            (labour_id,)
        )
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Labourer not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Labourer deactivated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Attendance endpoints
@app.post("/attendance")
def mark_attendance(request: AttendanceRequest):
    """Mark attendance for a labourer"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO attendance 
               (labour_id, date, status, overtime_hours, notes) 
               VALUES (%s, %s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE 
               status = VALUES(status), 
               overtime_hours = VALUES(overtime_hours), 
               notes = VALUES(notes)""",
            (request.labour_id, request.date, request.status, 
             request.overtime_hours, request.notes)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Attendance marked successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/attendance/bulk")
def mark_bulk_attendance(request: BulkAttendanceRequest):
    """Mark attendance for multiple labourers on a specific date"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        for record in request.attendance_records:
            cursor.execute(
                """INSERT INTO attendance 
                   (labour_id, date, status, overtime_hours, notes) 
                   VALUES (%s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE 
                   status = VALUES(status), 
                   overtime_hours = VALUES(overtime_hours), 
                   notes = VALUES(notes)""",
                (record['labour_id'], request.date, record['status'], 
                 record.get('overtime_hours', 0), record.get('notes'))
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": f"Bulk attendance marked for {len(request.attendance_records)} labourers"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/attendance")
def get_attendance(labour_id: int = None, month: int = None, year: int = None, date: str = None):
    """Get attendance records with filters"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """SELECT a.*, l.full_name, l.position 
                   FROM attendance a 
                   JOIN labourers l ON a.labour_id = l.id 
                   WHERE 1=1"""
        params = []
        
        if labour_id:
            query += " AND a.labour_id = %s"
            params.append(labour_id)
        
        if month and year:
            query += " AND MONTH(a.date) = %s AND YEAR(a.date) = %s"
            params.extend([month, year])
        
        if date:
            query += " AND a.date = %s"
            params.append(date)
        
        query += " ORDER BY a.date DESC, l.full_name ASC"
        
        cursor.execute(query, tuple(params))
        attendance = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": attendance,
            "count": len(attendance)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/payroll/calculate")
def calculate_payroll(request: PayrollRequest):
    """Calculate and create payroll for a labourer"""
    try:
        from datetime import datetime
        import calendar
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get labourer details
        cursor.execute("SELECT * FROM labourers WHERE id = %s", (request.labour_id,))
        labourer = cursor.fetchone()
        
        if not labourer:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Labourer not found")
        
        # Get attendance for the month
        cursor.execute(
            """SELECT status, overtime_hours FROM attendance 
               WHERE labour_id = %s AND MONTH(date) = %s AND YEAR(date) = %s""",
            (request.labour_id, request.month, request.year)
        )
        attendance_records = cursor.fetchall()
        
        # Calculate working days
        total_working_days = 0.0
        total_overtime_hours = 0
        
        for record in attendance_records:
            if record['status'] == 'Present':
                total_working_days += 1.0
            elif record['status'] == 'Half-Day':
                total_working_days += 0.5
            total_overtime_hours += record.get('overtime_hours', 0)
        
        # Calculate base earning
        base_rate = float(labourer['base_rate'])
        if labourer['pay_type'] == 'Monthly_Salary':
            # For monthly salary, calculate pro-rata if days missed
            days_in_month = calendar.monthrange(request.year, request.month)[1]
            base_earning = (base_rate / days_in_month) * total_working_days
        else:  # Daily_Wage
            base_earning = base_rate * total_working_days
        
        # Calculate total payable
        total_payable = base_earning + request.bonus_amount - request.deduction_amount
        
        # Insert or update payroll record
        cursor.execute(
            """INSERT INTO payroll_transactions 
               (labour_id, month, year, total_working_days, base_earning, 
                bonus_amount, deduction_amount, total_payable, notes) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE 
               total_working_days = VALUES(total_working_days),
               base_earning = VALUES(base_earning),
               bonus_amount = VALUES(bonus_amount),
               deduction_amount = VALUES(deduction_amount),
               total_payable = VALUES(total_payable),
               notes = VALUES(notes)""",
            (request.labour_id, request.month, request.year, total_working_days,
             base_earning, request.bonus_amount, request.deduction_amount, 
             total_payable, request.notes)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Payroll calculated successfully",
            "data": {
                "total_working_days": total_working_days,
                "base_earning": float(base_earning),
                "bonus_amount": float(request.bonus_amount),
                "deduction_amount": float(request.deduction_amount),
                "total_payable": float(total_payable)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/payroll")
def get_payroll(month: int = None, year: int = None, labour_id: int = None, status: str = None):
    """Get payroll transactions with filters"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """SELECT p.*, l.full_name, l.position, l.pay_type 
                   FROM payroll_transactions p 
                   JOIN labourers l ON p.labour_id = l.id 
                   WHERE 1=1"""
        params = []
        
        if month:
            query += " AND p.month = %s"
            params.append(month)
        
        if year:
            query += " AND p.year = %s"
            params.append(year)
        
        if labour_id:
            query += " AND p.labour_id = %s"
            params.append(labour_id)
        
        if status and status != "All":
            query += " AND p.payment_status = %s"
            params.append(status)
        
        query += " ORDER BY p.year DESC, p.month DESC, l.full_name ASC"
        
        cursor.execute(query, tuple(params))
        payroll = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": payroll,
            "count": len(payroll)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.put("/payroll/{payroll_id}")
def update_payroll_status(payroll_id: int, request: PayrollUpdateRequest):
    """Update payroll payment status and/or amounts"""
    try:
        from datetime import datetime
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query based on provided fields
        update_fields = []
        params = []
        
        if request.payment_status is not None:
            update_fields.append("payment_status = %s")
            params.append(request.payment_status)
        
        if request.payment_date is not None:
            update_fields.append("payment_date = %s")
            params.append(request.payment_date)
        elif request.payment_status == "Paid":
            update_fields.append("payment_date = %s")
            params.append(datetime.now().strftime("%Y-%m-%d"))
        
        if request.bonus_amount is not None:
            update_fields.append("bonus_amount = %s")
            params.append(request.bonus_amount)
        
        if request.deduction_amount is not None:
            update_fields.append("deduction_amount = %s")
            params.append(request.deduction_amount)
        
        if request.total_payable is not None:
            update_fields.append("total_payable = %s")
            params.append(request.total_payable)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        params.append(payroll_id)
        
        query = f"UPDATE payroll_transactions SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, tuple(params))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Payroll record not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Payroll updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/payroll/{payroll_id}")
def delete_payroll(payroll_id: int):
    """Delete a payroll transaction"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM payroll_transactions WHERE id = %s", (payroll_id,))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Payroll record not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Payroll deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/labourers/stats/summary")
def get_labour_stats():
    """Get labour statistics"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_labourers,
                SUM(CASE WHEN status = 'Active' THEN 1 ELSE 0 END) as active_labourers,
                SUM(CASE WHEN pay_type = 'Monthly_Salary' THEN 1 ELSE 0 END) as monthly_employees,
                SUM(CASE WHEN pay_type = 'Daily_Wage' THEN 1 ELSE 0 END) as daily_workers
            FROM labourers
        """)
        stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ===================== WAREHOUSE ENDPOINTS =====================

class StockItemRequest(BaseModel):
    item_name: str
    category: str
    batch_no: str
    quantity: float
    unit: str
    expiry_date: str | None = None
    photo_path: str | None = None


class StockTransferRequest(BaseModel):
    item_id: int
    target_category: str
    notes: str | None = None


class StockAdjustmentRequest(BaseModel):
    item_id: int
    adjustment_type: str
    quantity: float
    reason: str


@app.get("/warehouse/stock")
def get_all_stock():
    """Get all stock items"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, item_name, category, batch_no, quantity, unit, 
                   DATE_FORMAT(expiry_date, '%Y-%m-%d') as expiry_date, photo_path,
                   created_at, updated_at
            FROM stock_items
            ORDER BY created_at DESC
        """)
        stock_items = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": stock_items,
            "count": len(stock_items)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/warehouse/stock/category/{category}")
def get_stock_by_category(category: str):
    """Get stock items by category"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, item_name, category, batch_no, quantity, unit,
                   DATE_FORMAT(expiry_date, '%Y-%m-%d') as expiry_date, photo_path,
                   created_at, updated_at
            FROM stock_items
            WHERE category = %s
            ORDER BY created_at DESC
        """, (category,))
        stock_items = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": stock_items,
            "count": len(stock_items)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/warehouse/stock/{item_id}")
def get_stock_item(item_id: int):
    """Get specific stock item details"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, item_name, category, batch_no, quantity, unit,
                   DATE_FORMAT(expiry_date, '%Y-%m-%d') as expiry_date, photo_path,
                   created_at, updated_at
            FROM stock_items
            WHERE id = %s
        """, (item_id,))
        item = cursor.fetchone()
        
        if not item:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Stock item not found")
        
        # Get movement history
        cursor.execute("""
            SELECT id, movement_type, quantity_change, quantity_before, quantity_after,
                   from_category, to_category, reason, movement_date
            FROM stock_movements
            WHERE stock_item_id = %s
            ORDER BY movement_date DESC
            LIMIT 10
        """, (item_id,))
        movements = cursor.fetchall()
        
        item['movement_history'] = movements
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": item
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/warehouse/stock")
def add_stock_item(request: StockItemRequest):
    """Add new stock item"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Convert empty strings to None for nullable fields
        expiry_date = request.expiry_date if request.expiry_date else None
        photo_path = request.photo_path if request.photo_path else None
        
        # Insert stock item
        cursor.execute("""
            INSERT INTO stock_items 
            (item_name, category, batch_no, quantity, unit, expiry_date, photo_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            request.item_name,
            request.category,
            request.batch_no,
            request.quantity,
            request.unit,
            expiry_date,
            photo_path
        ))
        
        stock_item_id = cursor.lastrowid
        
        # Record initial stock movement
        cursor.execute("""
            INSERT INTO stock_movements
            (stock_item_id, movement_type, quantity_change, quantity_before, quantity_after, reason)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            stock_item_id,
            "Initial",
            request.quantity,
            0,
            request.quantity,
            f"Initial stock entry for {request.item_name}"
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Stock item added successfully",
            "data": {
                "id": stock_item_id,
                "item_name": request.item_name,
                "quantity": request.quantity
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/warehouse/transfer")
def transfer_stock(request: StockTransferRequest):
    """Transfer stock item to another category"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get current item details
        cursor.execute("""
            SELECT id, item_name, category, quantity
            FROM stock_items
            WHERE id = %s
        """, (request.item_id,))
        item = cursor.fetchone()
        
        if not item:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Stock item not found")
        
        old_category = item['category']
        
        # Update category
        cursor.execute("""
            UPDATE stock_items
            SET category = %s
            WHERE id = %s
        """, (request.target_category, request.item_id))
        
        # Record movement
        cursor.execute("""
            INSERT INTO stock_movements
            (stock_item_id, movement_type, quantity_change, quantity_before, quantity_after,
             from_category, to_category, reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            request.item_id,
            "Transfer",
            0,
            item['quantity'],
            item['quantity'],
            old_category,
            request.target_category,
            request.notes or f"Transferred from {old_category} to {request.target_category}"
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Stock transferred successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/warehouse/adjust")
def adjust_stock(request: StockAdjustmentRequest):
    """Adjust stock quantity"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get current item details
        cursor.execute("""
            SELECT id, item_name, quantity
            FROM stock_items
            WHERE id = %s
        """, (request.item_id,))
        item = cursor.fetchone()
        
        if not item:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Stock item not found")
        
        current_quantity = float(item['quantity'])
        
        # Calculate new quantity based on adjustment type
        if request.adjustment_type == "Add":
            new_quantity = current_quantity + request.quantity
            quantity_change = request.quantity
        elif request.adjustment_type == "Remove":
            new_quantity = max(0, current_quantity - request.quantity)
            quantity_change = -request.quantity
        elif request.adjustment_type == "Set To":
            new_quantity = request.quantity
            quantity_change = request.quantity - current_quantity
        else:
            raise HTTPException(status_code=400, detail="Invalid adjustment type")
        
        # Update quantity
        cursor.execute("""
            UPDATE stock_items
            SET quantity = %s
            WHERE id = %s
        """, (new_quantity, request.item_id))
        
        # Record movement
        cursor.execute("""
            INSERT INTO stock_movements
            (stock_item_id, movement_type, quantity_change, quantity_before, quantity_after, reason)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            request.item_id,
            "Adjustment",
            quantity_change,
            current_quantity,
            new_quantity,
            request.reason
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Stock adjusted successfully",
            "data": {
                "previous_quantity": current_quantity,
                "new_quantity": new_quantity
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/warehouse/summary")
def get_warehouse_summary():
    """Get warehouse summary statistics"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Total feed stock
        cursor.execute("""
            SELECT SUM(quantity) as total
            FROM stock_items
            WHERE category = 'Feed' AND unit = 'kg'
        """)
        feed_result = cursor.fetchone()
        total_feed = feed_result['total'] if feed_result['total'] else 0
        
        # Medicine stock count
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM stock_items
            WHERE category = 'Medicine'
        """)
        medicine_result = cursor.fetchone()
        medicine_count = medicine_result['count']
        
        # Product stock (milk and eggs)
        cursor.execute("""
            SELECT SUM(quantity) as total
            FROM stock_items
            WHERE category = 'Products' AND item_name LIKE '%milk%' AND unit = 'L'
        """)
        milk_result = cursor.fetchone()
        total_milk = milk_result['total'] if milk_result['total'] else 0
        
        cursor.execute("""
            SELECT SUM(quantity) as total
            FROM stock_items
            WHERE category = 'Products' AND item_name LIKE '%egg%' AND unit IN ('Pcs', 'pieces')
        """)
        eggs_result = cursor.fetchone()
        total_eggs = eggs_result['total'] if eggs_result['total'] else 0
        
        # Low stock items (quantity < 50)
        cursor.execute("""
            SELECT id, item_name, category, quantity, unit
            FROM stock_items
            WHERE quantity < 50
            ORDER BY quantity ASC
        """)
        low_stock = cursor.fetchall()
        
        # Expiring items (within 7 days)
        cursor.execute("""
            SELECT id, item_name, category, quantity, unit, 
                   DATE_FORMAT(expiry_date, '%Y-%m-%d') as expiry_date,
                   DATEDIFF(expiry_date, CURDATE()) as days_until_expiry
            FROM stock_items
            WHERE expiry_date IS NOT NULL
              AND expiry_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            ORDER BY expiry_date ASC
        """)
        expiring_items = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": {
                "total_feed_kg": float(total_feed),
                "medicine_items": medicine_count,
                "total_milk_liters": float(total_milk),
                "total_eggs_pieces": float(total_eggs),
                "low_stock_items": low_stock,
                "expiring_items": expiring_items
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/warehouse/stock/{item_id}")
def delete_stock_item(item_id: int):
    """Delete a stock item"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM stock_items WHERE id = %s", (item_id,))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Stock item not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Stock item deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ==================== FINANCE ENDPOINTS ====================

class VeterinaryVisitRequest(BaseModel):
    animal_tag: str
    animal_name: Optional[str] = None
    visit_date: str
    visit_type: str = "Routine Check"
    vet_name: str
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    medicines_used: Optional[str] = None
    cost: float = 0.0
    notes: Optional[str] = None
    next_visit_date: Optional[str] = None


class VeterinaryTreatmentRequest(BaseModel):
    visit_id: Optional[int] = None
    animal_tag: str
    treatment_date: str
    diagnosis: Optional[str] = None
    treatment_description: str
    medicines_used: Optional[str] = None
    dosage: Optional[str] = None
    duration_days: Optional[int] = None
    cost: float = 0.0
    vet_name: Optional[str] = None
    notes: Optional[str] = None


class MedicalHistoryRequest(BaseModel):
    animal_tag: str
    animal_name: Optional[str] = None
    date: str
    record_type: str
    disease_name: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    medicines_used: Optional[str] = None
    vet_name: Optional[str] = None
    cost: float = 0.0
    notes: Optional[str] = None


class VaccinationScheduleRequest(BaseModel):
    animal_tag: str
    animal_name: Optional[str] = None
    vaccine_name: str
    scheduled_date: str
    completed: bool = False
    completion_date: Optional[str] = None
    vet_name: Optional[str] = None
    cost: float = 0.0
    notes: Optional[str] = None


class FinancialEntryRequest(BaseModel):
    entry_type: str  # 'expense' or 'income'
    category_id: int
    amount: float
    date: str
    description: str = None
    notes: str = None
    linked_item_type: str = None
    linked_item_id: int = None


@app.get("/finance/categories")
def get_financial_categories():
    """Get all financial categories"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, type, description 
            FROM financial_categories 
            ORDER BY type, name
        """)
        categories = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        result = []
        for cat in categories:
            result.append({
                "id": cat[0],
                "name": cat[1],
                "type": cat[2],
                "description": cat[3]
            })
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/finance/templates")
def get_expense_templates():
    """Get all expense templates for quick shortcuts"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.id, t.name, t.category_id, c.name as category_name, 
                   t.default_amount, t.description, t.icon
            FROM expense_templates t
            JOIN financial_categories c ON t.category_id = c.id
            WHERE t.is_active = TRUE
            ORDER BY t.name
        """)
        templates = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        result = []
        for tpl in templates:
            result.append({
                "id": tpl[0],
                "name": tpl[1],
                "category_id": tpl[2],
                "category_name": tpl[3],
                "default_amount": float(tpl[4]) if tpl[4] else None,
                "description": tpl[5],
                "icon": tpl[6]
            })
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/finance/entries")
async def create_financial_entry(
    entry_type: str = Form(...),
    category_id: int = Form(...),
    amount: float = Form(...),
    date: str = Form(...),
    email: str = Form(...),
    description: str = Form(None),
    notes: str = Form(None),
    linked_item_type: str = Form(None),
    linked_item_id: int = Form(None),
    receipt: UploadFile = File(None)
):
    """Create a new financial entry with optional receipt upload"""
    try:
        # Verify user exists
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        user_email = email
        receipt_path = None
        
        # Handle receipt upload
        if receipt:
            # Use email hash for directory to avoid special characters
            import hashlib
            email_hash = hashlib.md5(email.encode()).hexdigest()[:8]
            upload_dir = f"uploads/receipts/{email_hash}"
            os.makedirs(upload_dir, exist_ok=True)
            
            file_ext = receipt.filename.split('.')[-1] if '.' in receipt.filename else 'jpg'
            timestamp = random.randint(100000, 999999)
            filename = f"receipt_{timestamp}.{file_ext}"
            file_path = os.path.join(upload_dir, filename)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(receipt.file, buffer)
            
            receipt_path = file_path
        
        # Insert financial entry
        cursor.execute("""
            INSERT INTO financial_entries 
            (user_email, entry_type, category_id, amount, date, description, notes, 
             receipt_path, linked_item_type, linked_item_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_email, entry_type, category_id, amount, date, description, notes,
              receipt_path, linked_item_type, linked_item_id))
        
        entry_id = cursor.lastrowid
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Financial entry created successfully",
            "data": {
                "id": entry_id,
                "receipt_path": receipt_path
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/finance/entries/{email}")
def get_financial_entries(
    email: str,
    entry_type: str = None,
    category_id: int = None,
    start_date: str = None,
    end_date: str = None,
    limit: int = 100
):
    """Get financial entries with filters"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verify user exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build query
        query = """
            SELECT e.id, e.entry_type, e.category_id, c.name as category_name,
                   e.amount, e.date, e.description, e.notes, e.receipt_path,
                   e.linked_item_type, e.linked_item_id, e.created_at
            FROM financial_entries e
            JOIN financial_categories c ON e.category_id = c.id
            WHERE e.user_email = %s
        """
        params = [email]
        
        if entry_type:
            query += " AND e.entry_type = %s"
            params.append(entry_type)
        
        if category_id:
            query += " AND e.category_id = %s"
            params.append(category_id)
        
        if start_date:
            query += " AND e.date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND e.date <= %s"
            params.append(end_date)
        
        query += " ORDER BY e.date DESC, e.created_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        entries = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        result = []
        for entry in entries:
            result.append({
                "id": entry[0],
                "entry_type": entry[1],
                "category_id": entry[2],
                "category_name": entry[3],
                "amount": float(entry[4]),
                "date": str(entry[5]),
                "description": entry[6],
                "notes": entry[7],
                "receipt_path": entry[8],
                "linked_item_type": entry[9],
                "linked_item_id": entry[10],
                "created_at": str(entry[11])
            })
        
        return {
            "status": "success",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/finance/summary/{email}")
def get_finance_summary(
    email: str,
    start_date: str = None,
    end_date: str = None
):
    """Get financial summary with income, expense, and category breakdown"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verify user exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build date filter
        date_filter = "WHERE user_email = %s"
        params = [email]
        
        if start_date:
            date_filter += " AND date >= %s"
            params.append(start_date)
        
        if end_date:
            date_filter += " AND date <= %s"
            params.append(end_date)
        
        # Get total income
        cursor.execute(f"""
            SELECT COALESCE(SUM(amount), 0) 
            FROM financial_entries 
            {date_filter} AND entry_type = 'income'
        """, params)
        total_income = float(cursor.fetchone()[0])
        
        # Get total expense
        cursor.execute(f"""
            SELECT COALESCE(SUM(amount), 0) 
            FROM financial_entries 
            {date_filter} AND entry_type = 'expense'
        """, params)
        total_expense = float(cursor.fetchone()[0])
        
        # Get top expense category
        cursor.execute(f"""
            SELECT c.name, SUM(e.amount) as total
            FROM financial_entries e
            JOIN financial_categories c ON e.category_id = c.id
            {date_filter} AND e.entry_type = 'expense'
            GROUP BY c.id, c.name
            ORDER BY total DESC
            LIMIT 1
        """, params)
        top_expense = cursor.fetchone()
        top_expense_category = top_expense[0] if top_expense else "N/A"
        top_expense_amount = float(top_expense[1]) if top_expense else 0
        
        # Get category breakdown
        cursor.execute(f"""
            SELECT c.name, e.entry_type, SUM(e.amount) as total
            FROM financial_entries e
            JOIN financial_categories c ON e.category_id = c.id
            {date_filter}
            GROUP BY c.id, c.name, e.entry_type
            ORDER BY total DESC
        """, params)
        category_breakdown = cursor.fetchall()
        
        # Get daily data for chart (last 30 days if no date range specified)
        chart_params = [email]
        if not start_date and not end_date:
            chart_date_filter = "WHERE user_email = %s AND date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
        else:
            chart_date_filter = date_filter
            chart_params = params.copy()
        
        cursor.execute(f"""
            SELECT date, entry_type, SUM(amount) as total
            FROM financial_entries
            {chart_date_filter}
            GROUP BY date, entry_type
            ORDER BY date ASC
        """, chart_params)
        daily_data = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Format category breakdown
        categories = []
        for cat in category_breakdown:
            categories.append({
                "category": cat[0],
                "type": cat[1],
                "amount": float(cat[2])
            })
        
        # Format daily data
        daily_chart = []
        for day in daily_data:
            daily_chart.append({
                "date": str(day[0]),
                "type": day[1],
                "amount": float(day[2])
            })
        
        return {
            "status": "success",
            "data": {
                "total_income": total_income,
                "total_expense": total_expense,
                "net_profit": total_income - total_expense,
                "top_expense_category": top_expense_category,
                "top_expense_amount": top_expense_amount,
                "category_breakdown": categories,
                "daily_data": daily_chart
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/finance/entries/{entry_id}")
def delete_financial_entry(entry_id: int):
    """Delete a financial entry"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get receipt path before deleting
        cursor.execute("SELECT receipt_path FROM financial_entries WHERE id = %s", (entry_id,))
        entry = cursor.fetchone()
        
        if not entry:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Financial entry not found")
        
        receipt_path = entry[0]
        
        # Delete the entry
        cursor.execute("DELETE FROM financial_entries WHERE id = %s", (entry_id,))
        conn.commit()
        
        # Delete receipt file if exists
        if receipt_path and os.path.exists(receipt_path):
            try:
                os.remove(receipt_path)
            except:
                pass
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Financial entry deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ===========================
# VETERINARY ENDPOINTS
# ===========================

@app.post("/veterinary/visits")
def create_veterinary_visit(request: VeterinaryVisitRequest):
    """Create a new veterinary visit"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO veterinary_visits 
            (animal_tag, animal_name, visit_date, visit_type, vet_name, diagnosis, 
             treatment, medicines_used, cost, notes, next_visit_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            request.animal_tag, request.animal_name, request.visit_date, request.visit_type,
            request.vet_name, request.diagnosis, request.treatment, request.medicines_used,
            request.cost, request.notes, request.next_visit_date
        ))
        
        visit_id = cursor.lastrowid
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Veterinary visit created successfully",
            "data": {"id": visit_id}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/veterinary/visits")
def get_veterinary_visits(animal_tag: str = None, limit: int = 100):
    """Get all veterinary visits or filter by animal tag"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if animal_tag:
            cursor.execute("""
                SELECT id, animal_tag, animal_name, visit_date, visit_type, vet_name,
                       diagnosis, treatment, medicines_used, cost, notes, next_visit_date,
                       created_at, updated_at
                FROM veterinary_visits
                WHERE animal_tag = %s
                ORDER BY visit_date DESC
                LIMIT %s
            """, (animal_tag, limit))
        else:
            cursor.execute("""
                SELECT id, animal_tag, animal_name, visit_date, visit_type, vet_name,
                       diagnosis, treatment, medicines_used, cost, notes, next_visit_date,
                       created_at, updated_at
                FROM veterinary_visits
                ORDER BY visit_date DESC
                LIMIT %s
            """, (limit,))
        
        visits = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        result = []
        for visit in visits:
            result.append({
                "id": visit[0],
                "animal_tag": visit[1],
                "animal_name": visit[2],
                "visit_date": str(visit[3]),
                "visit_type": visit[4],
                "vet_name": visit[5],
                "diagnosis": visit[6],
                "treatment": visit[7],
                "medicines_used": visit[8],
                "cost": float(visit[9]) if visit[9] else 0.0,
                "notes": visit[10],
                "next_visit_date": str(visit[11]) if visit[11] else None,
                "created_at": str(visit[12]),
                "updated_at": str(visit[13])
            })
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/veterinary/visits/{visit_id}")
def get_veterinary_visit(visit_id: int):
    """Get a specific veterinary visit by ID"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, animal_tag, animal_name, visit_date, visit_type, vet_name,
                   diagnosis, treatment, medicines_used, cost, notes, next_visit_date,
                   created_at, updated_at
            FROM veterinary_visits
            WHERE id = %s
        """, (visit_id,))
        
        visit = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not visit:
            raise HTTPException(status_code=404, detail="Veterinary visit not found")
        
        return {
            "status": "success",
            "data": {
                "id": visit[0],
                "animal_tag": visit[1],
                "animal_name": visit[2],
                "visit_date": str(visit[3]),
                "visit_type": visit[4],
                "vet_name": visit[5],
                "diagnosis": visit[6],
                "treatment": visit[7],
                "medicines_used": visit[8],
                "cost": float(visit[9]) if visit[9] else 0.0,
                "notes": visit[10],
                "next_visit_date": str(visit[11]) if visit[11] else None,
                "created_at": str(visit[12]),
                "updated_at": str(visit[13])
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.put("/veterinary/visits/{visit_id}")
def update_veterinary_visit(visit_id: int, request: VeterinaryVisitRequest):
    """Update a veterinary visit"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE veterinary_visits
            SET animal_tag = %s, animal_name = %s, visit_date = %s, visit_type = %s,
                vet_name = %s, diagnosis = %s, treatment = %s, medicines_used = %s,
                cost = %s, notes = %s, next_visit_date = %s
            WHERE id = %s
        """, (
            request.animal_tag, request.animal_name, request.visit_date, request.visit_type,
            request.vet_name, request.diagnosis, request.treatment, request.medicines_used,
            request.cost, request.notes, request.next_visit_date, visit_id
        ))
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Veterinary visit updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/veterinary/visits/{visit_id}")
def delete_veterinary_visit(visit_id: int):
    """Delete a veterinary visit"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM veterinary_visits WHERE id = %s", (visit_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Veterinary visit deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/veterinary/treatments")
def create_veterinary_treatment(request: VeterinaryTreatmentRequest):
    """Create a new veterinary treatment"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO veterinary_treatments 
            (visit_id, animal_tag, treatment_date, diagnosis, treatment_description,
             medicines_used, dosage, duration_days, cost, vet_name, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            request.visit_id, request.animal_tag, request.treatment_date, request.diagnosis,
            request.treatment_description, request.medicines_used, request.dosage,
            request.duration_days, request.cost, request.vet_name, request.notes
        ))
        
        treatment_id = cursor.lastrowid
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Treatment created successfully",
            "data": {"id": treatment_id}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/veterinary/treatments")
def get_veterinary_treatments(animal_tag: str = None, limit: int = 100):
    """Get all veterinary treatments or filter by animal tag"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if animal_tag:
            cursor.execute("""
                SELECT id, visit_id, animal_tag, treatment_date, diagnosis, 
                       treatment_description, medicines_used, dosage, duration_days,
                       cost, vet_name, notes, created_at, updated_at
                FROM veterinary_treatments
                WHERE animal_tag = %s
                ORDER BY treatment_date DESC
                LIMIT %s
            """, (animal_tag, limit))
        else:
            cursor.execute("""
                SELECT id, visit_id, animal_tag, treatment_date, diagnosis,
                       treatment_description, medicines_used, dosage, duration_days,
                       cost, vet_name, notes, created_at, updated_at
                FROM veterinary_treatments
                ORDER BY treatment_date DESC
                LIMIT %s
            """, (limit,))
        
        treatments = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        result = []
        for treatment in treatments:
            result.append({
                "id": treatment[0],
                "visit_id": treatment[1],
                "animal_tag": treatment[2],
                "treatment_date": str(treatment[3]),
                "diagnosis": treatment[4],
                "treatment_description": treatment[5],
                "medicines_used": treatment[6],
                "dosage": treatment[7],
                "duration_days": treatment[8],
                "cost": float(treatment[9]) if treatment[9] else 0.0,
                "vet_name": treatment[10],
                "notes": treatment[11],
                "created_at": str(treatment[12]),
                "updated_at": str(treatment[13])
            })
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/veterinary/treatments/{treatment_id}")
def delete_veterinary_treatment(treatment_id: int):
    """Delete a veterinary treatment"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM veterinary_treatments WHERE id = %s", (treatment_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Treatment deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/veterinary/medical-history")
def create_medical_history(request: MedicalHistoryRequest):
    """Create a new medical history record"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO medical_history_detailed 
            (animal_tag, animal_name, date, record_type, disease_name, diagnosis,
             treatment, medicines_used, vet_name, cost, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            request.animal_tag, request.animal_name, request.date, request.record_type,
            request.disease_name, request.diagnosis, request.treatment, request.medicines_used,
            request.vet_name, request.cost, request.notes
        ))
        
        history_id = cursor.lastrowid
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Medical history record created successfully",
            "data": {"id": history_id}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/veterinary/medical-history")
def get_medical_history(animal_tag: str = None, limit: int = 100):
    """Get medical history records"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if animal_tag:
            cursor.execute("""
                SELECT id, animal_tag, animal_name, date, record_type, disease_name,
                       diagnosis, treatment, medicines_used, vet_name, cost, notes,
                       created_at, updated_at
                FROM medical_history_detailed
                WHERE animal_tag = %s
                ORDER BY date DESC
                LIMIT %s
            """, (animal_tag, limit))
        else:
            cursor.execute("""
                SELECT id, animal_tag, animal_name, date, record_type, disease_name,
                       diagnosis, treatment, medicines_used, vet_name, cost, notes,
                       created_at, updated_at
                FROM medical_history_detailed
                ORDER BY date DESC
                LIMIT %s
            """, (limit,))
        
        records = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        result = []
        for record in records:
            result.append({
                "id": record[0],
                "animal_tag": record[1],
                "animal_name": record[2],
                "date": str(record[3]),
                "record_type": record[4],
                "disease_name": record[5],
                "diagnosis": record[6],
                "treatment": record[7],
                "medicines_used": record[8],
                "vet_name": record[9],
                "cost": float(record[10]) if record[10] else 0.0,
                "notes": record[11],
                "created_at": str(record[12]),
                "updated_at": str(record[13])
            })
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/veterinary/medical-history/{history_id}")
def delete_medical_history(history_id: int):
    """Delete a medical history record"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM medical_history_detailed WHERE id = %s", (history_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Medical history record deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/veterinary/vaccination-schedule")
def create_vaccination_schedule(request: VaccinationScheduleRequest):
    """Create a new vaccination schedule"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO vaccination_schedule 
            (animal_tag, animal_name, vaccine_name, scheduled_date, completed,
             completion_date, vet_name, cost, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            request.animal_tag, request.animal_name, request.vaccine_name, request.scheduled_date,
            request.completed, request.completion_date, request.vet_name, request.cost, request.notes
        ))
        
        schedule_id = cursor.lastrowid
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Vaccination schedule created successfully",
            "data": {"id": schedule_id}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/veterinary/vaccination-schedule")
def get_vaccination_schedules(animal_tag: str = None, upcoming: bool = False):
    """Get vaccination schedules"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if animal_tag and upcoming:
            cursor.execute("""
                SELECT id, animal_tag, animal_name, vaccine_name, scheduled_date,
                       completed, completion_date, vet_name, cost, notes, reminder_sent,
                       created_at, updated_at
                FROM vaccination_schedule
                WHERE animal_tag = %s AND completed = FALSE AND scheduled_date >= CURDATE()
                ORDER BY scheduled_date ASC
            """, (animal_tag,))
        elif animal_tag:
            cursor.execute("""
                SELECT id, animal_tag, animal_name, vaccine_name, scheduled_date,
                       completed, completion_date, vet_name, cost, notes, reminder_sent,
                       created_at, updated_at
                FROM vaccination_schedule
                WHERE animal_tag = %s
                ORDER BY scheduled_date DESC
            """, (animal_tag,))
        elif upcoming:
            cursor.execute("""
                SELECT id, animal_tag, animal_name, vaccine_name, scheduled_date,
                       completed, completion_date, vet_name, cost, notes, reminder_sent,
                       created_at, updated_at
                FROM vaccination_schedule
                WHERE completed = FALSE AND scheduled_date >= CURDATE()
                ORDER BY scheduled_date ASC
            """)
        else:
            cursor.execute("""
                SELECT id, animal_tag, animal_name, vaccine_name, scheduled_date,
                       completed, completion_date, vet_name, cost, notes, reminder_sent,
                       created_at, updated_at
                FROM vaccination_schedule
                ORDER BY scheduled_date DESC
                LIMIT 100
            """)
        
        schedules = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        result = []
        for schedule in schedules:
            result.append({
                "id": schedule[0],
                "animal_tag": schedule[1],
                "animal_name": schedule[2],
                "vaccine_name": schedule[3],
                "scheduled_date": str(schedule[4]),
                "completed": bool(schedule[5]),
                "completion_date": str(schedule[6]) if schedule[6] else None,
                "vet_name": schedule[7],
                "cost": float(schedule[8]) if schedule[8] else 0.0,
                "notes": schedule[9],
                "reminder_sent": bool(schedule[10]),
                "created_at": str(schedule[11]),
                "updated_at": str(schedule[12])
            })
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.put("/veterinary/vaccination-schedule/{schedule_id}")
def update_vaccination_schedule(schedule_id: int, request: VaccinationScheduleRequest):
    """Update a vaccination schedule"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE vaccination_schedule
            SET animal_tag = %s, animal_name = %s, vaccine_name = %s, scheduled_date = %s,
                completed = %s, completion_date = %s, vet_name = %s, cost = %s, notes = %s
            WHERE id = %s
        """, (
            request.animal_tag, request.animal_name, request.vaccine_name, request.scheduled_date,
            request.completed, request.completion_date, request.vet_name, request.cost,
            request.notes, schedule_id
        ))
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Vaccination schedule updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/veterinary/vaccination-schedule/{schedule_id}")
def delete_vaccination_schedule(schedule_id: int):
    """Delete a vaccination schedule"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM vaccination_schedule WHERE id = %s", (schedule_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Vaccination schedule deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/veterinary/diseases")
def get_common_diseases():
    """Get list of common diseases"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, disease_name, category, symptoms, common_treatment, 
                   prevention, severity
            FROM common_diseases
            ORDER BY disease_name
        """)
        
        diseases = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        result = []
        for disease in diseases:
            result.append({
                "id": disease[0],
                "disease_name": disease[1],
                "category": disease[2],
                "symptoms": disease[3],
                "common_treatment": disease[4],
                "prevention": disease[5],
                "severity": disease[6]
            })
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/veterinary/summary")
def get_veterinary_summary(animal_tag: str = None):
    """Get veterinary summary statistics"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Total visits
        if animal_tag:
            cursor.execute("SELECT COUNT(*) FROM veterinary_visits WHERE animal_tag = %s", (animal_tag,))
        else:
            cursor.execute("SELECT COUNT(*) FROM veterinary_visits")
        total_visits = cursor.fetchone()[0]
        
        # Total cost
        if animal_tag:
            cursor.execute("SELECT SUM(cost) FROM veterinary_visits WHERE animal_tag = %s", (animal_tag,))
        else:
            cursor.execute("SELECT SUM(cost) FROM veterinary_visits")
        total_cost = cursor.fetchone()[0] or 0
        
        # Upcoming vaccinations
        if animal_tag:
            cursor.execute("""
                SELECT COUNT(*) FROM vaccination_schedule 
                WHERE animal_tag = %s AND completed = FALSE AND scheduled_date >= CURDATE()
            """, (animal_tag,))
        else:
            cursor.execute("""
                SELECT COUNT(*) FROM vaccination_schedule 
                WHERE completed = FALSE AND scheduled_date >= CURDATE()
            """)
        upcoming_vaccinations = cursor.fetchone()[0]
        
        # Recent visits (last 30 days)
        if animal_tag:
            cursor.execute("""
                SELECT COUNT(*) FROM veterinary_visits 
                WHERE animal_tag = %s AND visit_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            """, (animal_tag,))
        else:
            cursor.execute("""
                SELECT COUNT(*) FROM veterinary_visits 
                WHERE visit_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            """)
        recent_visits = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": {
                "total_visits": total_visits,
                "total_cost": float(total_cost),
                "upcoming_vaccinations": upcoming_vaccinations,
                "recent_visits": recent_visits
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/veterinary/reports/upload")
async def upload_veterinary_report(
    animal_tag: str = Form(...),
    report_date: str = Form(...),
    report_type: str = Form(None),
    description: str = Form(None),
    visit_id: int = Form(None),
    file: UploadFile = File(...)
):
    """Upload a veterinary report/document"""
    try:
        # Create directory for veterinary reports
        report_dir = f"uploads/veterinary_reports/{animal_tag}"
        os.makedirs(report_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1]
        filename = f"{animal_tag}_{timestamp}{file_extension}"
        file_path = os.path.join(report_dir, filename)
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Save to database
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO veterinary_reports 
            (visit_id, animal_tag, report_date, report_type, file_path, file_name, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (visit_id, animal_tag, report_date, report_type, file_path, file.filename, description))
        
        report_id = cursor.lastrowid
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Report uploaded successfully",
            "data": {
                "id": report_id,
                "file_path": file_path,
                "file_name": file.filename
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/veterinary/reports")
def get_veterinary_reports(animal_tag: str = None, visit_id: int = None):
    """Get veterinary reports"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if visit_id:
            cursor.execute("""
                SELECT id, visit_id, animal_tag, report_date, report_type, 
                       file_path, file_name, description, uploaded_at
                FROM veterinary_reports
                WHERE visit_id = %s
                ORDER BY report_date DESC
            """, (visit_id,))
        elif animal_tag:
            cursor.execute("""
                SELECT id, visit_id, animal_tag, report_date, report_type,
                       file_path, file_name, description, uploaded_at
                FROM veterinary_reports
                WHERE animal_tag = %s
                ORDER BY report_date DESC
            """, (animal_tag,))
        else:
            cursor.execute("""
                SELECT id, visit_id, animal_tag, report_date, report_type,
                       file_path, file_name, description, uploaded_at
                FROM veterinary_reports
                ORDER BY report_date DESC
                LIMIT 100
            """)
        
        reports = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        result = []
        for report in reports:
            result.append({
                "id": report[0],
                "visit_id": report[1],
                "animal_tag": report[2],
                "report_date": str(report[3]),
                "report_type": report[4],
                "file_path": report[5],
                "file_name": report[6],
                "description": report[7],
                "uploaded_at": str(report[8])
            })
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ==================== CALENDAR API ENDPOINTS ====================

class CalendarEventRequest(BaseModel):
    title: str
    event_type: str  # Vaccination, Breeding, Vet Visit, Order, Labour
    event_date: str
    event_time: Optional[str] = None
    end_date: Optional[str] = None
    end_time: Optional[str] = None
    notes: Optional[str] = None
    related_animals: Optional[str] = None  # Comma-separated tag numbers
    assigned_person: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = "Scheduled"  # Scheduled, In Progress, Completed, Cancelled
    color: Optional[str] = None
    email_reminder: Optional[int] = None  # Hours before event
    sms_reminder: Optional[int] = None  # Hours before event


class EventReminderRequest(BaseModel):
    reminder_type: str  # Email, SMS
    reminder_time: str  # Datetime string
    sent: Optional[bool] = False


class RecurringEventRequest(BaseModel):
    recurrence_pattern: str  # Daily, Weekly, Monthly, Yearly
    recurrence_interval: Optional[int] = 1
    recurrence_end_date: Optional[str] = None
    recurrence_count: Optional[int] = None


@app.post("/calendar/events")
def create_calendar_event(request: CalendarEventRequest):
    """Create a new calendar event"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO farm_events 
            (title, event_type, event_date, event_time, end_date, end_time, notes, 
             related_animals, assigned_person, location, status, color) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (request.title, request.event_type, request.event_date, request.event_time,
             request.end_date, request.end_time, request.notes, request.related_animals,
             request.assigned_person, request.location, request.status, request.color)
        )
        
        event_id = cursor.lastrowid
        
        # Add reminders if specified (calculate reminder datetime)
        from datetime import datetime, timedelta
        
        if request.email_reminder:
            event_datetime = datetime.strptime(f"{request.event_date} {request.event_time or '00:00:00'}", "%Y-%m-%d %H:%M:%S")
            reminder_dt = event_datetime - timedelta(hours=request.email_reminder)
            cursor.execute(
                """INSERT INTO event_reminders (event_id, reminder_type, reminder_time)
                VALUES (%s, 'Email', %s)""",
                (event_id, reminder_dt.strftime("%Y-%m-%d %H:%M:%S"))
            )
        
        if request.sms_reminder:
            event_datetime = datetime.strptime(f"{request.event_date} {request.event_time or '00:00:00'}", "%Y-%m-%d %H:%M:%S")
            reminder_dt = event_datetime - timedelta(hours=request.sms_reminder)
            cursor.execute(
                """INSERT INTO event_reminders (event_id, reminder_type, reminder_time)
                VALUES (%s, 'SMS', %s)""",
                (event_id, reminder_dt.strftime("%Y-%m-%d %H:%M:%S"))
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Event created successfully",
            "event_id": event_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/calendar/events")
def get_calendar_events(
    start_date: str = None,
    end_date: str = None,
    event_type: str = None,
    status: str = None,
    animal_tag: str = None,
    limit: int = 100
):
    """Get calendar events with optional filters"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM farm_events WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND event_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND event_date <= %s"
            params.append(end_date)
        
        if event_type:
            query += " AND event_type = %s"
            params.append(event_type)
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        if animal_tag:
            query += " AND (related_animals LIKE %s OR related_animals = %s)"
            params.append(f"%{animal_tag}%")
            params.append(animal_tag)
        
        query += " ORDER BY event_date DESC, event_time DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        events = cursor.fetchall()
        
        result = []
        for event in events:
            # Get reminders for this event
            cursor.execute(
                """SELECT reminder_type, reminder_time, sent 
                FROM event_reminders WHERE event_id = %s""",
                (event[0],)
            )
            reminders = cursor.fetchall()
            
            event_data = {
                "id": event[0],
                "title": event[1],
                "event_type": event[2],
                "event_date": str(event[3]),
                "event_time": str(event[4]) if event[4] else None,
                "end_date": str(event[5]) if event[5] else None,
                "end_time": str(event[6]) if event[6] else None,
                "all_day": bool(event[7]) if event[7] is not None else False,
                "related_animals": event[8],
                "assigned_person": event[9],
                "location": event[10],
                "notes": event[11],
                "status": event[12],
                "color": event[13],
                "created_at": str(event[17]),
                "updated_at": str(event[18]),
                "reminders": [
                    {
                        "type": r[0],
                        "reminder_time": str(r[1]),
                        "sent": bool(r[2])
                    } for r in reminders
                ]
            }
            result.append(event_data)
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/calendar/events/{event_id}")
def get_calendar_event(event_id: int):
    """Get a specific calendar event by ID"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM farm_events WHERE id = %s", (event_id,))
        event = cursor.fetchone()
        
        if not event:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Get reminders
        cursor.execute(
            """SELECT reminder_type, reminder_time, sent 
            FROM event_reminders WHERE event_id = %s""",
            (event_id,)
        )
        reminders = cursor.fetchall()
        
        # Get recurring pattern if exists
        cursor.execute(
            """SELECT recurrence_type, recurrence_interval, recurrence_end_date, recurrence_count
            FROM recurring_events WHERE event_id = %s""",
            (event_id,)
        )
        recurring = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        event_data = {
            "id": event[0],
            "title": event[1],
            "event_type": event[2],
            "event_date": str(event[3]),
            "event_time": str(event[4]) if event[4] else None,
            "end_date": str(event[5]) if event[5] else None,
            "end_time": str(event[6]) if event[6] else None,
            "all_day": bool(event[7]) if event[7] is not None else False,
            "related_animals": event[8],
            "assigned_person": event[9],
            "location": event[10],
            "notes": event[11],
            "status": event[12],
            "color": event[13],
            "created_at": str(event[17]),
            "updated_at": str(event[18]),
            "reminders": [
                {
                    "type": r[0],
                    "reminder_time": str(r[1]),
                    "sent": bool(r[2])
                } for r in reminders
            ]
        }
        
        if recurring:
            event_data["recurring"] = {
                "pattern": recurring[0],
                "interval": recurring[1],
                "end_date": str(recurring[2]) if recurring[2] else None,
                "count": recurring[3]
            }
        
        return {
            "status": "success",
            "data": event_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.put("/calendar/events/{event_id}")
def update_calendar_event(event_id: int, request: CalendarEventRequest):
    """Update a calendar event"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if event exists
        cursor.execute("SELECT id FROM farm_events WHERE id = %s", (event_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Event not found")
        
        cursor.execute(
            """UPDATE farm_events 
            SET title = %s, event_type = %s, event_date = %s, event_time = %s,
                end_date = %s, end_time = %s, notes = %s, related_animals = %s,
                assigned_person = %s, location = %s, status = %s, color = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s""",
            (request.title, request.event_type, request.event_date, request.event_time,
             request.end_date, request.end_time, request.notes, request.related_animals,
             request.assigned_person, request.location, request.status, request.color, event_id)
        )
        
        # Update reminders - delete existing and add new
        cursor.execute("DELETE FROM event_reminders WHERE event_id = %s", (event_id,))
        
        from datetime import datetime, timedelta
        
        if request.email_reminder:
            event_datetime = datetime.strptime(f"{request.event_date} {request.event_time or '00:00:00'}", "%Y-%m-%d %H:%M:%S")
            reminder_dt = event_datetime - timedelta(hours=request.email_reminder)
            cursor.execute(
                """INSERT INTO event_reminders (event_id, reminder_type, reminder_time)
                VALUES (%s, 'Email', %s)""",
                (event_id, reminder_dt.strftime("%Y-%m-%d %H:%M:%S"))
            )
        
        if request.sms_reminder:
            event_datetime = datetime.strptime(f"{request.event_date} {request.event_time or '00:00:00'}", "%Y-%m-%d %H:%M:%S")
            reminder_dt = event_datetime - timedelta(hours=request.sms_reminder)
            cursor.execute(
                """INSERT INTO event_reminders (event_id, reminder_type, reminder_time)
                VALUES (%s, 'SMS', %s)""",
                (event_id, reminder_dt.strftime("%Y-%m-%d %H:%M:%S"))
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Event updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete("/calendar/events/{event_id}")
def delete_calendar_event(event_id: int):
    """Delete a calendar event"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if event exists
        cursor.execute("SELECT id FROM farm_events WHERE id = %s", (event_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Delete reminders first (foreign key constraint)
        cursor.execute("DELETE FROM event_reminders WHERE event_id = %s", (event_id,))
        
        # Delete recurring pattern if exists
        cursor.execute("DELETE FROM recurring_events WHERE event_id = %s", (event_id,))
        
        # Delete attachments if exists
        cursor.execute("DELETE FROM event_attachments WHERE event_id = %s", (event_id,))
        
        # Delete event
        cursor.execute("DELETE FROM farm_events WHERE id = %s", (event_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": "Event deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.put("/calendar/events/{event_id}/status")
def update_event_status(event_id: int, status: str):
    """Update event status (Scheduled, In Progress, Completed, Cancelled)"""
    try:
        valid_statuses = ["Scheduled", "In Progress", "Completed", "Cancelled"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """UPDATE farm_events SET status = %s, updated_at = CURRENT_TIMESTAMP 
            WHERE id = %s""",
            (status, event_id)
        )
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Event not found")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "message": f"Event status updated to {status}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/calendar/upcoming")
def get_upcoming_events(days: int = 7, limit: int = 20):
    """Get upcoming events for the next N days"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT * FROM farm_events 
            WHERE event_date >= CURDATE() 
            AND event_date <= DATE_ADD(CURDATE(), INTERVAL %s DAY)
            AND status != 'Cancelled'
            ORDER BY event_date ASC, event_time ASC
            LIMIT %s""",
            (days, limit)
        )
        
        events = cursor.fetchall()
        
        result = []
        for event in events:
            result.append({
                "id": event[0],
                "title": event[1],
                "event_type": event[2],
                "event_date": str(event[3]),
                "event_time": str(event[4]) if event[4] else None,
                "notes": event[11],
                "related_animals": event[8],
                "assigned_person": event[9],
                "status": event[12],
                "color": event[13]
            })
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/calendar/summary")
def get_calendar_summary():
    """Get calendar statistics and summary"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Total events
        cursor.execute("SELECT COUNT(*) FROM farm_events")
        total_events = cursor.fetchone()[0]
        
        # Events by status
        cursor.execute(
            """SELECT status, COUNT(*) as count 
            FROM farm_events 
            GROUP BY status"""
        )
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Events by type
        cursor.execute(
            """SELECT event_type, COUNT(*) as count 
            FROM farm_events 
            GROUP BY event_type"""
        )
        type_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Upcoming events (next 7 days)
        cursor.execute(
            """SELECT COUNT(*) FROM farm_events 
            WHERE event_date >= CURDATE() 
            AND event_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            AND status != 'Cancelled'"""
        )
        upcoming_count = cursor.fetchone()[0]
        
        # Overdue events
        cursor.execute(
            """SELECT COUNT(*) FROM farm_events 
            WHERE event_date < CURDATE() 
            AND status NOT IN ('Completed', 'Cancelled')"""
        )
        overdue_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": {
                "total_events": total_events,
                "status_breakdown": status_counts,
                "type_breakdown": type_counts,
                "upcoming_7_days": upcoming_count,
                "overdue": overdue_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ===================== DASHBOARD ENDPOINTS =====================

@app.get("/dashboard/stats/{email}")
def get_dashboard_stats(email: str):
    """Get comprehensive dashboard statistics"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verify user exists
        cursor.execute("SELECT farm_name FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        farm_name = user[0]
        
        # Get total animals count
        cursor.execute(
            "SELECT COUNT(*) FROM cattles WHERE (is_archived = FALSE OR is_archived IS NULL) AND user_email = %s",
            (email,)
        )
        total_animals = cursor.fetchone()[0]
        
        # Get today's production
        from datetime import date, timedelta
        today = date.today().strftime("%Y-%m-%d")
        cursor.execute(
            """SELECT SUM(p.quantity) as total 
               FROM production_entries p
               JOIN cattles c ON p.cattle_id = c.id
               WHERE p.entry_date = %s AND c.user_email = %s""",
            (today, email)
        )
        production_result = cursor.fetchone()
        today_production = float(production_result[0]) if production_result and production_result[0] else 0
        
        # Get current month's income
        current_month = date.today().strftime("%Y-%m")
        cursor.execute(
            """SELECT COALESCE(SUM(amount), 0) 
            FROM financial_entries 
            WHERE user_email = %s AND entry_type = 'income' 
            AND DATE_FORMAT(date, '%%Y-%%m') = %s""",
            (email, current_month)
        )
        monthly_income = float(cursor.fetchone()[0])
        
        # Get production trend for last 7 days
        production_trend = []
        for i in range(6, -1, -1):
            target_date = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
            cursor.execute(
                """SELECT COALESCE(SUM(p.quantity), 0) 
                   FROM production_entries p
                   JOIN cattles c ON p.cattle_id = c.id
                   WHERE p.entry_date = %s AND c.user_email = %s""",
                (target_date, email)
            )
            daily_prod = float(cursor.fetchone()[0])
            production_trend.append({
                "date": target_date,
                "quantity": daily_prod
            })
        
        # Get expense vs income for current month (by day)
        cursor.execute(
            """SELECT date, entry_type, SUM(amount) as total
            FROM financial_entries
            WHERE user_email = %s AND DATE_FORMAT(date, '%%Y-%%m') = %s
            GROUP BY date, entry_type
            ORDER BY date ASC""",
            (email, current_month)
        )
        finance_data = cursor.fetchall()
        
        # Get farm health score (based on production and animal condition)
        # For now, we'll calculate based on production consistency
        cursor.execute(
            """SELECT COUNT(DISTINCT p.entry_date) 
               FROM production_entries p
               JOIN cattles c ON p.cattle_id = c.id
               WHERE p.entry_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND c.user_email = %s""",
            (email,)
        )
        active_days = cursor.fetchone()[0]
        health_score = min(100, int((active_days / 7) * 100))
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": {
                "farm_name": farm_name,
                "total_animals": total_animals,
                "today_production": today_production,
                "monthly_income": monthly_income,
                "production_trend": production_trend,
                "finance_data": [
                    {
                        "date": str(row[0]),
                        "type": row[1],
                        "amount": float(row[2])
                    } for row in finance_data
                ],
                "farm_health": health_score
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
