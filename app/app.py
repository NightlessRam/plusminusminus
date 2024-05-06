from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response, current_app
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from flask_pymongo import PyMongo
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import os
import bcrypt

from datetime import datetime
from bson.objectid import ObjectId
import bleach
import hashlib
import secrets
import pytz

from auth import validate_password


app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address)
app.config["MONGO_URI"] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/myDatabase')
# app.secret_key = os.environ.get('SECRET_KEY', 'secretkey123456789')
mongo = PyMongo(app)
socketio = SocketIO(app)

users = {}  # Maps usernames to user session IDs

#X-Content-Type-Options: nosniff header
@app.after_request
def apply_caching(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

#Home Page
@app.route('/')
@limiter.limit('50 per 10 seconds')

def index():
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



    #original route
    # posts = list(mongo.db.posts.find({}))  #retrieve all posts from database

    # token = request.cookies.get('auth_token')
    # #init username as 'Guest'
    # username = 'Guest'
    # if token:
    #     #hash token to match stored hash
    #     hash_object = hashlib.sha256(token.encode('utf-8'))
    #     token_hash = hash_object.hexdigest()
    #     session_record = mongo.db.session.find_one({'token_hash': token_hash})
        
    #     if session_record:
    #         username = session_record['username']
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
        
        #init username as 'Guest'
        username = 'Guest'
        if token:
            # Hash the token to match the stored hash
            hash_object = hashlib.sha256(token.encode('utf-8'))
            token_hash = hash_object.hexdigest()
            # Find the session in the database using the hashed token
            session_record = mongo.db.session.find_one({'token_hash': token_hash})
            
            if session_record:
                # If a session is found, retrieve the username from the session
                username = session_record['username']
        post = {
            'username': username,
            'content': content,
            'image': image_filename,
            'created_at': datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d'),
            'messageType': messageType
        }
        # Add likes and dislikes only for posts
        # if messageType == 'post':
        #     post.update({'likes': 0, 'dislikes': 0})
            
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
        'created_at': datetime.now(pytz.timezone('US/Eastern')).strftime('%B %d, %Y at %I:%M:%S %p'),
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


    
    # #makesure a user cant like/dislike more than once
    # if not mongo.db.interactions.find_one({
    #     'post_id': post_id,
    #     'interactor': interactor,
    #     'interaction': interaction_type
    # }):
    #     mongo.db.interactions.insert_one({
    #         'post_id': post_id,
    #         'interactor': interactor,
    #         'interaction': interaction_type
    #     })
    #     update_field = 'like' if interaction_type == 'Like' else 'Dislike'
    #     mongo.db.posts.update_one({'_id': post_id}, {'$inc': {update_field: 1}})
    #     if interaction_type == 'Like':
    #         mongo.db.posts.update_one({'_id': ObjectId(post_id)}, {'$inc': {'like': 1}})
    #     elif interaction_type == 'Dislike':
    #         mongo.db.posts.update_one({'_id': ObjectId(post_id)}, {'$inc': {'dislike': 1}})

    #     return redirect(url_for('index'))
    # This is where you'd return a suitable response to the AJAX request
    # return jsonify(success=True)
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

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)
    # app.run(host='0.0.0.0', port=8080, debug=True)
