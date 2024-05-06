from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response, current_app, send_from_directory
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from flask_pymongo import PyMongo

import os
import bcrypt

import time
from datetime import datetime
from bson.objectid import ObjectId
import bleach
import hashlib
import secrets
import pytz
import threading
from auth import validate_password


app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/myDatabase')
# app.secret_key = os.environ.get('SECRET_KEY', 'secretkey123456789')
mongo = PyMongo(app)
socketio = SocketIO(app)


# Dictionary to store the expiration time of blocks
ip_data = {}
lock = threading.Lock()

def get_client_ip():
    # Try to retrieve the real IP from the X-Forwarded-For header
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    return request.remote_addr


def check_and_update_request_count(ip):
    with lock:
        current_time = datetime.now()
        if ip in ip_data:
            # Reset count if last request was more than 10 seconds ago
            if (current_time - ip_data[ip]['last_request_time']).seconds > 10:
                ip_data[ip]['count'] = 1
            else:
                ip_data[ip]['count'] += 1
            # Update last request time
            ip_data[ip]['last_request_time'] = current_time
        else:
            # Initialize data for a new IP
            ip_data[ip] = {
                'count': 1,
                'last_request_time': current_time,
                'block_until': None
            }

        # Check if IP should be blocked
        if ip_data[ip]['count'] > 50:
            # Block for 30 seconds
            ip_data[ip]['block_until'] = current_time + timedelta(seconds=30)
            return False
        return True

def is_ip_blocked(ip):
    with lock:
        if ip in ip_data:
            if ip_data[ip]['block_until'] and datetime.now() < ip_data[ip]['block_until']:
                return True
        return False


def serve_static_file(path):
    ip = get_client_ip()
    if is_ip_blocked(ip):
        return "Too Many Requests! Your IP is currently blocked. Please wait.", 429

    if not check_and_update_request_count(ip):
        return "Too Many Requests! Your IP is currently blocked. Please wait.", 429

    return send_from_directory('static', path)

# Define routes for specific static files
@app.route('/static/css/style.css')
def style_css():
    return serve_static_file('css/style.css')

@app.route('/static/image/avocado.png')
def avocado_png():
    return serve_static_file('image/avocado.png')

@app.route('/static/image/Good_background.jpg')
def good_background_jpg():
    return serve_static_file('image/Good_background.jpg')

@app.route('/static/js/script.js')
def script_js():
    return serve_static_file('js/script.js')

@app.errorhandler(429)
def ratelimit_handler(e):
    return "Too Many Requests! You have exceeded your request limit. Please wait.", 429



users = {}  # Maps usernames to user session IDs

