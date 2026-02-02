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
rename .env.example to .env and fill the arguments with proper value;
values are equal with those from django service's drf-simplejwt config.


3. **Docker setup**
kafka and redis are required in order to start the fastapi server
```bash
# Start docker compose
docker compose -f ./kafka.docker-compose.yml up
```
the kafka server might take around a minute to initiate 

3.5 **Django Server**
this app communicates with the django app for user authentications and informations;
go to the django directory and use this command 
```bash
# Start kafka consumer on django 
python manage.py kafka_consumer --settings=settings.settings.dev
```
this is different from the main django server and its only purpose is to communicate 
with fastapi


4. **Run the server**
```bash
cd app

uvicorn main:app --reload --port 8001
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


