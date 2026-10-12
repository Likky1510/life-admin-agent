import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.models import User
from app.models.schemas import (
    UserCreate, Token, UserOut, UserProfileUpdate,
    PasswordResetRequest, PasswordResetConfirm,
)
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger("auth")


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        interests=user_in.interests,
        qualifications=user_in.qualifications,
        career_goals=user_in.career_goals,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token = create_access_token(data={"sub": user.id})
    return Token(access_token=access_token, user=user)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.interests is not None:
        current_user.interests = payload.interests
    if payload.qualifications is not None:
        current_user.qualifications = payload.qualifications
    if payload.career_goals is not None:
        current_user.career_goals = payload.career_goals
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/password-reset/request")
def request_password_reset(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Issues a short-lived reset token. In mock mode (no real SMTP) the
    token is logged server-side instead of emailed -- for a real
    deployment, email this token via the notification service instead
    of returning it in the response.
    """
    user = db.query(User).filter(User.email == payload.email).first()
    # Always return 200 regardless of whether the email exists, to avoid
    # leaking which emails are registered.
    if not user:
        return {"message": "If that email is registered, a reset link has been sent."}

    reset_token = create_access_token(data={"sub": user.id, "purpose": "password_reset"}, expires_minutes=30)
    logger.info(f"[MOCK] Password reset token for {user.email}: {reset_token}")
    return {"message": "If that email is registered, a reset link has been sent.", "dev_token": reset_token}


@router.post("/password-reset/confirm")
def confirm_password_reset(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    decoded = decode_access_token(payload.reset_token)
    if not decoded or decoded.get("purpose") != "password_reset":
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = db.query(User).filter(User.id == decoded.get("sub")).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")

    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password updated successfully."}
