from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt
from app.database import supabase
import traceback

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserCreate(BaseModel):
    email: str
    name: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: str

def hash_password(password: str) -> str:
    import hashlib
    import secrets
    salt = secrets.token_hex(16)
    pwdhash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwdhash}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt, stored_hash = hashed_password.split("$")
        import hashlib
        pwdhash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
        return pwdhash == stored_hash
    except:
        return False

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate):
    print(f"DEBUG: Register called with email={user.email}, name={user.name}")
    
    try:
        existing = supabase.table("users").select("*").eq("email", user.email).execute()
        print(f"DEBUG: Existing users: {existing.data}")
        
        if existing.data:
            print("DEBUG: Email already exists")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = hash_password(user.password)
        print(f"DEBUG: Password hashed")
        
        result = supabase.table("users").insert({
            "email": user.email,
            "name": user.name,
            "hashed_password": hashed_password
        }).select().execute()
        
        print(f"DEBUG: Insert result: {result.data}")
        
        if not result.data or len(result.data) == 0:
            print("DEBUG: Insert returned no data!")
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        db_user = result.data[0]
        user_id = db_user["id"]
        print(f"DEBUG: User created with id={user_id}")
        
        default_expense_budgets = [
            {"category": "Food", "amount": 5000},
            {"category": "Transport", "amount": 3000},
            {"category": "Shopping", "amount": 10000},
            {"category": "Entertainment", "amount": 2000},
            {"category": "Bills", "amount": 5000},
            {"category": "Health", "amount": 2000},
            {"category": "Education", "amount": 3000},
            {"category": "Other", "amount": 2000},
        ]
        
        default_income_budgets = [
            {"category": "Salary", "amount": 50000},
            {"category": "Investment", "amount": 10000},
            {"category": "Other", "amount": 5000},
        ]
        
        for budget_data in default_expense_budgets:
            supabase.table("budgets").insert({
                "user_id": user_id,
                "category": budget_data["category"],
                "amount": budget_data["amount"]
            }).execute()
        
        for budget_data in default_income_budgets:
            supabase.table("budgets").insert({
                "user_id": user_id,
                "category": budget_data["category"],
                "amount": budget_data["amount"]
            }).execute()
        
        print("DEBUG: Budgets created successfully")
        
        return {
            "id": db_user["id"],
            "email": db_user["email"],
            "name": db_user["name"],
            "created_at": db_user.get("created_at", "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.post("/login")
def login(user: LoginRequest):
    print(f"DEBUG: Login called with email={user.email}")
    
    try:
        result = supabase.table("users").select("*").eq("email", user.email).execute()
        print(f"DEBUG: User query result: {result.data}")
        
        if not result.data:
            print("DEBUG: User not found")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        db_user = result.data[0]
        print(f"DEBUG: Found user, verifying password...")
        
        if not verify_password(user.password, db_user["hashed_password"]):
            print("DEBUG: Password verification failed")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        print("DEBUG: Password verified, creating token...")
        access_token = create_access_token(data={"sub": db_user["email"]})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": db_user["id"],
            "name": db_user["name"],
            "email": db_user["email"]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG ERROR in login: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.get("/me", response_model=UserResponse)
def get_current_user():
    try:
        user = supabase.table("users").select("*").limit(1).execute()
        if not user.data:
            raise HTTPException(status_code=404, detail="User not found")
        u = user.data[0]
        return {
            "id": u["id"],
            "email": u["email"],
            "name": u["name"],
            "created_at": u.get("created_at", "")
        }
    except Exception as e:
        print(f"DEBUG ERROR in get_current_user: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
