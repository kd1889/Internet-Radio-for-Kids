##Currently able to change playlists and radio stations using the python flask app
##Waiting on controls functions working to implement code for control.yaml and corresponding flask
import radio
import signal
import sys
import RPi.GPIO as GPIO
from resources.utils import BUTTON, LCD_COMMAND
import time
import yaml;
import threading
from flask import Flask,request, redirect, render_template
import os;

#import pygame as pg
GPIO.setmode(GPIO.BCM)
LCD_CMD = GPIO.LOW
radio.setup_pins()
exit_event = threading.Event() # exit_event for background musicPlayer
radio.setup_pygame_player();
#MUSIC_ENDED = pg.USEREVENT;
#pg.mixer.music.set_endevent(MUSIC_ENDED);

radio_file = open("./webui/radio.yaml", 'r');
playlist_file = open("./webui/playlist.yaml", 'r');
CONFIG_RADIO = yaml.safe_load(radio_file);
CONFIG_PLAYLIST = yaml.safe_load(playlist_file);
#print(PLAYLISTS[0]);
radio_file.close();
playlist_file.close();

class MusicPlayer(threading.Thread):

    def __init__(self):
        super().__init__()
        self.TIME_PLAYED = 0
        self.trackList = []
        self.index = 0 # for track number in trackList
        self.isPlaying = False # attribute is set to true when track is playing
        self.changeTrack = False # set to true when changing track
        #threading.Thread.__init__(self);
       # threading to keep play running at all times in background
        thread = threading.Thread(target=self.play, args=())
        thread.daemon = True
        thread.start()
        
    def load_trackList(self, PLAYLIST):
        self.trackList = PLAYLIST;
        self.index = 0;
        
    def pause(self):
        radio.pause_music()
        self.isPlaying = False

    def unpause(self):
        radio.unpause_music()
        self.isPlaying = True

    def process(self):
        if self.changeTrack:
            self.changeTrack = False
            self.play_track(self.index)

        if not radio.is_music_playing():
            # if music was playing before but has now ended play next track; else it has been paused
            if self.isPlaying == True:
                print("in process");
                self.play_next_track(self.index)

        time.sleep(1)

    def play(self):

        while True:
            if exit_event.is_set():
                break # kill background task play at the end when ctrl + c hit
            self.process()

    def play_track(self, trackNumber=0):
        """
        play track should be updated with actual code for playing station or
        track
        """
#        self.isPlaying = True;
#        for i in range(len(self.trackList)):
#            if not self.isPlaying:
#                break
#            print("Playing track: " + self.trackList[trackNumber])
#            time.sleep(1)
        if (len(self.trackList) == 0):
            return;
        self.TIME_PLAYED += radio.play_sound(self.trackList[trackNumber]);
        self.index = (self.index+1)%len(self.trackList) ;
        self.isPlaying = True;
        time.sleep(5)
#        self.isPlaying=False;
#        self.isPlaying = True

#        for i in range(5):
#            if not self.isPlaying:
#                break
#            print("playing track: " + self.trackList[trackNumber])
#            time.sleep(1)

#        self.isPlaying = False # done playing music

    def kill_music(self):
        radio.stop_player();
        radio.stop_radio();
        self.isPlaying = False
    def toggle_player(self, state):
        self.isPlaying = state;

    def play_next_track(self, trackNumber):
        #self.kill_music()
        # sleep time here must be greater than that in play to ensure effect
        # of kill_music and change track
        # time.sleep(1.1)
        self.index = trackNumber;
        self.changeTrack = True

class Page:

    def __init__(self, features):
        self.index = 0
        self.features = features

    def display_features(self):

        radio.write_arr_4bits(LCD_COMMAND["LCD_CLEAR"], LCD_CMD)
        for i in range(len(self.features)):
            radio.lcd_go_to_XY(i, 0)
            radio.send_data_to_screen(str(i + 1) + " " + self.features[i])

    def perform_actions(self, actionNumber=0):
        """
        actionNumber is the option number on the screen 
        performs default actions when changed to a page
        this method may be overriden in subclasses
        """
        self.display_features()

    def exit_actions(self, actionNumber=0):
        """
        actionNumber is the option number on the screen
        performs default actions when page is being exited
        this method may be overriden in subclasses
        """
        return