#X-Content-Type-Options: nosniff header
@app.after_request
def apply_caching(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

#Home Page
@app.route('/')

def index():
    ip = get_client_ip()
    if is_ip_blocked(ip):
        return "Too Many Requests! Your IP is currently blocked. Please wait.", 429
    
    if not check_and_update_request_count(ip):
        return "Too Many Requests! Your IP is currently blocked. Please wait.", 429
    
    
    username = get_username_from_token(request.cookies.get('auth_token'))
    query = {
        "$or": [
            {"messageType": {"$ne": "dm"}},
            {"$or": [{"sender": username}, {"receiver": username}]}
        ]
    }
    posts = list(mongo.db.posts.find(query))[::-1]

    #changed the handling of updating post likes/dislikes here

    postUpdater = mongo.db.posts.find({})
    for post in postUpdater:
        print(post)
        post_id = str(post["_id"])
        post_interactions = mongo.db.interactions.find({"post_id": post_id})
        likes = 0
        dislikes = 0
        for interactions in post_interactions:
            if interactions["interaction"] == "like":
                likes+=1
            elif interactions["interaction"] == "dislike":
                dislikes +=1
        mongo.db.posts.update_one({"_id": post["_id"]},{"$set": {'like': likes, "dislike": dislikes}})
    return render_template('index.html', posts=posts, username=username)

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    password2 = request.form['password2']

    if validate_password(password) == False:
        return 'Password is invalid', 400

    if password != password2:
        return 'Passwords do not match', 400

    existing_user = mongo.db.users.find_one({'username': username})
    if existing_user is not None:
        return 'Username already exists', 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    mongo.db.users.insert_one({
        'username': username,
        'password': hashed_password
    })

    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = mongo.db.users.find_one({'username': username})


    if password is None:
        return 'Password is required', 400

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        #generate a random token
        token = secrets.token_hex(16)

        # Hash the token before storing it in the database (using SHA-256)
        hash_object = hashlib.sha256(token.encode('utf-8'))
        token_hash = hash_object.hexdigest()


        # Store the hash in the 'session' collection
        mongo.db.session.insert_one({
            'username': username,
            'token_hash': token_hash
        })

        # Send the token as an HttpOnly cookie to the client
        response = make_response(redirect(url_for('index')))
        response.set_cookie('auth_token', token, max_age=3600, httponly=True)
        return response

    else:
        # Handle login failure
        return 'Invalid username/password', 401

@app.route('/logout', methods=['POST'])
def logout():
    token = request.cookies.get('auth_token')
    username = get_username_from_token(token)
    if token:
        hash_object = hashlib.sha256(token.encode('utf-8'))
        token_hash = hash_object.hexdigest()
        mongo.db.session.delete_one({'token_hash': token_hash})

    if username in users:
        del users[username]
        emit('update user list', list(users.keys()), broadcast=True, namespace='/')

    response = make_response(redirect(url_for('index')))
    response.set_cookie('auth_token', '', expires=0, httponly=True, path='/')
    return response


def get_schedule_time(message:str):
    #example command !scheduled_post: 05/04/2024 06:00:00 PM!
    if message.startswith('!scheduled_post: '):
        time = message.split("!")[1].split(": ")[1]
        return time
    else:
        return None

@app.route('/posts', methods=['POST'])
def create_post():
    try:
        content = bleach.clean(request.form['content'])  # Sanitize input
        messageType = request.form.get('messageType', 'post')  # Default to 'post' if not specified

        #retrieve token from cookie
        token = request.cookies.get('auth_token')
        
        # Handle the image if it exists
        image = request.files.get('image')
        image_filename = None
        if image and allowed_file(image.filename):
            image_filename = save_image_to_disk(image)
        
        #scheduled post
        scheduled_time_post = None
        if content.startswith("!scheduled_post: ") and get_username_from_token(token) != 'Guest':
            if not (content[37:40] == "PM!" or content[37:40] == "AM!") or len(content)<=40 or not any(c != ' ' for c in content[40:]):
                return jsonify(success=False, message="Invalid scheduled time format or no message"), 400
            scheduled_time_post = get_schedule_time(content)
            current_time = datetime.now(pytz.timezone('US/Eastern')).strftime("%m/%d/%Y %I:%M:%S %p")
            content = content[40:]  # Remove the scheduled time from the content
        elif content.startswith("!") and not content.startswith("!scheduled_post: "):
            return jsonify(success=False, message="Invalid command"), 400
        
        if scheduled_time_post is not None and (scheduled_time_post<current_time):
            return jsonify(success=False, message="Scheduled time is in the past"), 400

        #init username as 'Guest'
        username = get_username_from_token(token)
        post = {
            'username': username,
            'content': content,
            'image': image_filename,
            'created_at': datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d'),
            'messageType': messageType,
            'scheduled_time': scheduled_time_post
        }
        # Add likes and dislikes only for posts
        # if messageType == 'post':
        #     post.update({'likes': 0, 'dislikes': 0})
        if scheduled_time_post is not None:
            mongo.db.scheduled.insert_one(post)
        else:
            mongo.db.posts.insert_one(post) 
        # post['_id'] = str(post['_id'])  #convert ObjectId to string for JSON serialization
        # return jsonify(post)

        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500
    
@socketio.on('send chat message')
def handle_chat_message(data):
    token = request.cookies.get('auth_token')
    username = 'Guest'
    message = bleach.clean(data['content'])
    if token:
        # Hash the token to match the stored hash
        hash_object = hashlib.sha256(token.encode('utf-8'))
        token_hash = hash_object.hexdigest()
        # Find the session in the database using the hashed token
        session_record = mongo.db.session.find_one({'token_hash': token_hash})
        
        if session_record:
            # If a session is found, retrieve the username from the session
            username = session_record['username']
    emit('new content', {'content': message, 'username': username}, broadcast=True)
    post = {
        'username': username,
        'content': message,
        'created_at': datetime.now(pytz.timezone('US/Eastern')).strftime('%B %d, %Y at %I:%M:%S %p')
    }
    mongo.db.posts.insert_one(post)


@app.route('/interact', methods=['POST'])
def interact():
    post_id = request.form.get('post_id')
    interaction_type = request.form.get('interaction')  # "Like" or "Dislike"
    interactor = 'Guest'
    
    #retrieve token from HttpOnly cookie
    token = request.cookies.get('auth_token')
    
    if token:
        hash_object = hashlib.sha256(token.encode('utf-8'))
        token_hash = hash_object.hexdigest()
        session_record = mongo.db.session.find_one({'token_hash': token_hash})
        
        if session_record:
            interactor = session_record['username']
    
    if not mongo.db.interactions.find_one({
        'post_id':post_id,
        'interactor': interactor,
    }):
        mongo.db.interactions.insert_one({
            'post_id':post_id,
            'interactor': interactor,
            'interaction': interaction_type
        })
    else:
        currentInteraction = mongo.db.interactions.find_one({
            'post_id':post_id,
            'interactor': interactor
        })
        newReaction = interaction_type
        oldReaction = currentInteraction["interaction"]
        if oldReaction == newReaction:
            newReaction = "neutral"
        

        mongo.db.interactions.update_one({
            'post_id':post_id,
            'interactor': interactor,
        }, {'$set':{'interaction': newReaction}})
    return redirect(url_for('index'))

# Helper Merthod for file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper Method to save image to disk
def save_image_to_disk(file):
    image_dir = os.path.join(current_app.root_path, 'static', 'image')  
    os.makedirs(image_dir, exist_ok=True)

    # Check the file type (you could also use file.mimetype here)
    file_type = file.content_type

    # Determine the file extension based on the file type
    if file_type == 'image/jpeg':
        extension = '.jpg'
    elif file_type == 'image/png':
        extension = '.png'
    elif file_type == 'image/gif':
        extension = '.gif'
    else:
        raise ValueError('Unsupported file type')

    filename = f'image_{secrets.token_hex(8)}{extension}'
    image_path = os.path.join(image_dir, filename)

    # Save the file securely
    file.save(image_path)
    return filename

@socketio.on('connect')
def handle_connect():
    username = get_username_from_token(request.cookies.get('auth_token'))
    if username and username != 'Guest':
        users[username] = request.sid  # Map current SocketIO session ID to username
        join_room(username)  # Join a room for private messaging
        emit('update user list', list(users.keys()), broadcast=True, include_self=False)
        print(f"{username} connected and added to the user list.")
    else:
        print("Guest connected; not adding to the user list.")    
        
@socketio.on('disconnect')
def handle_disconnect():
    # Retrieve username the same way upon disconnect
    username = get_username_from_token(request.cookies.get('auth_token'))
    if username and username in users:
        del users[username]
        emit('update user list', list(users.keys()), broadcast=True)

@socketio.on('send dm')
def handle_send_dm(data):
    sender = get_username_from_token(request.cookies.get('auth_token'))
    receiver = data['receiver']
    message = bleach.clean(data['message'])
    messageType = 'dm'  # Specify the message type as 'dm'

    if sender and receiver and receiver in users:
        # Data to send to the receiver
        dm_data_to_receiver = {
            'sender': sender,
            'content': message,
            'messageType': messageType,
            'to_self': False,  # Indicates if this message is to self
            'receiver': receiver
        }
        # Data to echo back to the sender
        dm_data_to_sender = {
            'sender': sender,
            'content': message,
            'messageType': messageType,
            'to_self': True,  # This message is to self
            'receiver': receiver
        }
        dm = {
            'sender': sender,
            'receiver': receiver,
            'content': message,
            'created_at': datetime.now(pytz.timezone('US/Eastern')).strftime('%B %d, %Y at %I:%M:%S %p'),
            'messageType': messageType
        }
        # Save the DM to the posts collection
        mongo.db.posts.insert_one(dm)
        
        emit('receive dm', dm_data_to_receiver, room=users[receiver])
        emit('receive dm', dm_data_to_sender, room=users[sender])

@socketio.on('request_user_list')
def handle_request_user_list():
    emit('update user list', list(users.keys()), broadcast=True)
    print("User list requested and broadcasted.")

def get_username_from_token(token):
    username = 'Guest'  # Default username if token is invalid or not present
    if token:
        try:
            hash_object = hashlib.sha256(token.encode('utf-8'))
            token_hash = hash_object.hexdigest()
            session_record = mongo.db.session.find_one({'token_hash': token_hash})
            if session_record:
                username = session_record['username']
        except Exception as e:
            print(f"Error retrieving username from token: {e}")
    return username


def check_schedule_posts():
    while True:
        current_time = datetime.now(pytz.timezone('US/Eastern')).strftime("%m/%d/%Y %I:%M:%S %p")
        scheduled_posts = list(mongo.db.scheduled.find({}))
        if len(scheduled_posts) == 0:
            continue
        for post in scheduled_posts:
            if 'scheduled_time' in post:
                time_remaining = max(0, (datetime.strptime(post['scheduled_time'], "%m/%d/%Y %I:%M:%S %p") - datetime.strptime(current_time, "%m/%d/%Y %I:%M:%S %p")).total_seconds())
                # socketio.emit('update_scheduled_post', {'time_remaining': time_remaining, 'post_id': str(post['_id'])}, namespace='/')
                socketio.emit('update_scheduled_post', {'time_remaining': time_remaining, 'post_id': str(post['_id'])}, room=post['username'])

                if post['scheduled_time'] < current_time:
                    post["created_at"] = datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d')
                    mongo.db.posts.insert_one(post)
                    mongo.db.scheduled.delete_one({'_id': post['_id']})
                    socketio.emit('reload_page', namespace='/') 
        print(f"Checked for scheduled posts at {current_time}.")
        time.sleep(1)
        
def start_background_thread():
    thread = threading.Thread(target=check_schedule_posts)
    thread.daemon = True  # Daemonize the thread so it will be terminated when the main thread exits
    thread.start()

@app.route('/rock-paper-scissors')
def rock_paper_scissors():
    return render_template('rock_paper_scissors.html')

if __name__ == '__main__':
    start_background_thread()
    socketio.run(app, host='0.0.0.0', port=8080, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)
    # app.run(host='0.0.0.0', port=8080, debug=True)
