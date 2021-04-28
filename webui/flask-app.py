from flask import Flask, redirect, render_template
import yaml

app = Flask(__name__, static_folder='assets')

file = open("radio.yaml", 'r');
stations = yaml.safe_load(file)['stations'];
@app.route("/")
def hello():
    return render_template('index.html');

@app.route("/radio.html")
def radio():
#    fill_stations(file)
    return render_template('radio.html', stations=stations);

@app.route("/control.html")
def control():
    return render_template('control.html');

@app.route("/music.html")
def music():
    return render_template('music.html');


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)

