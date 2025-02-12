# User Authentication System

## Overview
This project is a **FastAPI-based user authentication system** that provides user registration, login, and password reset functionality. It uses **SQLite** as the database, **bcrypt** for password hashing, and **Jinja2** templates for rendering HTML pages.

## Features
- **User Registration**: Allows users to create an account with a username, email, and password.
- **User Login**: Validates user credentials and authenticates users.
- **Password Reset**: Generates a reset token and allows users to set a new password.
- **HTML Templates**: Provides user-friendly interfaces for authentication pages.

## Technologies Used
- **FastAPI**: A modern web framework for building APIs with Python.
- **SQLite**: Lightweight database for storing user credentials.
- **SQLAlchemy**: ORM for database interactions.
- **Jinja2**: Templating engine for rendering HTML.
- **Passlib (bcrypt)**: For secure password hashing.

## Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/auth-system.git
   cd auth-system
   ```
2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the FastAPI server**:
   ```bash
   uvicorn main:app --reload
   ```
5. **Access the application**:
   - API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - Web Interface: [http://127.0.0.1:8000/register](http://127.0.0.1:8000/register)

## API Endpoints
| Method | Endpoint                 | Description                        |
|--------|--------------------------|------------------------------------|
| GET    | `/register`              | Show registration form            |
| POST   | `/register`              | Register a new user               |
| GET    | `/login`                 | Show login form                   |
| POST   | `/login`                 | Authenticate user                  |
| GET    | `/reset_password`        | Show password reset form          |
| POST   | `/reset_password`        | Generate a password reset token   |
| GET    | `/set_new_password/{token}` | Show new password form            |
| POST   | `/set_new_password/{token}` | Set a new password for user       |

## License
This project is licensed under the **MIT License**.

