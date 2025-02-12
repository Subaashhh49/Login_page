from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uuid
from datetime import datetime, timedelta
from passlib.context import CryptContext

# FastAPI setup
app = FastAPI()

# Templates (HTML)
templates = Jinja2Templates(directory="templates")

# Database setup 
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create user model 
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# Create database tables
Base.metadata.create_all(bind=engine)

# Token store 
reset_tokens = {}

# Hash password
def hash_password(password: str):
    return pwd_context.hash(password)

# Verify password
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Register Page (HTML Form)
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Register Route (User registration)
@app.post("/register")
async def register(username: str, email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered.")
    
    hashed_password = hash_password(password)
    new_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully."}

# Login Page (HTML Form)
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Login Route
@app.post("/login")
async def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password.")
    return {"message": "Login successful."}

# Password Reset Page (HTML Form)
@app.get("/reset_password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request})

# Password Reset Route
@app.post("/reset_password")
async def reset_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Email not found.")
    reset_token = str(uuid.uuid4())
    reset_tokens[reset_token] = {"email": email, "expires_at": datetime.utcnow() + timedelta(hours=1)}
    return {"message": f"Password reset requested. Use this token to reset your password: {reset_token}"}

# Set New Password Page (HTML Form)
@app.get("/set_new_password/{token}", response_class=HTMLResponse)
async def set_new_password_page(request: Request, token: str):
    return templates.TemplateResponse("set_new_password.html", {"request": request, "token": token})

# Set New Password Route
@app.post("/set_new_password/{token}")
async def set_new_password(token: str, new_password: str, db: Session = Depends(get_db)):
    token_info = reset_tokens.get(token)
    if not token_info or datetime.utcnow() > token_info["expires_at"]:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")
    user = db.query(User).filter(User.email == token_info["email"]).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found.")
    user.hashed_password = hash_password(new_password)
    db.commit()
    del reset_tokens[token]
    return {"message": "Password updated successfully."}