class PlaySomething(Page):
    FEATURES = ["Radio 1", "Playlist 1", "More"]


    def __init__(self):
        super().__init__(self.FEATURES)
        #Inital setup of the configuration value
        #Using flask-app + threads, update these values
        self.STATIONS = radio.create_stations(CONFIG_RADIO)[0];
        self.NUM_STATIONS = radio.create_stations(CONFIG_RADIO)[1];
        self.PLAYLIST_1 = radio.create_playlist(CONFIG_PLAYLIST, 1);
        self.PLAYLIST_2 = radio.create_playlist(CONFIG_PLAYLIST, 2);
        self.PLAYLISTS = [self.PLAYLIST_1, self.PLAYLIST_2];
        radio.setup_station(self.STATIONS);

        #Attributes to control radio + music player
        self.isLocked = False # parental lock
        self.isRadioPlaying = False
        self.isMusicOnly = True
        self.radio_number = 0 # radio number on screen - 1
        self.playlist_number = 0 # playlist number on screen - 1
        self.number_of_playlists = len(self.PLAYLISTS);
        self.number_of_stations = self.NUM_STATIONS;

        #music player to swap between tracks and radio stations
        self.musicPlayer = MusicPlayer()
        #self.musicPlayer.start();
        self.musicPlayer.load_trackList(self.PLAYLISTS[self.playlist_number]);
        if (self.NUM_STATIONS != 0):
            self.play_radio_station();
        else:
            self.FEATURES[0] = "No station"
        

    def get_time_played(self):
        return self.musicPlayer.TIME_PLAYED

    @staticmethod
    def increment_index(inc, maxIndex):
        inc += 1
        if inc == maxIndex:
            inc = 0
        return inc

    def next_option(self):
        """
        present next set of options available for radio and playlist
        """
        self.playlist_number = self.increment_index(
                                                    self.playlist_number,
                                                    self.number_of_playlists
        )
        self.radio_number = self.increment_index(
                                                 self.radio_number,
                                                 self.number_of_stations
        )
        if (self.NUM_STATIONS == 0):
            self.FEATURES[0] = "No Station";
        else:
            self.FEATURES[0] = "Radio " + str(self.radio_number + 1)
        self.FEATURES[1] = "Playlist " + str(self.playlist_number + 1)

    def is_radio_playing(self):
        return self.isRadioPlaying

    def stop_radio(self):
        radio.stop_radio()
        self.isRadioPlaying = False
        
    def stop_player(self):
        radio.stop_player();
        self.isMusicPlaying = False;
        
    def update_playlist(self, new_playlist, playlist_num):
        changed = -1;
        if (playlist_num > 2):
            return;
        new_trackList = radio.create_playlist(new_playlist, playlist_num);
        if new_trackList is None:
            new_trackList = [];
        for i in range(len(self.PLAYLISTS)):
            
            if i == playlist_num - 1:
                self.PLAYLISTS[i] = new_trackList;
                if i == self.playlist_number:
                    self.musicPlayer.load_trackList(new_trackList);
                    changed = i;
                    print(changed);
        if (not self.isRadioPlaying and changed == self.playlist_number):
            print(changed);
            self.stop_player(); 
            self.play_track();
        
    def update_radio(self, new_radio):
        self.STATIONS = radio.create_stations(new_radio)[0];
        self.NUM_STATIONS = radio.create_stations(new_radio)[1];
        self.number_of_stations = self.NUM_STATIONS;
        if self.NUM_STATIONS == 0:
            self.FEATURES[0] = "No station"
        else:
            self.FEATURES[0] = "Radio 1"
        print(self.STATIONS, self.NUM_STATIONS);
        radio.radio_reset();
        radio.setup_station(self.STATIONS);
        self.radio_number = 0;
        
    def play_radio_station(self):
        if self.NUM_STATIONS:
            radio.play_radio(self.radio_number + 1)
            self.isRadioPlaying = True

    def perform_actions(self, actionNumber=0):
        if actionNumber == 3:
            self.next_option()

        self.display_features()

    def exit_actions(self, actionNumber=0):
        if self.is_locked():
            print("Cannot play anything if locked")
            return # do not perform any action below

        if actionNumber == 1: #playing radio
            self.isMusicOnly = False
            self.stop_player()
            self.play_radio_station();
            self.musicPlayer.toggle_player(False);

        if actionNumber == 2: # playing playlist
            self.isMusicOnly = True
            self.stop_radio();
            self.musicPlayer.load_trackList(self.PLAYLISTS[self.playlist_number]);
            self.play_track();
            self.musicPlayer.toggle_player(True);
            #self.play();

    def is_playing(self):
        return self.musicPlayer.isPlaying

    def is_locked(self):
        return self.isLocked

    def lock(self):
        self.isLocked = True

    def unlock(self):
        self.isLocked = False

    def pause(self):
        self.musicPlayer.pause()

    def unpause(self):
        self.musicPlayer.unpause()

    def play_track(self, trackNumber=0):

        self.musicPlayer.play_next_track(trackNumber)

