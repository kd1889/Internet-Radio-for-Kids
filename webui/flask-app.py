

from flask import Flask,request, redirect, render_template
import os;
import yaml

app = Flask(__name__, static_folder='assets')


UPLOAD_FOLDER = "/home/pi/curr_project/Internet-Radio-for-Kids/uploads"
ALLOWED_MUSIC_EXTENSIONS = ["MP3", "WAV"]
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER;


stations = [];
radio_file = open("radio.yaml", 'r');
music_file = open("music.yaml", 'r');
stations = yaml.safe_load(radio_file);
musics = yaml.safe_load(music_file);
radio_file.close();
music_file.close();

@app.route("/")
def hello():
    return render_template('index.html');

@app.route("/radio.html", methods=["GET", "POST"])
def radio():
#    fill_stations(file)
    print("Before POST");
    if request.method == "POST":
        print("IN_POST");
        enable_station = request.form.getlist('station');
        for num in range(int(stations['num_stations'])):
            if str(num) in enable_station:
                stations['stations'][num]['state'] = True;
            else:
                stations['stations'][num]['state'] = False;
        file = open("radio.yaml", 'w');
        yaml.dump(stations,file);
        return redirect(request.url);
    return render_template('radio.html', stations=stations['stations']);

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

@app.route("/upload-music.html", methods=["GET", "POST"])
def upload_music():

    if request.method == "POST":

        if request.files:

            music = request.files["music"]
             
            if not valid_extension(music.filename):
                print("This file type is not allowed")
                return redirect(request.url)
            for files in musics['musics']:
                if file['filename'] == music.filename:
                return redirect(request.url);
            music.save(os.path.join(app.config['UPLOAD_FOLDER'], music.filename))

            print("music saved")

            return redirect(request.url)

    return render_template('upload-music.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)

