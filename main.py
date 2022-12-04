from flask import Flask
import sqlite3
from flask import g

DATABASSE = './tarea3.db'

def get_db():
        db = getattr(g,'_database', None)
        if db is None:
                db=g._database = sqlite3.connect(DATABASSE)
        return db


app=Flask(__name__)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
        cur = get_db().cursor()
        sql = """SELECT * FROM admin;"""
        cur.execute(sql)
        ans = cur.fetchall()

        return ans