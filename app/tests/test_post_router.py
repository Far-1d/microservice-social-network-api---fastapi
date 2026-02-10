import requests
import json
import pytest
import uuid
from unittest.mock import patch


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

def test_get_empty_list_posts(client):
    response = client.get("/api/posts/")
    data = response.json()
    # assert status code
    assert response.status_code == 200
    # assert return list
    assert isinstance(data, list)
    # assert empty return
    assert data == []

# post can be created ✅
def test_create_post_valid(client):
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

    response = client.post(
        "/api/posts/",
        data=data,
        files=files,
        headers=headers
    )
    res_data = response.json()

    # assert status code
    assert response.status_code == 200
    # assert response data, caption
    assert res_data['caption'] == data['caption']
    # assert response data, tag length
    assert len(res_data['tags']) == 2
    # assert response data, tag name
    assert res_data['tags'][0]['name'] in data['tags']

# post can not be created ❌
def test_create_post_no_caption(client):
    data = {
        'tags': json.dumps(['one', 'two']),
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    image_path = "tests/test.jpg"
    files = {
        'file': ('test.jpg', open(image_path, 'rb'), 'image/jpg')
    }

    response = client.post(
        "/api/posts/",
        data=data,
        files=files,
        headers=headers
    )
    
    # assert status code
    assert response.status_code == 422, "missing caption field"

# post ✅
def test_create_post_no_tag(client):
    data = {
        'caption': 'This is a test post',
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    image_path = "tests/test.jpg"
    files = {
        'file': ('test.jpg', open(image_path, 'rb'), 'image/jpg')
    }

    response = client.post(
        "/api/posts/",
        data=data,
        files=files,
        headers=headers
    )
    res_data = response.json()

    # assert status code
    assert response.status_code == 200
    # assert response data, caption
    assert res_data['caption'] == data['caption']
    # assert response data, tag length
    assert len(res_data['tags']) == 0

# post ✅
def test_create_post_with_extra_data_field(client):
    data = {
        'caption': 'This is a test post',
        'tags': json.dumps(['three']),
        'extra_field': 'this is extra',
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    image_path = "tests/test.jpg"
    files = {
        'file': ('test.jpg', open(image_path, 'rb'), 'image/jpg')
    }

    response = client.post(
        "/api/posts/",
        data=data,
        files=files,
        headers=headers
    )
    res_data = response.json()

    # assert status code
    assert response.status_code == 200
    # assert response data, caption
    assert res_data['caption'] == data['caption']
    # assert response data, tag length
    assert len(res_data['tags']) == 1
    # assert response data, tag name
    assert res_data['tags'][0]['name'] in data['tags']

# post ✅
def test_create_post_with_whitespace_data(client):
    data = {
        'caption': ' ',
        'tags': json.dumps([' ', '  ']),
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    image_path = "tests/test.jpg"
    files = {
        'file': ('test.jpg', open(image_path, 'rb'), 'image/jpg')
    }

    response = client.post(
        "/api/posts/",
        data=data,
        files=files,
        headers=headers
    )
    res_data = response.json()

    # assert status code
    assert response.status_code == 200
    # assert response data, caption
    assert res_data['caption'] == data['caption'].strip(), "empty caption"
    # assert response data, tag length
    assert len(res_data['tags']) == 0, "no tag is added"

def test_create_post_without_authorization(client):
    data = {
        'caption': 'This is a test post',
        'tags': json.dumps(['one', 'two']),
    }

    image_path = "tests/test.jpg"
    files = {
        'file': ('test.jpg', open(image_path, 'rb'), 'image/jpg')
    }

    response = client.post(
        "/api/posts/",
        data=data,
        files=files,
    )
    res_data = response.json()

    # assert status code
    assert response.status_code == 401

def test_create_post_wrong_authorization(client):
    data = {
        'caption': 'This is a test post',
        'tags': json.dumps(['one', 'two']),
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}+123",
    }

    image_path = "tests/test.jpg"
    files = {
        'file': ('test.jpg', open(image_path, 'rb'), 'image/jpg')
    }

    response = client.post(
        "/api/posts/",
        data=data,
        files=files,
        headers=headers
    )
    res_data = response.json()

    # assert status code
    assert response.status_code == 401, "Unauthorized"

# post ❌
def test_create_post_without_file(client):
    data = {
        'caption': 'This is a test post',
        'tags': json.dumps(['one', 'two']),
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.post(
        "/api/posts/",
        data=data,
        headers=headers
    )
    res_data = response.json()

    # assert status code
    assert response.status_code == 422, "file is required"

# post ❌
def test_create_post_with_bad_file_format(client):

    data = {
        'caption': 'This is a test post',
        'tags': json.dumps(['one', 'two']),
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    image_path = "tests/test.pdf"
    files = {
        'file': ('test.pdf', open(image_path, 'rb'), 'application/pdf')
    }

    response = client.post(
        "/api/posts/",
        data=data,
        files=files,
        headers=headers
    )
    res_data = response.json()

    # assert status code
    assert response.status_code == 400
    assert res_data['detail'].startswith('File type not allowed')

# post ❌
def test_create_post_with_valid_file_but_bad_format(client):

    data = {
        'caption': 'This is a test post',
        'tags': json.dumps(['one', 'two']),
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    image_path = "tests/test.jpg"
    files = {
        'file': ('test.jpg', open(image_path, 'rb'), 'application/pdf')
    }

    response = client.post(
        "/api/posts/",
        data=data,
        files=files,
        headers=headers
    )
    res_data = response.json()

    # assert status code
    assert response.status_code == 400
    assert res_data['detail'].startswith('File type not allowed')

# post ✅
def test_create_post_with_video_file(client):

    data = {
        'caption': 'This is a test post',
        'tags': json.dumps(['four']),
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    image_path = "tests/test.mp4"
    files = {
        'file': ('test.mp4', open(image_path, 'rb'), 'video/mp4')
    }

    response = client.post(
        "/api/posts/",
        data=data,
        files=files,
        headers=headers
    )
    res_data = response.json()

    # assert status code
    assert response.status_code == 200
    # assert response data, caption
    assert res_data['caption'] == data['caption']

# post ❌
def test_create_post_with_oversized_file(client):

    data = {
        'caption': 'This is a test post',
        'tags': json.dumps(['one', 'two']),
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    image_path = "tests/test-over10Mb.jpg"
    files = {
        'file': ('test.jpg', open(image_path, 'rb'), 'image/jpg')
    }

    response = client.post(
        "/api/posts/",
        data=data,
        files=files,
        headers=headers
    )
    res_data = response.json()

    # assert status code
    assert response.status_code == 400
    assert res_data['detail'].startswith('File size exceeds')


def test_create_post_notification(client):
    # before this test make sure:
    # - user 2 is following user 1
    # - user 3 is not following user 1
    # do it in djnago service
    import threading
    import time

    url = "http://localhost:8001/notifications"

    user2_events = []
    user3_events = []
    stop_listening = threading.Event()

    def listen_sse(user_idx, event_list):
        """Listen to SSE events in background thread"""
        get_access_key(user_idx)
        headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Authorization": f"Bearer {access_key}"
        }
        try:
            with requests.get(url, headers=headers, stream=True, timeout=15) as response:
                assert response.status_code == 200
                
                for line in response.iter_lines(decode_unicode=True):
                    if stop_listening.is_set():
                        break
                    if line and line.startswith('data: '):
                        event_data = line[6:].strip()  # Remove 'data: ' prefix
                        event_list.append(event_data)
        except Exception as e:
            print(f"SSE error for user {user_idx+1}: {e}")
    
    # arg numbers are changed !!
    thread2 = threading.Thread(target=listen_sse, args=(2, user2_events), daemon=True)
    thread3 = threading.Thread(target=listen_sse, args=(1, user3_events), daemon=True)
    
    thread2.start()
    thread3.start()

    # don't lower the time or connections are made after the post is created
    time.sleep(5)
    
    # user 1 creates a post 
    get_access_key()
    data = {
        'caption': 'This is a SSE test post',
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    image_path = "tests/test.jpg"
    files = {
        'file': ('test.jpg', open(image_path, 'rb'), 'image/jpg')
    }

    response = client.post(
        "/api/posts/",
        data=data,
        files=files,
        headers=headers
    )
    assert response.status_code == 200

    post_id = response.json()['id']

    time.sleep(3)

    stop_listening.set()
    time.sleep(1)
    
    print(f"\nUser 2 events: {user2_events}")
    print(f"\nUser 3 events: {user3_events}")

    assert user3_events == [], "user 3 must have no notifications"
    assert len(user2_events) == 1, "user 2 must have 1 notification"

    event_data = json.loads(user2_events[0])
    assert event_data['type'] == 'new_post', f"Expected 'new_post', got {event_data['type']}"
    assert event_data['data']['post_id'] == post_id, "notification must be for the post created by user 1"


def test_get_list_posts(client):
    response = client.get("/api/posts/")
    data = response.json()
    # assert status code
    assert response.status_code == 200
    # assert return list
    assert len(data) == 6, "6 posts must be created by now"

def test_get_list_posts_with_authorization(client):
    headers = {
        "Authorization": f"Bearer {access_key}",
    }
    response = client.get("/api/posts/", headers=headers)
    data = response.json()
    # assert status code
    assert response.status_code == 200
    # assert return list
    assert len(data) == 0, "since all post are created by test user, none is shown"


def test_get_list_posts_with_unknown_query(client):
    response = client.get("/api/posts?unknown=true")
    data = response.json()
    # assert status code
    assert response.status_code == 200
    # assert return list
    assert len(data) == 6, "unknown query doesn't affect the result"

def test_get_list_posts_with_tag(client):
    response = client.get("/api/posts?tags=one")
    data = response.json()
    # assert status code
    assert response.status_code == 200
    # assert return list
    assert len(data) == 1

def test_get_list_posts_with_tags(client):
    response = client.get("/api/posts?tags=two,three,four")
    data = response.json()
    # assert status code
    assert response.status_code == 200
    # assert return list
    assert len(data) == 3

def test_get_list_posts_with_tag_without_post(client):
    response = client.get("/api/posts?tags=five")
    data = response.json()
    # assert status code
    assert response.status_code == 200
    # assert return list
    assert len(data) == 0

def test_get_list_posts_with_wrong_tags(client):
    response = client.get("/api/posts?tags=two-three-five")
    data = response.json()
    # assert status code
    assert response.status_code == 200
    # assert return list
    assert len(data) == 0

@pytest.fixture
def create_post_for_other_users(client):
    for i in range(1,3):
        get_access_key(i)

        data = {
            'caption': f'This is a post from user {i}',
            'tags': json.dumps(['one', 'two']),
        }
        
        headers = {
            "Authorization": f"Bearer {access_key}",
        }

        image_path = "tests/test.jpg"
        files = {
            'file': ('test.jpg', open(image_path, 'rb'), 'image/jpg')
        }
        
        response = client.post(
            "/api/posts/",
            data=data,
            files=files,
            headers=headers
        )
        print('response stat = ', response.status_code)

def test_get_list_posts_with_user_id(client, create_post_for_other_users):
    user_id = get_access_key(1)
    response = client.get(f"/api/posts?user={user_id}")
    data = response.json()
    # assert status code
    assert response.status_code == 200
    # assert return list
    assert len(data) == 1

def test_get_list_posts_with_bad_user_id(client):
    user_id = 'abcd'
    response = client.get(f"/api/posts?user={user_id}")
    data = response.json()
    # assert status code
    assert response.status_code == 400
    # assert detail
    assert data['detail'] == 'Invalid user id'

def test_get_list_posts_with_unknown_user_id(client):
    # change some chars
    user_id = uuid.uuid4()

    response = client.get(f"/api/posts?user={user_id}")
    data = response.json()
    # assert status code
    assert response.status_code == 200
    # assert data
    assert data == []

def test_get_post_with_valid_id(client):
    # find an id
    response = client.get("/api/posts/")
    data = response.json()
    post_id = data[0]['id']
    caption = data[0]['caption']

    # testing the id
    response = client.get(f"/api/posts/{post_id}/")
    data = response.json()

    assert response.status_code == 200
    assert data['id'] == post_id
    assert data['caption'] == caption

def test_get_post_with_invalid_id(client):
    # find an id
    response = client.get("/api/posts/")
    data = response.json()
    # change some chars
    post_id = data[0]['id'][:-2]+'ab'

    # testing the id
    response = client.get(f"/api/posts/{post_id}/")

    assert response.status_code == 404

def test_get_post_with_bad_id_format(client):
    post_id = '1234'

    response = client.get(f"/api/posts/{post_id}/")
    data = response.json()
    assert response.status_code == 400
    assert data['detail'] == 'Invalid post id'

@pytest.fixture
def delete_post(client):
    get_access_key()
    headers = {
        'Authorization': f'Bearer {access_key}'
    }

    response = client.get("/api/posts/")
    data = response.json()
    
    for post in data:
        if post['caption'] == '':
            response = client.delete(f'/api/posts/{post['id']}', headers=headers)
            if response.status_code == 204:
                global deleted_post_id
                deleted_post_id = post['id']
                print(f'post {post['id']} deleted')

            break

def test_get_post_deleted_post(client, delete_post):
    response = client.get(f"/api/posts/{deleted_post_id}/")
    assert response.status_code == 404, "must return not found"


def test_post_update_valid(client):
    # get post id
    response = client.get("/api/posts/")
    post_id = response.json()[0]['id']

    # updating
    get_access_key()
    data = {
        'caption': 'updated caption',
        'tags': ['one', 'two', 'zero']
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }
    response = client.patch(
        f"/api/posts/{post_id}",
        json=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 200
    assert res_data['caption'] == 'updated caption', "caption must be updated"
    assert all([tag['name'] in ['one', 'two', 'zero'] for tag in res_data['tags']])

def test_post_update_only_tags(client):
    # get post id
    response = client.get("/api/posts/")
    post_id = response.json()[0]['id']

    # updating
    data = {
        'tags': ['onetwo']
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }
    response = client.patch(
        f"/api/posts/{post_id}",
        json=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 200
    assert all([tag['name'] in ['onetwo'] for tag in res_data['tags']])

def test_post_update_only_caption(client):
    # get post id
    response = client.get("/api/posts/")
    post_id = response.json()[0]['id']

    # updating
    data = {
        'caption': 'updated caption',
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }
    response = client.patch(
        f"/api/posts/{post_id}",
        json=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 200
    assert res_data['caption'] == 'updated caption', "caption must be updated"

def test_post_update_wrong_post_id(client):
    # random id
    post_id = uuid.uuid4()

    # updating
    data = {
        'caption': 'updated caption',
        'tags': ['one', 'two', 'zero']
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }
    response = client.patch(
        f"/api/posts/{post_id}",
        json=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 404

def test_post_update_bad_post_id_format(client):
    # bad id
    post_id = 'abc'

    # updating
    data = {
        'caption': 'updated caption',
        'tags': ['one', 'two', 'zero']
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }
    response = client.patch(
        f"/api/posts/{post_id}",
        json=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 400
    assert response.json()['detail'] == 'Invalid post id'

def test_post_update_no_authentication(client):
    # get post id
    response = client.get("/api/posts/")
    post_id = response.json()[0]['id']

    # updating
    data = {
        'caption': 'updated caption',
        'tags': ['one', 'two', 'zero']
    }
    response = client.patch(
        f"/api/posts/{post_id}",
        json=data,
    )

    res_data = response.json()

    assert response.status_code == 401
    assert res_data['detail'] == 'Not authenticated'

def test_post_update_unauthorized(client):
    # get post id
    response = client.get("/api/posts/")
    post_id = response.json()[0]['id']

    # updating
    get_access_key(1)
    data = {
        'caption': 'updated caption',
        'tags': ['one', 'two', 'zero']
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }
    response = client.patch(
        f"/api/posts/{post_id}",
        json=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 403
    assert res_data['detail'] == 'Not allowed'

def test_post_update_deleted_post(client):
    # updating
    get_access_key()
    data = {
        'caption': 'updated caption',
        'tags': ['one', 'two', 'zero']
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }
    response = client.patch(
        f"/api/posts/{deleted_post_id}",
        json=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 404
    assert res_data['detail'] == 'Post not found'


def test_post_delete(client):
    response = client.get("/api/posts/")
    post_id = response.json()[0]['id']

    # updating
    get_access_key()
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.delete(
        f'api/posts/{post_id}',
        headers=headers
    )

    assert response.status_code == 204

def test_post_delete_already_deleted(client):
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.delete(
        f'api/posts/{deleted_post_id}',
        headers=headers
    )

    res_data = response.json()
    assert response.status_code == 404
    assert res_data['detail'] == 'Post not found'

def test_post_delete_unauthorized(client):
    response = client.get("/api/posts/")
    post_id = response.json()[0]['id']

    get_access_key(1)
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.delete(
        f'api/posts/{post_id}',
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 403
    assert res_data['detail'] == 'Not allowed'

def test_post_delete_wrong_post_id(client):
    post_id = uuid.uuid4()

    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.delete(
        f'api/posts/{post_id}',
        headers=headers
    )

    res_data = response.json()
    assert response.status_code == 404
    assert res_data['detail'] == 'Post not found'

def test_post_delete_bad_post_id_format(client):
    post_id = '123abc'
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.delete(
        f'api/posts/{post_id}',
        headers=headers
    )

    res_data = response.json()
    assert response.status_code == 400
    assert res_data['detail'] == 'Invalid post id'


def test_post_media(client):
    response = client.get("/api/posts/")
    post_id = response.json()[0]['id']

    # every user can access media
    get_access_key()
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.get(
        f'api/posts/{post_id}/media/',
        headers=headers
    )
    content_type = response.headers.get('Content-Type')

    assert response.status_code == 200
    assert content_type.startswith(('image/', 'video/')), \
        f"Expected image/* or video/*, got {content_type}"
    assert len(response.content) > 0, "Media file is empty"

def test_post_media_wrong_id(client):
    post_id = uuid.uuid4()

    # every user can access media
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.get(
        f'api/posts/{post_id}/media/',
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 404
    assert res_data['detail'] == 'Post not found'

def test_post_media_bad_format_id(client):
    post_id = '123abc'

    # every user can access media
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.get(
        f'api/posts/{post_id}/media/',
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 400
    assert res_data['detail'] == 'Invalid post id'

def test_post_media_no_authentication(client):
    response = client.get("/api/posts/")
    post_id = response.json()[0]['id']

    response = client.get(
        f'api/posts/{post_id}/media/',
    )

    res_data = response.json()

    assert response.status_code == 401
    assert res_data['detail'] == 'Not authenticated'

def test_post_media_deleted_post(client):
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.get(
        f'api/posts/{deleted_post_id}/media/',
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 404
    assert res_data['detail'] == 'Post not found'

