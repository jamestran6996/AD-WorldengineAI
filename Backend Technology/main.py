from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from ldap3 import Server, Connection, NTLM, Tls
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

import ssl

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT configuration
SECRET_KEY = "NZuwjM14eMQaoeTsDoMrnr9vky0sktYab1h8IbrqPMo"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# HTTPBearer to authenticate token
oauth2_scheme = HTTPBearer()

# Models
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    role: str

# Login and authenticate AD
@app.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    tls_config = Tls(validate=ssl.CERT_NONE)  # no internal CA

    server = Server("dc.worldengine.ai", port=389, use_ssl=False, tls=tls_config)

    bind_user = "worldengine\\svc-adbind"
    bind_password = "World@engine1005"

    try:
        # Connect AD
        conn = Connection(server, user=bind_user, password=bind_password, authentication=NTLM)
        conn.open()
        conn.start_tls()
        conn.bind()

        # Find user DN
        conn.search(
            search_base="dc=worldengine,dc=ai",
            search_filter=f"(sAMAccountName={request.username})",
            attributes=["distinguishedName"]
        )

        if not conn.entries:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        user_dn = conn.entries[0].distinguishedName.value

        # Bind by sAMAccountName
        user_sam = f"worldengine\\{request.username}"
        user_conn = Connection(server, user=user_sam, password=request.password, authentication=NTLM)
        user_conn.open()
        user_conn.start_tls()
        user_conn.bind()

        if not user_conn.bound:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # Filter role by OU
        role = "admin" if "OU=admin" in user_dn else "user"

        # Create JWT
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": request.username,
            "role": role,
            "exp": expire
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        return TokenResponse(access_token=token, token_type="bearer")

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid username or password")

# Middleware for token
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> User:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return User(username=username, role=role)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Route protected
@app.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "role": current_user.role,
        "message": f"Welcome {current_user.username}, you have access as {current_user.role}"
    }

# Logout
@app.post("/logout")
def logout():
    return {"message": "Logged out successfully"}

# Route for admin
@app.get("/admin-only")
def admin_only(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied: Admins only")
    return {"message": f"Welcome admin {current_user.username}"}
