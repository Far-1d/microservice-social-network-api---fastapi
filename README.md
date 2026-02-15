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
- **Database**: Sqlite3
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Authentication**: JWT
- **File Handling**: Python's shutil
- **Testing: Pytest

---

## Prerequisites

Before setting up the project, ensure you have the following installed and configured on your development machine:

- Python 3.13+
- Running Django User Service (for user data) 
- Running kafka server and redis client
---
## Getting Started

### Running the Development Server

1. **Configure environment**
rename .env.example to .env and fill the arguments with proper value;
values are equal with those from django service's drf-simplejwt config.
also for kafka and redis usrls use those from docker-compose.tml file.

2. **Docker setup**
docker-compose.yml file is not shiped with this repo because the directory structure 
requires it to be in the parent folder and with have multiple docker compose and .env 
files, i think it is better to use another repo for it. 

go to [microservice-social-network-api--docker](https://github.com/Far-1d/microservice-social-network-api---docker) to see all the details

not that you can't run this app alone but you need kafka and redis running to use this app,
either to start the server or test it.

3. **Django Server**
this app communicates with the django app for user authentications and informations;
with containerizing the apps, you don't need extra commands to run the django server;
just start the docker compose and you are ready to go.


4. **Logs and Metrics**
all logs and metrics are captured and used in grafana using loki, promtail and prometheus.
the logs and metrics are started from a different docker compose file in case you don't 
need it. 

for more info go to [microservice-social-network-api--monitoring](https://github.com/Far-1d/microservice-social-network-api---monitoring)

---

## Integration with Django Service

### This service relies on a Django service for:

- User authentication (JWT validation)
- User Account information
- Follow/block relationships
- User existence validation

these communications are achieved both with redis pubsub and kafka's producer and consumer.
---

## Test
Tests have been written to ensure safe usage with mock db sessions and separate configurations.
to start testing:
- make sure pytest is installed either from the requirements.txt file or 
```bash
pip install pytest
```
- start pytest
```bash
pytest
```

- in case there are failures in notifications tests, most of the time increasing the sleep time
fixes the failure.

---

## Feedback

You are encouraged to test the API thoroughly and help improve it by reporting any bugs or issues you encounter.

Please send your feedback or bug reports via:

- **Email:** farid.zarie.000@gmail.com
- **Telegram:** [@el_fredoo](https://t.me/el_fredoo)

Your contributions and feedback are highly appreciated!


---

Thank you for using the Social Network API project!


