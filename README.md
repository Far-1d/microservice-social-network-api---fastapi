# Social Network API (FastApi)

A FastAPI-based microservice for social media post management, handling posts, likes, comments, and bookmarks.

---

## 🚀 Features

- **Post Management**: Create, read, update, and delete posts
- **Interactions**: Likes, comments, and bookmarks
- **Tag System**: Categorize posts with hashtags
- **File Uploads**: Support for images and videos
- **Soft Delete**: Safe deletion with recovery option
- **JWT Authentication**: Secure API endpoints

---

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (shared with Django user service)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Authentication**: JWT
- **File Handling**: Python's shutil + aiofiles

---

## Prerequisites

Before setting up the project, ensure you have the following installed and configured on your development machine:

- Python 3.10+
- PostgreSQL 14+
- Running Django User Service (for user data)

---
## Getting Started

### Running the Development Server

1. **Clone and setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Configure environment**
rename .env.example to .env and file the arguments with proper value;
values are equal with those from django service's drf-simplejwt config.


3. **Database setup**
```bash
# Run migrations
alembic upgrade head

# Or create tables directly
python -c "from app.db.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

4. **Run the server**
```bash
uvicorn app.main:app --reload --port 8001
```

---

## Integration with Django Service

### This service relies on a Django service for:

- User authentication (JWT validation)
- User profile information
- Follow/block relationships
- User existence validation

---

## Testing & Feedback

You are encouraged to test the API thoroughly and help improve it by reporting any bugs or issues you encounter.

Please send your feedback or bug reports via:

- **Email:** farid.zarie.000@gmail.com
- **Telegram:** [@el_fredoo](https://t.me/el_fredoo)

Your contributions and feedback are highly appreciated!


---

Thank you for using the Social Network API project!


