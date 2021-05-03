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

# defualt values at the start of the program
CONFIG = {
          "textbox": {
                      "start_time": 1,
                      "end_time": 4,
                      "max_playtime": 5
          },
          "drop_down": {
                        "pc_status": [ # [name, is_selected]
                                      ["Enable", False],
                                      ["Disable", True]
                        ],
                        "add_music_radio": [
                                            ["Enable_Session", False],
                                            ["Enable_Always", False],
                                            ["Disable", True]
                        ]
         }
}

def update_config(values):
    CONFIG["textbox"]["start_time"] = values["start_time"]
    CONFIG["textbox"]["end_time"] = values["end_time"]
    CONFIG["textbox"]["max_playtime"] = values["max_playtime"]
    newPcStatus = values["pc_status"]
    newMusicRadioStatus = values["add_music_radio"]

    for statusOption in CONFIG["drop_down"]["pc_status"]:
        if statusOption[0] == newPcStatus:
            statusOption[1] = True
        else:
            statusOption[1] = False

    for statusOption in CONFIG["drop_down"]["add_music_radio"]:
        if statusOption[0] == newMusicRadioStatus:
            statusOption[1] = True
        else:
            statusOption[1] = False

@app.route("/parental-control", methods=["GET", "POST"])
def parental_control():

    if request.method == "POST":
        if request.form:

            print("pc_status:",request.form.get("pc_status"))
            print("max_playtime:", request.form.get("max_playtime"))
            print("start_time:", request.form.get("start_time"))
            print("end_time:", request.form.get("end_time"))
            print("add_music_radio:", request.form.get("add_music_radio"))

            update_config(request.form)
            return redirect(request.url)

    return render_template('parental.html', config=CONFIG)

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

