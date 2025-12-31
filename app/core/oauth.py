import jwt
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

load_dotenv()

security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

SIMPLE_JWT = {
    'SIGNING_KEY': os.environ.get("JWT_SECRET"),
    'ALGORITHM': os.environ.get("JWT_ALGORITHM", "HS256"),
}

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(
            credentials.credentials,
            SIMPLE_JWT['SIGNING_KEY'],
            algorithms=[SIMPLE_JWT['ALGORITHM']],
            options={"verify_signature": True, "verify_exp": True}
        )

        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional)) -> str:
    if credentials is None:
        return None
    
    try:
        payload = jwt.decode(
            credentials.credentials,
            SIMPLE_JWT['SIGNING_KEY'],
            algorithms=[SIMPLE_JWT['ALGORITHM']],
            options={"verify_signature": True, "verify_exp": True}
        )

        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")