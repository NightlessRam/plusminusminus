from flask import Flask, send_from_directory, make_response

app = Flask(__name__)

@app.route('/')
def root():
    response = send_from_directory('.', 'index.html')
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

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
    app.run( host='0.0.0.0', port=8080)
