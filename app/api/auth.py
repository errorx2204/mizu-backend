from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from app.database import get_db
from app.models.user import User
from app.models.budget import Budget
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_user(db: Session, user: UserCreate):
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create default EXPENSE budgets for new user
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
    
    # Create default INCOME budgets (goals) for new user
    default_income_budgets = [
        {"category": "Salary", "amount": 50000},
        {"category": "Investment", "amount": 10000},
        {"category": "Other", "amount": 5000},
    ]
    
    for budget_data in default_expense_budgets:
        db_budget = Budget(
            user_id=db_user.id,
            category=budget_data["category"],
            amount=budget_data["amount"]
        )
        db.add(db_budget)
    
    for budget_data in default_income_budgets:
        db_budget = Budget(
            user_id=db_user.id,
            category=budget_data["category"],
            amount=budget_data["amount"]
        )
        db.add(db_budget)
    
    db.commit()
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)

@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": db_user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": db_user.id,
        "name": db_user.name,
        "email": db_user.email
    }

@router.get("/me", response_model=UserResponse)
def get_current_user(db: Session = Depends(get_db)):
    # In production, get user from JWT token
    # For now, return first user
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
