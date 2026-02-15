from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from prometheus_fastapi_instrumentator import Instrumentator

# ─── Request Metrics (auto-handled by instrumentator) ────────────────────────
# These are exposed automatically:
#   http_requests_total           - total requests by method/path/status
#   http_request_duration_seconds - latency histogram by method/path

# ─── Business Metrics ─────────────────────────────────────────────────────────

posts_created_total = Counter(
    "posts_created_total",
    "Total number of posts created",
    ["user_id"],  # label: which user created it
)

posts_deleted_total = Counter(
    "posts_deleted_total",
    "Total number of posts deleted",
    ["user_id"],  # label: which user deleted it
)

posts_liked_total = Gauge(
    "posts_liked_total",
    "Total number of post likes",
)

post_views_total = Counter(
    "post_views_total",
    "Total number of post views",
)

comments_total = Counter(
    "comments_total",
    "Total number of comments",
)

bookmarks_total = Gauge(
    "bookmarks_total",
    "Total number of posts bookmarked",
)

# ─── Auth Metrics ─────────────────────────────────────────────────────────────

response_time = Histogram(
    "response_time",
    "Average response time by endpoint",
    ['endpoint'],
    unit='ms'
)

response_codes = Counter(
    "response_codes",
    "number of response codes",
    ['status_code'],
)

active_users = Gauge(
    "active_users_total",
    "Number of currently active users (rough estimate via recent requests)",
)

# ─── Notification Metrics ──────────────────────────────────────────────────────

notifications_sent_total = Counter(
    "notifications_sent_total",
    "Total SSE notifications sent",
    ["type"],  # label: 'new_post', 'new_comment', etc.
)

# ─── Setup Function ────────────────────────────────────────────────────────────

def setup_metrics(app):
    """
    Call this in main.py to expose /metrics endpoint.
    Automatically instruments all FastAPI routes.
    """
    Instrumentator(
        should_group_status_codes=False,
        excluded_handlers=["/metrics", "/health"],
    ).instrument(app).expose(app, endpoint="/metrics")
