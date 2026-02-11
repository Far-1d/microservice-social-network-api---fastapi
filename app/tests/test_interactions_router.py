import json
import pytest
import requests
import uuid


user_emails = ["test.1001@gmail.com", "test.1002@gmail.com", "test.1003@gmail.com"]
user_password = "123456"
access_key = ''
deleted_post_id = ''
deleted_comment_id = ''

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


def test_like_toggle_valid(client, create_post):
    response = client.get('api/posts/')
    post_id = response.json()[0]['id']

    data = {
        'post_id': post_id
    }

    get_access_key()
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    # like
    response = client.post(
        f'api/interactions/likes',
        data=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 200
    assert res_data['value'] == 1

    # un-like
    response = client.post(
        f'api/interactions/likes',
        data=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 200
    assert res_data['value'] == 0

def test_like_not_existing_post(client):
    post_id = uuid.uuid4()

    data = {
        'post_id': post_id
    }

    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    # like
    response = client.post(
        f'api/interactions/likes',
        data=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 404
    assert res_data['detail'] == "Post not found"

def test_like_bad_format_post_id(client):
    post_id = 'abc'

    data = {
        'post_id': post_id
    }

    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    # like
    response = client.post(
        f'api/interactions/likes',
        data=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 400
    assert res_data['detail'] == "Invalid post id"

def test_like_post_no_authentication(client):
    response = client.get('api/posts/')
    post_id = response.json()[0]['id']

    data = {
        'post_id': post_id
    }

    # like
    response = client.post(
        f'api/interactions/likes',
        data=data
    )

    res_data = response.json()

    assert response.status_code == 401
    assert res_data['detail'] == "Not authenticated"

def test_like_post_no_post_id(client):
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    # like
    response = client.post(
        f'api/interactions/likes',
        headers=headers
    )

    assert response.status_code == 422, "incomplete or empty request body"

def test_like_post_wrong_request_body(client):
    data = {
        'post': uuid.uuid4()
    }

    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    # like
    response = client.post(
        f'api/interactions/likes',
        data=data,
        headers=headers
    )

    assert response.status_code == 422, "incomplete or empty request body"

# time consumer test
def test_like_notification(client):
    import threading
    import time

    url = "http://localhost:8001/notifications"

    author_events = []
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
    
    thread = threading.Thread(target=listen_sse, args=(0, author_events), daemon=True)
    thread.start()

    # don't lower the time or connections are made after the post is created
    time.sleep(5)
    
    # posts are created by user 1
    response = client.get('api/posts/')
    post_id = response.json()[0]['id']

    # user 2 likes user 1's post
    get_access_key(1)

    data = {
        'post_id': post_id,
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    # send request 3 times to have 2 likes (and 1 unlike)
    response = client.post(
        "/api/interactions/likes",
        data=data,
        headers=headers
    )
    assert response.status_code == 200
    
    time.sleep(1)
    response = client.post(
        "/api/interactions/likes",
        data=data,
        headers=headers
    )
    assert response.status_code == 200
    
    time.sleep(1)
    response = client.post(
        "/api/interactions/likes",
        data=data,
        headers=headers
    )
    assert response.status_code == 200

    time.sleep(3)

    stop_listening.set()
    time.sleep(1)
    
    print(f"\nAuthor events: {author_events}")
    # likes are cached for 24 hour (one like notification per day per post)
    assert len(author_events) == 1, "post author must have 1 notification"

    event_data = json.loads(author_events[0])
    assert event_data['type'] == 'post_liked', f"Expected 'post_liked', got {event_data['type']}"
    assert event_data['data']['post_id'] == post_id, "notification must be for the post created by user 1"


def test_user_likes_valid(client):
    response = client.get('api/posts/')
    post_id = response.json()[0]['id']

    data = {
        'post_id': post_id
    }

    get_access_key()
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    # like
    response = client.post(
        f'api/interactions/likes',
        data=data,
        headers=headers
    )

    # check user likes
    response = client.get(
        f'api/interactions/likes',
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 200
    assert res_data[0]['id'] == post_id

def test_user_likes_no_authentication(client):
    response = client.get(
        f'api/interactions/likes'
    )

    res_data = response.json()

    assert response.status_code == 401
    assert res_data['detail'] == 'Not authenticated'


# time consumer test
def test_comment_notification(client):
    import threading
    import time

    url = "http://localhost:8001/notifications"

    author_events = []
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
    
    thread = threading.Thread(target=listen_sse, args=(0, author_events), daemon=True)
    thread.start()

    # don't lower the time or connections are made after the post is created
    time.sleep(5)
    
    # posts are created by user 1
    response = client.get('api/posts/')
    post_id = response.json()[0]['id']

    # user 2 likes user 1's post
    get_access_key(1)

    data = {
        'post_id': post_id,
        'comment': 'this is a comment for testing notifications'
    }
    
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.post(
        "/api/interactions/comments",
        data=data,
        headers=headers
    )
    assert response.status_code == 200
    

    time.sleep(3)

    stop_listening.set()
    time.sleep(1)
    
    print(f"\nAuthor events: {author_events}")
    assert len(author_events) == 1, "post author must have 1 notification"

    event_data = json.loads(author_events[0])
    assert event_data['type'] == 'new_comment', f"Expected 'new_comment', got {event_data['type']}"
    assert event_data['data']['post_id'] == post_id, "notification must be for the post created by user 1"
    assert event_data['data']['comment'] == data['comment']

def test_create_comment_valid(client):
    response = client.get('api/posts/')
    post_id = response.json()[0]['id']

    data = {
        'post_id': post_id,
        'comment': 'this is a comment'
    }

    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.post(
        f'api/interactions/comments',
        data=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 200
    assert res_data['post_id'] == post_id
    assert res_data['content'] == data['comment']

def test_create_comment_incomplete_body(client):
    response = client.get('api/posts/')
    post_id = response.json()[0]['id']

    data1 = {
        'post_id': post_id,
    }
    data2 = {
        'comment': 'this is a comment'
    }

    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response_empty_body = client.post(
        f'api/interactions/comments',
        headers=headers
    )

    response_for_id = client.post(
        f'api/interactions/comments',
        data=data1,
        headers=headers
    )

    response_for_comment = client.post(
        f'api/interactions/comments',
        data=data2,
        headers=headers
    )


    assert response_empty_body.status_code == 422, "incomplete or empty request body"
    assert response_for_id.status_code == 422, "incomplete or empty request body"
    assert response_for_comment.status_code == 422, "incomplete or empty request body"

def test_create_comment_no_authentication(client):
    response = client.get('api/posts/')
    post_id = response.json()[0]['id']

    data = {
        'post_id': post_id,
        'comment': 'this is a comment'
    }

    response = client.post(
        f'api/interactions/comments',
        data=data,
    )

    res_data = response.json()

    assert response.status_code == 401
    assert res_data['detail'] == 'Not authenticated'

def test_create_comment_not_existing_post(client):
    data = {
        'post_id': uuid.uuid4(),
        'comment': 'this is a comment'
    }

    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.post(
        f'api/interactions/comments',
        data=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 404
    assert res_data['detail'] == 'Post not found'

def test_create_comment_bad_format_post_id(client):
    data = {
        'post_id': 'abc',
        'comment': 'this is a comment'
    }

    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.post(
        f'api/interactions/comments',
        data=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 400
    assert res_data['detail'] == 'Invalid post id'

def test_create_comment_empty_comment_and_id(client):
    response = client.get('api/posts/')
    post_id = response.json()[0]['id']

    data1 = {
        'post_id': post_id,
        'comment': ''
    }
    data2 = {
        'post_id': '',
        'comment': 'this is a comment'
    }
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response_empty_comment = client.post(
        f'api/interactions/comments',
        data=data1,
        headers=headers
    )
    response_empty_id = client.post(
        f'api/interactions/comments',
        data=data2,
        headers=headers
    )

    assert response_empty_comment.status_code == 422
    assert response_empty_id.status_code == 422

def test_create_comment_whitespace_comment(client):
    response = client.get('api/posts/')
    post_id = response.json()[0]['id']

    data = {
        'post_id': post_id,
        'comment': ' '
    }
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.post(
        f'api/interactions/comments',
        data=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 400
    assert res_data['detail'] == 'Invalid comment'


def test_list_comments_valid(client):
    response = client.get('api/posts/')
    post_id = response.json()[0]['id']

    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.get(
        f'api/interactions/comments/{post_id}',
        headers=headers
    )
    
    res_data = response.json()

    assert response.status_code == 200
    assert len(res_data) > 0
    assert res_data[0]['post_id'] == post_id

def test_list_comments_not_existing_post(client):
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.get(
        f'api/interactions/comments/{uuid.uuid4()}',
        headers=headers
    )
    
    res_data = response.json()

    assert response.status_code == 404
    assert res_data['detail'] == 'Post not found'

def test_list_comments_bad_format_post_id(client):
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.get(
        f'api/interactions/comments/{'abc'}',
        headers=headers
    )
    
    res_data = response.json()

    assert response.status_code == 400
    assert res_data['detail'] == 'Invalid post id'

def test_list_comments_no_authentication(client):
    response = client.get('api/posts/')
    post_id = response.json()[0]['id']

    response = client.get(
        f'api/interactions/comments/{post_id}',
    )
    
    res_data = response.json()

    assert response.status_code == 401
    assert res_data['detail'] == 'Not authenticated'

def test_list_comments_bad_authentication(client):
    response = client.get('api/posts/')
    post_id = response.json()[0]['id']

    headers = {
        "Authorization": f"Bearer {access_key}12ab",
    }

    response = client.get(
        f'api/interactions/comments/{post_id}',
        headers=headers
    )
    
    res_data = response.json()

    assert response.status_code == 401
    assert res_data['detail'] == 'Invalid token'

def test_user_comments_valid(client):
    headers = {
        "Authorization": f"Bearer {access_key}",
    }
    response = client.get(
        'api/interactions/comments', 
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 200
    assert isinstance(res_data, list)

def test_user_comments_no_authentication(client):
    response = client.get(
        'api/interactions/comments', 
    )

    res_data = response.json()

    assert response.status_code == 401
    assert res_data['detail'] == 'Not authenticated'

@pytest.fixture
def create_more_comments(client):
    response = client.get('api/posts/')
    post_id = response.json()[0]['id']

    headers = {
        "Authorization": f"Bearer {access_key}",
    }
    
    for i in range(3):
        data = {
            'post_id': post_id,
            'comment': f'this is comment {i}'
        }

        client.post(
            f'api/interactions/comments',
            data=data,
            headers=headers
        )

def test_delete_comment_valid(client, create_more_comments):
    headers = {
        "Authorization": f"Bearer {access_key}",
    }
    response = client.get(
        'api/interactions/comments', 
        headers=headers
    )
    comment_id = response.json()[0]['id']

    response = client.delete(
        f'api/interactions/comments/{comment_id}',
        headers=headers
    )

    # used in following tests
    global deleted_comment_id
    deleted_comment_id = comment_id

    assert response.status_code == 204

def test_delete_comment_not_existing_comment(client):
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.delete(
        f'api/interactions/comments/{uuid.uuid4()}',
        headers=headers
    )
    
    res_data = response.json()

    assert response.status_code == 404
    assert res_data['detail'] == 'Comment not found'

def test_delete_comment_already_deleted(client):
    headers = {
        "Authorization": f"Bearer {access_key}",
    }
    response = client.delete(
        f'api/interactions/comments/{deleted_comment_id}',
        headers=headers
    )
    
    res_data = response.json()

    assert response.status_code == 404
    assert res_data['detail'] == 'Comment not found'

def test_delete_comment_bad_format_id(client):
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.delete(
        f'api/interactions/comments/{'abcd1324'}',
        headers=headers
    )
    
    res_data = response.json()

    assert response.status_code == 400
    assert res_data['detail'] == 'Invalid comment id'

def test_delete_comment_no_authentication(client):
    headers = {
        "Authorization": f"Bearer {access_key}",
    }
    response = client.get(
        'api/interactions/comments', 
        headers=headers
    )
    comment_id = response.json()[0]['id']

    response = client.delete(
        f'api/interactions/comments/{comment_id}'
    )
    
    res_data = response.json()

    assert response.status_code == 401
    assert res_data['detail'] == 'Not authenticated'

def test_delete_comment_not_authorized(client):
    headers = {
        "Authorization": f"Bearer {access_key}",
    }
    response = client.get(
        'api/interactions/comments', 
        headers=headers
    )
    comment_id = response.json()[0]['id']

    get_access_key(2)
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.delete(
        f'api/interactions/comments/{comment_id}',
        headers=headers
    )
    
    res_data = response.json()

    assert response.status_code == 403
    assert res_data['detail'] == 'Not allowed'


def test_bookmark_toggle_valid(client):
    response = client.get('api/posts/')
    post_id = response.json()[0]['id']

    data = {
        'post_id': post_id
    }

    get_access_key()
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    # bookmark
    response = client.post(
        f'api/interactions/bookmarks',
        data=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 200
    assert res_data['value'] == 1

    # un-bookmark
    response = client.post(
        f'api/interactions/bookmarks',
        data=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 200
    assert res_data['value'] == 0

def test_bookmark_toggle_not_existing_post(client):
    data = {
        'post_id': uuid.uuid4()
    }

    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    response = client.post(
        f'api/interactions/bookmarks',
        data=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 404
    assert res_data['detail'] == 'Post not found'

def test_bookmark_toggle_bad_format_post_id(client):
    data = {
        'post_id': 'abcd1234'
    }

    get_access_key()
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    # bookmark
    response = client.post(
        f'api/interactions/bookmarks',
        data=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 400
    assert res_data['detail'] == 'Invalid post id'

def test_bookmark_toggle_empty_body(client):
    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    # bookmark
    response = client.post(
        f'api/interactions/bookmarks',
        headers=headers
    )

    assert response.status_code == 422

def test_bookmark_toggle_empty_post_id(client):
    data = {
        'post_id': ''
    }

    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    # bookmark
    response = client.post(
        f'api/interactions/bookmarks',
        data=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 422

def test_bookmark_toggle_whitespace_id(client):
    data = {
        'post_id': ' '
    }

    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    # bookmark
    response = client.post(
        f'api/interactions/bookmarks',
        data=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 400
    assert res_data['detail'] == 'Invalid post id'

def test_bookmark_toggle_not_authenticated(client):
    response = client.get('api/posts/')
    post_id = response.json()[0]['id']

    data = {
        'post_id': post_id
    }

    # bookmark
    response = client.post(
        f'api/interactions/bookmarks',
        data=data,
    )

    res_data = response.json()

    assert response.status_code == 401
    assert res_data['detail'] == 'Not authenticated'

def test_bookmark_toggle_bad_authentication(client):
    response = client.get('api/posts/')
    post_id = response.json()[0]['id']

    data = {
        'post_id': post_id
    }

    headers = {
        "Authorization": f"Bearer {access_key}ab12",
    }

    # bookmark
    response = client.post(
        f'api/interactions/bookmarks',
        data=data,
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 401
    assert res_data['detail'] == 'Invalid token'


def test_user_bookmarks_valid(client):
    response = client.get('api/posts/')
    post_id = response.json()[0]['id']

    data = {
        'post_id': post_id
    }

    headers = {
        "Authorization": f"Bearer {access_key}",
    }

    # bookmark a post
    response = client.post(
        f'api/interactions/bookmarks',
        data=data,
        headers=headers
    )

    # check bookmark
    response = client.get(
        f'api/interactions/bookmarks',
        headers=headers
    )

    res_data = response.json() # list of posts

    assert response.status_code == 200
    assert len(res_data) > 0
    assert res_data[0]['id'] == post_id

def test_user_bookmarks_no_authentication(client):
    # check bookmark
    response = client.get(
        f'api/interactions/bookmarks',
    )

    res_data = response.json()

    assert response.status_code == 401
    assert res_data['detail'] == 'Not authenticated'

def test_user_bookmarks_bad_authentication(client):
    headers = {
        "Authorization": f"Bearer rrr {access_key}",
    }

    # check bookmark
    response = client.get(
        f'api/interactions/bookmarks',
        headers=headers
    )

    res_data = response.json()

    assert response.status_code == 401
    assert res_data['detail'] == 'Invalid token'


