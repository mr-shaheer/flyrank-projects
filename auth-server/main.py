from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from supabase_auth.errors import AuthApiError
from supabase_client import auth_client

from typing import Optional


app = FastAPI()
security = HTTPBearer()

# Models
class AuthRequest(BaseModel):
    email: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# Root
@app.get("/")
def root():
    return {"message": "Server running and connected to Supabase"}


# Public Route
@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


# Auth
@app.post("/auth/signup", status_code=201)
def signup(data: AuthRequest):
    if not data.email or not data.password:
        raise HTTPException(
            status_code = 400,
            detail = {"error": "Email and password required"}
        )

    try:
        response = auth_client.auth.sign_up({
            "email": data.email,
            "password": data.password
        })

        if response.user is None:
            raise HTTPException(
                status_code = 400,
                detail = {"error": "Signup failed"}
            )

        return {
            "message": "User created successfully",
            "user": {
                "id": response.user.id,
                "email": response.user.email
            }
        }

    except AuthApiError as e:
        raise HTTPException(
            status_code = 400,
            detail = {"error": str(e)}
        )


@app.post("/auth/login")
def login(data: AuthRequest):
    if not data.email or not data.password:
        raise HTTPException(
            status_code = 400,
            detail = {"error": "Email and password required"}
        )

    try:
        response = auth_client.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "expires_in": response.session.expires_in,
            "token_type": "Bearer"
        }

    except AuthApiError:
        raise HTTPException(
            status_code = 401,
            detail = {"error": "Invalid login credentials"}
        )


# Dependency
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if not credentials:
        raise HTTPException(
            status_code = 401,
            detail = {"error": "Access token required"}
        )

    token = credentials.credentials

    try:
        response = auth_client.auth.get_user(jwt=token)

        if response.user is None:
            raise HTTPException(
                status_code = 401,
                detail = {"error": "Invalid or expired token"}
            )

        return response.user

    except Exception:
        raise HTTPException(
            status_code = 401,
            detail = {"error": "Invalid or expired token"}
        )


# Protected Route
@app.get("/protected/profile")
def protected_profile(user = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email
    }


# Logout
@app.post("/auth/logout", status_code = 204)
def logout(user = Depends(get_current_user)):
    auth_client.auth.sign_out()
    return


# Refresh Token (Optional but good)
@app.post("/auth/refresh")
def refresh_token(data: RefreshTokenRequest):
    try:
        response = auth_client.auth.refresh_session({
            "refresh_token": data.refresh_token
        })

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "expires_in": response.session.expires_in
        }

    except Exception:
        raise HTTPException(
            status_code = 401,
            detail = {"error": "Invalid refresh token"}
        )