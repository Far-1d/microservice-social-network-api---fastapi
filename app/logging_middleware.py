import time, uuid, os, jwt
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import structlog
from app.logging import get_logger
from app.metrics import(
    response_time,
    response_codes
)

logger = get_logger("http")

SIGNING_KEY = os.environ.get("JWT_SECRET")
ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")

def extract_user_id(request: Request) -> str | None:
    """Extract user_id from JWT token in request headers."""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        payload = jwt.decode(
            token,
            SIGNING_KEY,
            algorithms=[ALGORITHM],
            options={"verify_signature": True, "verify_exp": True}
        )
        return payload.get("user_id")
    
    except Exception:
        # Don't raise - middleware should never block a request
        return None


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every request with:
    - Who:  IP address + authenticated user (if any)
    - What: Method, path, status code
    - When: Human-readable timestamp + duration
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate a unique request ID for tracing errors
        request_id = str(uuid.uuid4())[:8]

        # Extract who is making the request
        client_ip = self._get_client_ip(request)
        user_id = extract_user_id(request)

        # Bind context so all logs within this request share these fields
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            ip=client_ip,
            user_id=user_id or "anonymous",
            method=request.method,
            path=request.url.path,
        )

        start_time = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response

        except Exception as exc:
            logger.error(
                "request_failed",
                error=str(exc),
                exc_info=True,
            )
            raise

        finally:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            
            if request.url.path not in ("/metrics", "/health"):
                response_time.labels(endpoint=request.url.path).observe(duration_ms)
                response_codes.labels(status_code=str(status_code)).inc()
            
                log_fn = logger.warning if status_code >= 400 else logger.info
                log_fn(
                    "request_finished",
                    status_code=status_code,
                    duration_ms=duration_ms,
                    query_params=str(request.query_params) or None,
                )

    def _get_client_ip(self, request: Request) -> str:
        # Respect X-Forwarded-For for requests behind a proxy/nginx
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def _get_user_id(self, request: Request) -> str | None:
        """
        Try to extract user_id from request state.
        Your auth middleware should set request.state.user_id after verifying the token.
        """
        return getattr(request.state, "user_id", None)
