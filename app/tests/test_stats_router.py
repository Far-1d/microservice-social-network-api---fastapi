import requests
import json
import pytest
import uuid

user_emails = ["test.1001@gmail.com", "test.1002@gmail.com", "test.1003@gmail.com"]
user_password = "123456"
access_key = ''
deleted_post_id = ''

def get_access_key(user:int = 0):
    user_login_url = 'http://127.0.0.1:8000/api/users/login'
    response = requests.post(
        user_login_url,
        data={
            "login_identifier": user_emails[user],
            "password": user_password
        }
    )

    if response.status_code == 200:
        data = response.json()
        global access_key
        access_key = data['access']
        return data['user']['id']


@pytest.fixture
def create_post(client):
    get_access_key()

    data = {
        'caption': 'This is a test post',
        'tags': json.dumps(['one', 'two']),
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    image_path = "tests/test.jpg"
    files = {
        'file': ('test.jpg', open(image_path, 'rb'), 'image/jpg')
    }

    client.post(
        "/api/posts/",
        data=data,
        files=files,
        headers=headers
    )

def test_stats_valid(client, create_post):
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.get(
        f'api/stats/',
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 200
    assert res_data['posts'] == 1, 'user must have a post'
    assert set(res_data.keys()).issubset(('posts', 'views', 'likes', 'comments', 'bookmarks'))


def test_stats_no_authentication(client):
    response = client.get(
        f'api/stats/'
    )

    res_data = response.json()

    assert response.status_code == 401
    assert res_data['detail'] == 'Not authenticated'
