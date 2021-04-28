from flask import Flask, request, redirect, render_template
import os

MUSIC_UPLOAD_PATH = "/home/pi/Desktop/new/Internet-Radio-for-Kids/uploads"
ALLOWED_MUSIC_EXTENSIONS = ["MP3", "WAV"]
app = Flask(__name__, static_folder='~/curr_project/Internet-Radio-for-Kids/webui/assets')


stations = [];
file = open("stations.txt", 'r');
def fill_stations(file):
    for line in file:
       name = line[:line.find("|")];
       line = line[line.find("|")+1:];
       url = line[:line.find("|")];
       line = line[line.find("|")+1:];
       state = line;
       stations.append({'name':name, 'url':url, 'state':state});

@app.route("/")
def hello():
    fill_stations(file);
    return render_template('index.html', stations=stations);

@app.route("/radio.html")
def radio():
    return render_template('radio.html');

@app.route("/control.html")
def control():
    return render_template('control.html');

@app.route("/music.html")
def music():
    return render_template('music.html');

def valid_extension(file_name):

    if "." not in file_name:
        return False

    ext = file_name.split(".")[-1]

    return ext.upper() in ALLOWED_MUSIC_EXTENSIONS

@app.route("/upload-music", methods=["GET", "POST"])
def upload_music():

    if request.method == "POST":

        if request.files:

            music = request.files["music"]

            if not valid_extension(music.filename):
                print("This file type is not allowed")
                return redirect(request.url)

            music.save(os.path.join(MUSIC_UPLOAD_PATH, music.filename))

            print("music saved")

            return redirect(request.url)

    return render_template('upload_music.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)

