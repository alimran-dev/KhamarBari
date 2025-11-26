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
