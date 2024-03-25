from flask import Flask, send_from_directory, make_response, render_template,request, redirect, url_for, session
from flask_pymongo import PyMongo


import os
import bcrypt
<<<<<<< Updated upstream
=======
from datetime import datetime
from bson.objectid import ObjectId
import bleach
import hashlib
import secrets
import pytz
import html
from markupsafe import Markup
>>>>>>> Stashed changes


app = Flask(__name__)

#app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
app.config["MONGO_URI"] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/myDatabase')

app.secret_key = 'secretkey123456789'

mongo = PyMongo(app)


print("-=-=-=-=- Here -> ", app.config["MONGO_URI"])


@app.route('/')
<<<<<<< Updated upstream
def root():
    response = send_from_directory('.', 'index.html')
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    if 'username' in session:
        output = f"Here -> new guy called, {session['username']}! <a href='/logout'>Logout</a>"
        response = make_response(output)
=======
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
>>>>>>> Stashed changes
        
    else:
        response = send_from_directory('.', 'index.html')

    return response
        
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = mongo.db.users.find_one({'username': username})
    
    print(f"-+-+-+ hash in db -+-+-+: {user['password']}")

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):        
        session['username'] = username
                
    else:
        
        return "wrong username and/or password", 401
    
    return redirect(url_for('root'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    
    username = request.form['username']
    password = request.form['password']
    password2 = request.form['password2']
    
    if password != password2:
            return 'passowrds not same', 400
    
    user_check = mongo.db.users.find_one({'username': username})

    if user_check:
        return 'username already in use', 400

    h_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    print(f"-+-+-+ hashed password -+-+-+: {h_password}") 
    
    mongo.db.users.insert_one(
        {
        'username': username,
        'password': h_password
        }
    )

    session['username'] = username

    return redirect(url_for('root'))

@app.route('/logout')
def logout():
    # idk what to do here for logout functionality 
    
    session.pop('username', None)
    
    return redirect(url_for('root'))


@app.route('/css/style.css')
def css():
    response = make_response(send_from_directory('css', 'style.css'))
    response.headers['Content-Type'] = 'text/css'
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

<<<<<<< Updated upstream
@app.route('/js/script.js')
def js():
    response = make_response(send_from_directory('js', 'script.js'))
    response.headers['Content-Type'] = 'application/javascript'
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
=======
@app.route('/posts', methods=['POST'])
def create_post():
    content = bleach.clean(request.form['content'])  # Sanitize input
    # content = request.form['content']
    
    # content = html.escape(request.form['content'])
    # content = str(content)
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
>>>>>>> Stashed changes

@app.route('/image/objonecam.jpg')
def image():
    response = make_response(send_from_directory('image', 'objonecam.jpg'))
    response.headers['Content-Type'] = 'image/jpeg'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

if __name__ == '__main__':
    app.run( host='0.0.0.0', port=8080, debug=True)