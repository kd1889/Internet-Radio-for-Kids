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
playlist_file = open("playlist.yaml", 'r');
control_file = open("control.yaml", 'r');
playlists = yaml.safe_load(playlist_file);
stations = yaml.safe_load(radio_file);
musics = yaml.safe_load(music_file);
controls = yaml.safe_load(control_file);
radio_file.close();
music_file.close();
playlist_file.close();
control_file.close();

@app.route("/")
def hello():
    return render_template('index.html');

@app.route("/radio.html", methods=["GET", "POST"])
def radio():
#    fill_stations(file)
    print("Before POST");
    dis = controls["drop_down"]["add_music_radio"][2][1];
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
        file.close();
        return redirect(request.url);
    return render_template('radio.html', stations=stations['stations'], disabled=dis);


#@app.route("/control.html")
#def control():
#    return render_template('control.html');

@app.route("/music.html")
def music():
    return render_template('music.html');

@app.route("/playlist-music.html")
def playlist():
    return render_template('playlist-music.html');


@app.route("/playlist-1.html", methods=["GET", "POST"])
def playlist1():
    if request.method == "POST":
        songs_to_add = request.form.getlist('music');
        if(len(songs_to_add) == 0):
            playlists['playlists'][1]['songs'] = None;
        else:
            playlists['playlists'][1]['songs'] = songs_to_add;
        playlists['playlists'][1]['num_songs'] = str(len(songs_to_add));
        print(playlists['playlists'][1]);
        config_playlist_file = open("playlist.yaml", 'w');
        yaml.dump(playlists, config_playlist_file);
        config_playlist_file.close();
        return redirect(request.url);
    return render_template('playlist-1.html', all_music=musics['musics'], pl1 = playlists['playlists'][1]['songs']);

@app.route("/playlist-2.html", methods=["GET", "POST"])
def playlist2():
    if request.method == "POST":
        songs_to_add = request.form.getlist('music');
        if(len(songs_to_add) == 0):
            playlists['playlists'][2]['songs'] = None;
        else:
            playlists['playlists'][2]['songs'] = songs_to_add;
        playlists['playlists'][2]['num_songs'] = str(len(songs_to_add));
        config_playlist_file = open("playlist.yaml", 'w');
        yaml.dump(playlists, config_playlist_file);
        config_playlist_file.close();
        print(playlists['playlists'][2]);
        return redirect(request.url);

    return render_template('playlist-2.html', all_music=musics['musics'], pl2 = playlists['playlists'][2]['songs']);
# defualt values at the start of the program
"""
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
"""
def update_config(values):
    controls["textbox"]["start_time"] = values["start_time"]
    controls["textbox"]["end_time"] = values["end_time"]
    controls["textbox"]["max_playtime"] = values["max_playtime"]
    newPcStatus = values["pc_status"]
    newMusicRadioStatus = values["add_music_radio"]

    for statusOption in controls["drop_down"]["pc_status"]:
        if statusOption[0] == newPcStatus:
            statusOption[1] = True
        else:
            statusOption[1] = False

    for statusOption in controls["drop_down"]["add_music_radio"]:
        if statusOption[0] == newMusicRadioStatus:
            statusOption[1] = True
        else:
            statusOption[1] = False

@app.route("/control.html", methods=["GET", "POST"])
def parental_control():

    if request.method == "POST":
        if request.form:
            print("pc_status:",request.form.get("pc_status"))
            print("max_playtime:", request.form.get("max_playtime"))
            print("start_time:", request.form.get("start_time"))
            print("end_time:", request.form.get("end_time"))
            print("add_music_radio:", request.form.get("add_music_radio"))
            update_config(request.form)
            config_control_file = open("control.yaml", 'w');
            yaml.dump(controls, config_control_file);
            config_control_file.close();
            return redirect(request.url)
    return render_template('control.html', config=controls)

def valid_extension(file_name):

    if "." not in file_name:
        return False

    ext = file_name.split(".")[-1]

    return ext.upper() in ALLOWED_MUSIC_EXTENSIONS

@app.route("/upload-music.html", methods=["GET", "POST"])
def upload_music():
    dis = controls["drop_down"]["add_music_radio"][2][1];
    if request.method == "POST":

        if request.files:

            music = request.files["music"]
            music_name = request.form["music_name"];
            if not valid_extension(music.filename):
                print("This file type is not allowed")
                return redirect(request.url)
            for files in musics['musics']:
                if files['filename'] == music.filename:
                    return redirect(request.url);
            music.save(os.path.join(app.config['UPLOAD_FOLDER'], music.filename))
            config_music_file = open("music.yaml", 'w');
            print("music saved")
            musics['musics'].append({"name":music_name, "filename":music.filename});
            musics['num_music'] = str(int(musics['num_music']) + 1);
            print(musics);
            yaml.dump(musics, config_music_file);
            config_music_file.close();
            return redirect(request.url)

    return render_template('upload-music.html', disabled=dis)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)