class HomePage(Page):
    FEATURES = ["Play Something", "Change User", "Setup"]

    def __init__(self):

        super().__init__(self.FEATURES)

class Book(threading.Thread):
    """Book holds the pages displayed and controls current page"""

    def __init__(self):
        threading.Thread.__init__(self);
        self.playSomething = PlaySomething()
        self.home = HomePage()
        self.home.perform_actions()
        self.isPausedOrMuted = False
        self.hasReachedMax = False # based on parental control
        self.pageIdentifier = {
                               "hp": {
                                      1: (self.playSomething, "playSomething") # button 1 -> radio
                                     },
                               "playSomething": {
                                                 1: (self.home, "hp"),
                                                 2: (self.home, "hp"),
                                                 3: (self.playSomething, "playSomething"),
                                                 5: (self.home, "hp") # back button
                              }
        }

        self.currPageName = "hp"
        self.currPage = self.home
        self.MAX_TIME = 0.5

        # threading to keep checking whether daily max has been reached
        thread = threading.Thread(target=self.p_control, args=())
        thread.daemon = True
        thread.start()

    def p_control(self):
        STOP = False;
        while STOP:
            if exit_event.is_set():
                break # kill background task play at the end when ctrl + c hit

            if self.playSomething.get_time_played() > self.MAX_TIME:

                if not self.playSomething.is_locked():
                    if self.playSomething.is_playing():
                        self.playSomething.pause()
                        print("Lock has paused music")

                    self.playSomething.stop_radio()
                    self.playSomething.lock()
            else:
                if self.playSomething.is_locked():
                    self.playSomething.unlock()
            time.sleep(1)

    def input(self, pin):

        output = None
        buttonNumber = None
        if pin == BUTTON[1]:
            if 1 in self.pageIdentifier[self.currPageName]:
                output = self.pageIdentifier[self.currPageName][1]
                buttonNumber = 1

        if pin == BUTTON[2]:
            if 2 in self.pageIdentifier[self.currPageName]:
                output = self.pageIdentifier[self.currPageName][2]
                buttonNumber = 2

        if pin == BUTTON[3]:
            if 3 in self.pageIdentifier[self.currPageName]:
                output = self.pageIdentifier[self.currPageName][3]
                buttonNumber = 3

        if pin == BUTTON[4]:
            if 4 in self.pageIdentifier[self.currPageName]:
                output = self.pageIdentifier[self.currPageName][4]
                buttonNumber = 4

            else: # mute or pause actions
                if self.playSomething.is_locked():
                    print("Cannot pause/mute if locked")
                    return
                if self.isPausedOrMuted is not None:
                    if not self.isPausedOrMuted:

                        if not self.playSomething.isMusicOnly: # if currently playing music

                            if self.playSomething.is_radio_playing():
                                self.playSomething.stop_radio()
                                print("radio muted")

                        else:

                            if self.playSomething.is_playing():
                                self.playSomething.pause()
                                print("Music paused")
                        self.isPausedOrMuted = True
                    else:

                        if not self.playSomething.isMusicOnly: # if currently radio and not playing music

                            if not self.playSomething.is_radio_playing():
                                self.playSomething.play_radio()
                                print("radio unmuted")
                        else:

                            if not self.playSomething.is_playing():
                                self.playSomething.unpause()
                                print("Music unpaused")
                        self.isPausedOrMuted = False

        if pin == BUTTON[5]:
            if 5 in self.pageIdentifier[self.currPageName]:
                output = self.pageIdentifier[self.currPageName][5]
                buttonNumber = 5

        if output is not None:
            self.currPage.exit_actions(buttonNumber)
            self.currPage, self.currPageName = output
            self.currPage.perform_actions(buttonNumber)
            print("Output is not None");

