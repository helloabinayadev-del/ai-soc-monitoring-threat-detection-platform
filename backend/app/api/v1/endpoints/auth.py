from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional
from jose import jwt, JWTError

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserStatusUpdate, UserPasswordReset, Token, TokenData
from app.core.rbac import require_roles
from app.services.audit_service import audit_service

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated. Contact SOC Administrator."
        )
    return user

@router.post("/register", response_model=UserResponse)
def register(
    user_in: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SOC_ADMIN", "Admin"]))
):
    db_user = db.query(User).filter(User.username == user_in.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_email = db.query(User).filter(User.email == user_in.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pwd = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_pwd,
        full_name=user_in.full_name,
        role=user_in.role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    audit_service.record_action(
        db=db,
        actor_username=current_user.username,
        action="USER_CREATE",
        resource_type="User",
        resource_id=str(new_user.id),
        status="SUCCESS",
        details=f"Created user '{new_user.username}' with role '{new_user.role}'"
    )

    return new_user

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        audit_service.record_action(
            db=db,
            actor_username=form_data.username or "anonymous",
            action="LOGIN_FAILED",
            resource_type="User",
            status="FAILED",
            details="Invalid username or password"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        audit_service.record_action(
            db=db,
            actor_username=user.username,
            action="LOGIN_BLOCKED",
            resource_type="User",
            status="DENIED",
            details="Login attempt blocked for deactivated account"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated. Contact SOC Administrator."
        )

    user.last_login = datetime.now(timezone.utc)
    db.commit()

    audit_service.record_action(
        db=db,
        actor_username=user.username,
        action="LOGIN_SUCCESS",
        resource_type="User",
        resource_id=str(user.id),
        status="SUCCESS",
        details=f"User logged in successfully with role '{user.role}'"
    )

    access_token = create_access_token(subject=user.username, role=user.role)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# =========================================================
# USER MANAGEMENT ENDPOINTS (SOC_ADMIN ONLY)
# =========================================================

@router.get("/users", response_model=List[UserResponse])
def list_users(
    search: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SOC_ADMIN", "Admin"]))
):
    query = db.query(User)
    if search:
        s = f"%{search}%"
        query = query.filter((User.username.like(s)) | (User.email.like(s)) | (User.full_name.like(s)))
    if role and role != "ALL":
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.order_by(User.id.asc()).all()

@router.post("/users", response_model=UserResponse)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SOC_ADMIN", "Admin"]))
):
    return register(user_in=user_in, db=db, current_user=current_user)

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SOC_ADMIN", "Admin"]))
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    old_role = target.role
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(target, field, value)
    
    db.commit()
    db.refresh(target)

    audit_service.record_action(
        db=db,
        actor_username=current_user.username,
        action="USER_UPDATE",
        resource_type="User",
        resource_id=str(target.id),
        status="SUCCESS",
        details=f"Updated user '{target.username}' profile/role. Role changed from '{old_role}' to '{target.role}'"
    )

    return target

@router.put("/users/{user_id}/status", response_model=UserResponse)
def toggle_user_status(
    user_id: int,
    status_update: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SOC_ADMIN", "Admin"]))
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    if target.id == current_user.id and not status_update.is_active:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own active admin account")

    target.is_active = status_update.is_active
    db.commit()
    db.refresh(target)

    action_label = "USER_ACTIVATE" if target.is_active else "USER_DEACTIVATE"
    audit_service.record_action(
        db=db,
        actor_username=current_user.username,
        action=action_label,
        resource_type="User",
        resource_id=str(target.id),
        status="SUCCESS",
        details=f"Account status for '{target.username}' set to is_active={target.is_active}"
    )

    return target

@router.put("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    pwd_in: UserPasswordReset,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["SOC_ADMIN", "Admin"]))
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    if not pwd_in.new_password or len(pwd_in.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    target.hashed_password = get_password_hash(pwd_in.new_password)
    db.commit()

    audit_service.record_action(
        db=db,
        actor_username=current_user.username,
        action="PASSWORD_RESET",
        resource_type="User",
        resource_id=str(target.id),
        status="SUCCESS",
        details=f"Password for user '{target.username}' reset by Admin '{current_user.username}'"
    )

    return {"status": "SUCCESS", "message": f"Password reset successfully for user '{target.username}'"}
