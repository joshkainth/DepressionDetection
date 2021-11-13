from flask import Flask
from flask import request
import flask
from flask_cors import CORS
import psycopg2
# from markupsafe import escape

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Hello Nov2021"

@app.route("/<name>")
def homeParamas(name):
    return f"<p>Hello From {name}</p>"

@app.route('/details')
def getDetails():
    audio_name = request.args.get("audio_name")

    conn = None
    try: 
        conn = psycopg2.connect("dbname={0} user={1} password={2}".format("audio_depressed", "postgres", "V@St@v9SRI5011"))
        cursor = conn.cursor()

        sql = "SELECT * FROM data where audio_name='{0}'".format(audio_name)
        cursor.execute(sql)
        response = cursor.fetchall()
        return flask.jsonify({
            "response": response[0]
        })

    except Exception as exception:
        print(exception)
        return "Errro"
    finally: 
        conn.close()