def signal_handler(sig, frame):
    radio.stop_player();
    radio.stop_radio();
    radio.radio_reset();
    exit_event.set()
    GPIO.cleanup()
    sys.exit(0)

def button_pressed_callback(channel):

    output = curr.input(channel)
    return

GPIO.add_event_detect(BUTTON[1], GPIO.FALLING, callback=button_pressed_callback, bouncetime=200)
GPIO.add_event_detect(BUTTON[2], GPIO.FALLING, callback=button_pressed_callback, bouncetime=200)
GPIO.add_event_detect(BUTTON[3], GPIO.FALLING, callback=button_pressed_callback, bouncetime=200)
#GPIO.add_event_detect(BUTTON[4], GPIO.FALLING, callback=button_pressed_callback, bouncetime=200) # mute or pause
#GPIO.add_event_detect(BUTTON[5], GPIO.FALLING, callback=button_pressed_callback, bouncetime=200) # back button
WEBUI_FOLDER = "/home/pi/curr_project/Internet-Radio-for-Kids/webui/"
app = Flask(__name__, static_folder= WEBUI_FOLDER + '/assets', template_folder=WEBUI_FOLDER + 'templates/')
curr = Book()

UPLOAD_FOLDER = "/home/pi/curr_project/Internet-Radio-for-Kids/uploads"


ALLOWED_MUSIC_EXTENSIONS = ["MP3", "WAV"]
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER;


stations = [];
radio_file = open("./webui/radio.yaml", 'r');
music_file = open("./webui/music.yaml", 'r');
playlist_file = open("./webui/playlist.yaml", 'r');
control_file = open("./webui/control.yaml", 'r');
playlists = yaml.safe_load(playlist_file);
stations = yaml.safe_load(radio_file);
musics = yaml.safe_load(music_file);
controls = yaml.safe_load(control_file);
radio_file.close();
music_file.close();
playlist_file.close();
control_file.close();

def update_config_file(updated_config, filename):
    open_file = open(filename, 'w');
    yaml.dump(updated_config, open_file);
    open_file.close();
    
@app.route("/")
def hello():
    return render_template('index.html');

@app.route("/radio.html", methods=["GET", "POST"])
def radio_1():
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
        
        update_config_file(stations, "./webui/radio.yaml");
        
        curr.playSomething.update_radio(stations);
        
        return redirect(request.url);
    return render_template('radio.html', stations=stations['stations'], disabled=dis);

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
        
        update_config_file(playlists, "./webui/playlist.yaml");
        
        curr.playSomething.update_playlist(playlists, 1);
        
        print(playlists['playlists'][2]);
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
        
        update_config_file(playlists, "./webui/playlist.yaml");
        
        curr.playSomething.update_playlist(playlists, 2);
        
        print(playlists['playlists'][2]);
        return redirect(request.url);

    return render_template('playlist-2.html', all_music=musics['musics'], pl2 = playlists['playlists'][2]['songs']);

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
            
            update_config_file(controls, "./webui/control.yaml");
      
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
            
            print("music saved")
            musics['musics'].append({"name":music_name, "filename":music.filename});
            musics['num_music'] = str(int(musics['num_music']) + 1);
            print(musics);
            
            update_config_file(musics, "./webui/music.yaml");
            
            return redirect(request.url)

    return render_template('upload-music.html', disabled=dis)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True, use_reloader=False)
    curr.start();
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()

