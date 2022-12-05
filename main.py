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

#Agregar una nueva comañia
@app.route("/company",methods=["POST"])
def company():
    token_j=request.json["token"]
    try:
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


        return jsonify({"message": "Compañia agregada correctamente", "company_api_key":company_api})
    except:
        return make_response({"error": "Invalid token"}, 401)

#Mostrar toda la lista de company
@app.route("/company", methods=["GET"])
def listcompany():
    token = request.args.get('token')
    try:
        print(token)
        data = jwt.decode(token, key=KEY, algorithms=['HS256'])
        if data['expiration'] < datetime.utcnow().timestamp():
            return make_response('Token expired', 401)
        cur = get_db().cursor()
        sql = """SELECT * FROM company;"""
        cur.execute(sql)
        ans = cur.fetchall()
        return jsonify({"message": "You are in the protected area","Lista":ans})

    except:
        return make_response({"error": "Invalid token"}, 401)

#Agregar una nueva locación
@app.route("/location", methods=["POST"])
def location():
    token_j=request.json["token"]
    name = request.json["name"]
    country=request.json["country"]
    city=request.json["city"]
    meta=request.json["meta"]
    try:
        cur = get_db().cursor()
        sql = f"""SELECT id,company_api_key FROM company WHERE company_api_key='{token_j}';"""
        cur.execute(sql)
        ans = cur.fetchall()
        print(token_j)
        if(ans[0][1] == token_j):
            id_company=ans[0][0]
            cur = get_db().cursor()
            sql_insert = f"""
            INSERT INTO location (location_name,location_country,location_city,location_meta,company_id)
            VALUES ('{name}','{country}','{city}','{meta}','{id_company}');"""
            cur.execute(sql_insert)
            get_db().commit()
            

            return jsonify({"message": "Locación agregada correctamente."})
        else:
            return jsonify({"message": "API KEY not found."})
    except:
        return make_response({"error": "Invalid token"}, 401)

@app.route("/location", methods=["GET"])
def listlocation():
    token = request.args.get('token')
    try:
        cur = get_db().cursor()
        sql = f"""SELECT * FROM company WHERE company_api_key='{token}';"""
        cur.execute(sql)
        ans = cur.fetchall()
        if(ans[0][2] == token):
            print(ans[0][2])
            return jsonify({"message": "You are in the protected area"})
        else:
            return jsonify({"message": "API KEY not found."})
    except:
        return make_response({"error": "Invalid token"}, 401)

if __name__ == "__main__":
    app.run(debug=True)
