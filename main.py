from flask import Flask, request, jsonify, make_response
import sqlite3
from flask import g
import jwt
from datetime import datetime, timedelta

DATABASSE = './tarea3.db'

KEY = 'secret'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASSE)
    return db


app = Flask(__name__)


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


@app.route("/login", methods=['POST'])
def login():
    # auth = request.authorization
    username = request.json["username"]
    password = request.json["password"]

    # select user with username
    cur = get_db().cursor()
    sql = """SELECT username, password FROM admin WHERE username = ?;"""
    cur.execute(sql, (username,))
    ans = cur.fetchall()
    if len(ans) == 0:
        return make_response({"error": 'Could not verify'}, 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    # check if password of the user is correct
    if ans[0][1] != password:
        return make_response({"error": 'Could not verify'}, 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    token = jwt.encode({
        "user": username,
        "expiration": (datetime.utcnow() + timedelta(minutes=30)).timestamp()
    }, key=KEY)
    return jsonify({"token": token})


@app.route("/protected")
def protected():
    token = request.args.get('token')
    try:
        print(token)
        data = jwt.decode(token, key=KEY, algorithms=['HS256'])
        if data['expiration'] < datetime.utcnow().timestamp():
            return make_response('Token expired', 401)
        return jsonify({"message": "You are in the protected area"})
    except:
        return make_response({"error": "Invalid token"}, 401)

@app.route("/addcompany",methods=["POST"])
def addcompany():
    token_j=request.json["token"]
    #try:
    print(token_j)
    data = jwt.decode(token_j, key=KEY, algorithms=['HS256'])
    if data['expiration'] < datetime.utcnow().timestamp():
        return make_response('Token expired', 401)
    
    nombre_company=request.json["company_name"]
    company_api=jwt.encode({
        "company_name":nombre_company
    }, key=KEY)
    sql_insert=f"""
    INSERT INTO company (company_name,company_api_key)
    VALUES ('{nombre_company}','{company_api}');
    """
    cur = get_db().cursor()
    cur.execute(sql_insert)
    get_db().commit()
    ans = cur.fetchall()


    return jsonify({"message": "You are in the protected area", "company_api_key":company_api})
    #except:
    #    return make_response({"error": "Invalid token"}, 401)




if __name__ == "__main__":
    app.run(debug=True)
