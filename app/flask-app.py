for flask import Flask
app = Flask(__name__, static_folder='');

@app.route("/")
def helo():
    return app.send_static_file('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)

