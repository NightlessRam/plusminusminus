from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
from flask_pymongo import PyMongo

import os
import bcrypt

from datetime import datetime
from bson.objectid import ObjectId
import bleach
import hashlib
import secrets
import pytz




app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/myDatabase')
# app.secret_key = os.environ.get('SECRET_KEY', 'secretkey123456789')
mongo = PyMongo(app)

#X-Content-Type-Options: nosniff header
@app.after_request
def apply_caching(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

#Home Page
@app.route('/')

def index():
    posts = list(mongo.db.posts.find())  #retrieve all posts from database

    token = request.cookies.get('auth_token')
    #init username as 'Guest'
    username = 'Guest'
    if token:
        #hash token to match stored hash
        hash_object = hashlib.sha256(token.encode('utf-8'))
        token_hash = hash_object.hexdigest()
        session_record = mongo.db.session.find_one({'token_hash': token_hash})
        
        if session_record:
            username = session_record['username']
    return render_template('index.html', posts=posts, username=username)

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    password2 = request.form['password2']


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
    
    #make sure token is not None before proceeding
    if token is not None:
        #hash token to match stored hash
        hash_object = hashlib.sha256(token.encode('utf-8'))
        token_hash = hash_object.hexdigest()

        mongo.db.session.delete_one({'token_hash': token_hash})

    #clear auth_token cookie
    response = make_response(redirect(url_for('index')))
    response.set_cookie('auth_token', '', max_age=0, httponly=True)
    return response


@app.route('/posts', methods=['POST'])
def create_post():
    content = bleach.clean(request.form['content'])  # Sanitize input

    #retrieve token from cookie
    token = request.cookies.get('auth_token')
    
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
        'created_at': datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d'),
        'like': 0,  
        'dislike': 0  
    }
    mongo.db.posts.insert_one(post)
    # post['_id'] = str(post['_id'])  #convert ObjectId to string for JSON serialization
    # return jsonify(post)
    return redirect(url_for('index'))



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
    
    #makesure a user cant like/dislike more than once
    if not mongo.db.interactions.find_one({
        'post_id': post_id,
        'interactor': interactor,
        'interaction': interaction_type
    }):
        mongo.db.interactions.insert_one({
            'post_id': post_id,
            'interactor': interactor,
            'interaction': interaction_type
        })
        update_field = 'like' if interaction_type == 'Like' else 'dislike'
        mongo.db.posts.update_one({'_id': post_id}, {'$inc': {update_field: 1}})
        if interaction_type == 'Like':
            mongo.db.posts.update_one({'_id': ObjectId(post_id)}, {'$inc': {'like': 1}})
        elif interaction_type == 'Dislike':
            mongo.db.posts.update_one({'_id': ObjectId(post_id)}, {'$inc': {'dislike': 1}})

        return redirect(url_for('index'))
    # This is where you'd return a suitable response to the AJAX request
    # return jsonify(success=True)
    return redirect(url_for('index'))





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)