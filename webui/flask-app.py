from flask import Flask, redirect, render_template

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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)

