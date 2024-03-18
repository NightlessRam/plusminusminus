from flask import Flask, send_from_directory, make_response, render_template,request, redirect, url_for, session
from flask_pymongo import PyMongo

import os


app = Flask(__name__)

#app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
app.config["MONGO_URI"] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/myDatabase')

app.secret_key = 'secretkey123456789'

mongo = PyMongo(app)



print("-=-=-=-=- Here -> ", app.config["MONGO_URI"])


@app.route('/')
def root():
    response = send_from_directory('.', 'index.html')
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    if 'username' in session:
        output = f"Welcome {session['username']}! <a href='/logout'>Logout</a>"
        response = make_response(output)
        
    return response

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = mongo.db.users.find_one({'username': username})

    if user and 'password' in user and user['password'] == password:
        
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


    mongo.db.users.insert_one(
        {
        'username': username,
        'password': password
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

@app.route('/js/script.js')
def js():
    response = make_response(send_from_directory('js', 'script.js'))
    response.headers['Content-Type'] = 'application/javascript'
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

@app.route('/image/objonecam.jpg')
def image():
    response = make_response(send_from_directory('image', 'objonecam.jpg'))
    response.headers['Content-Type'] = 'image/jpeg'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

if __name__ == '__main__':
    app.run( host='0.0.0.0', port=8080, debug=True)
