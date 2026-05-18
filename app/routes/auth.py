from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.user import User
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    
)


from app.schemas.user_schema import (
    UserCreate,
    UserLogin,
    RefreshTokenRequest,
    LogoutRequest
)
from app.models.session import Session

from app.models.session import Session 





router = APIRouter()


@router.post("/register")
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    # Check existing email
    existing_email = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Check existing username
    existing_username = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )

    # Hash Password
    hashed_password = hash_password(user.password)

    # Create User
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully"
    }

@router.post("/login")
def login_user(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    refresh_expiry = datetime.utcnow() + timedelta(days=7)

    # Find User
    db_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify Password
    is_valid = verify_password(
        user.password,
        db_user.hashed_password
    )

    if not is_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create Access Token
    access_token = create_access_token({
        "user_id": db_user.id,
        "email": db_user.email
    })

    # Create Refresh Token
    refresh_token = create_refresh_token()

    # Create Session
    new_session = Session(
    user_id=db_user.id,
    refresh_token=refresh_token,
    device_info="MacBook Chrome",
    expires_at=refresh_expiry
)

    db.add(new_session)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/profile")
def get_profile(
    current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }


@router.post("/refresh")
def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    
    Session.is_active == True

    # Find Session
    session = db.query(Session).filter(
        Session.refresh_token == request.refresh_token
    ).first()

    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    # Find User
    user = db.query(User).filter(
        User.id == session.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    # Create New Access Token
    new_access_token = create_access_token({
        "user_id": user.id,
        "email": user.email
    })

    # Create NEW Refresh Token
    new_refresh_token = create_refresh_token()

    # Rotate Refresh Token
    session.refresh_token = new_refresh_token

    db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout_user(
    request: LogoutRequest,
    db: Session = Depends(get_db)
):

    # Find Session
    session = db.query(Session).filter(
        Session.refresh_token == request.refresh_token
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    # Delete Session
    db.delete(session)

    db.commit()

    return {
        "message": "Logged out successfully"
    }


@router.get("/sessions")
def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    sessions = db.query(Session).filter(
        Session.user_id == current_user.id,
        Session.is_active == True
    ).all()

    return [
        {
            "session_id": session.id,
            "device": session.device_info,
            "created_at": session.created_at
        }
        for session in sessions
    ]


@router.delete("/sessions/{session_id}")
def revoke_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    session = db.query(Session).filter(
        Session.id == session_id,
        Session.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    session.is_active = False

    db.commit()

    return {
        "message": "Session revoked successfully"
    }

@router.delete("/sessions")
def revoke_all_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    sessions = db.query(Session).filter(
        Session.user_id == current_user.id
    ).all()

    for session in sessions:
        session.is_active = False

    db.commit()

    return {
        "message": "All sessions revoked"
    }

from app.core.redis import redis_client


@app.get("/redis-test")
def redis_test():

    redis_client.set("message", "Redis is working")

    value = redis_client.get("message")

    return {
        "redis_value": value
    }