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
    """
    Hash a password using bcrypt.
    
    Args:
    password (str): The plain text password.
    
    Returns:
    str: The hashed password.
    """
    return pwd_context.hash(password)

# Verify password
def verify_password(plain_password: str, hashed_password: str):
    """
    Verify a password against its hashed version.
    
    Args:
    plain_password (str): The plain text password.
    hashed_password (str): The hashed password to compare against.
    
    Returns:
    bool: True if passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

# Dependency to get DB session
def get_db():
    """
    Dependency function to get a database session.
    
    Yields:
    Session: The database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Register Page (HTML Form)
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """
    Serve the registration page.
    
    Args:
    request (Request): The request object.
    
    Returns:
    HTMLResponse: The rendered registration page.
    """
    return templates.TemplateResponse("register.html", {"request": request})

# Register Route (User registration)
@app.post("/register")
async def register(username: str, email: str, password: str, db: Session = Depends(get_db)):
    """
    Handle user registration.
    
    Args:
    username (str): The username for the new user.
    email (str): The email address for the new user.
    password (str): The password for the new user.
    db (Session): The database session.
    
    Returns:
    dict: A message indicating the registration result.
    """
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
    """
    Serve the login page.
    
    Args:
    request (Request): The request object.
    
    Returns:
    HTMLResponse: The rendered login page.
    """
    return templates.TemplateResponse("login.html", {"request": request})

# Login Route
@app.post("/login")
async def login(username: str, password: str, db: Session = Depends(get_db)):
    """
    Handle user login.
    
    Args:
    username (str): The username of the user trying to log in.
    password (str): The password of the user trying to log in.
    db (Session): The database session.
    
    Returns:
    dict: A message indicating the login result.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password.")
    return {"message": "Login successful."}

# Password Reset Page (HTML Form)
@app.get("/reset_password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    """
    Serve the password reset page.
    
    Args:
    request (Request): The request object.
    
    Returns:
    HTMLResponse: The rendered password reset page.
    """
    return templates.TemplateResponse("reset_password.html", {"request": request})

# Password Reset Route
@app.post("/reset_password")
async def reset_password(email: str, db: Session = Depends(get_db)):
    """
    Handle password reset request.
    
    Args:
    email (str): The email address of the user requesting password reset.
    db (Session): The database session.
    
    Returns:
    dict: A message containing the password reset token.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Email not found.")
    reset_token = str(uuid.uuid4())
    reset_tokens[reset_token] = {"email": email, "expires_at": datetime.utcnow() + timedelta(hours=1)}
    return {"message": f"Password reset requested. Use this token to reset your password: {reset_token}"}

# Set New Password Page (HTML Form)
@app.get("/set_new_password/{token}", response_class=HTMLResponse)
async def set_new_password_page(request: Request, token: str):
    """
    Serve the page to set a new password using the reset token.
    
    Args:
    request (Request): The request object.
    token (str): The reset token.
    
    Returns:
    HTMLResponse: The rendered page to set a new password.
    """
    return templates.TemplateResponse("set_new_password.html", {"request": request, "token": token})

# Set New Password Route
@app.post("/set_new_password/{token}")
async def set_new_password(token: str, new_password: str, db: Session = Depends(get_db)):
    """
    Set a new password using the reset token.
    
    Args:
    token (str): The reset token.
    new_password (str): The new password to set.
    db (Session): The database session.
    
    Returns:
    dict: A message indicating the result of the password update.
    """
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
