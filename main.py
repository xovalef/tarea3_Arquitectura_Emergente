from flask import Flask, request, jsonify, make_response
import sqlite3
from flask import g
import jwt
from datetime import datetime, timedelta
from json import dumps

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

# Agregar una nueva comañia


@app.route("/company", methods=["POST"])
def company():
    token_j = request.json["token"]
    try:
        data = jwt.decode(token_j, key=KEY, algorithms=['HS256'])
        if data['expiration'] < datetime.utcnow().timestamp():
            return make_response('Token expired', 401)

        nombre_company = request.json["company_name"]
        company_api = jwt.encode({
            "company_name": nombre_company
        }, key=KEY)
        sql_insert = f"""
        INSERT INTO company (company_name,company_api_key)
        VALUES ('{nombre_company}','{company_api}');
        """
        cur = get_db().cursor()
        cur.execute(sql_insert)
        get_db().commit()
        ans = cur.fetchall()

        return jsonify({"message": "Compañia agregada correctamente", "company_api_key": company_api})
    except:
        return make_response({"error": "Invalid token"}, 401)

# Mostrar toda la lista de company


@app.route("/company", methods=["GET"])
def listcompany():
    token = request.args.get('token')  # token admin
    commpany_id = request.args.get('company_id')  # id para obtener 1 compañia
    try:
        if (commpany_id):
            cur = get_db().cursor()
            sql = f"""SELECT * FROM company WHERE company.id='{commpany_id}';"""
            cur.execute(sql)
            ans = cur.fetchall()
            return jsonify({"message": "Listando una company", "Datos company": ans})

        else:
            data = jwt.decode(token, key=KEY, algorithms=['HS256'])
            if data['expiration'] < datetime.utcnow().timestamp():
                return make_response('Token expired', 401)
            cur = get_db().cursor()
            sql = """SELECT * FROM company;"""
            cur.execute(sql)
            ans = cur.fetchall()
            return jsonify({"message": "You are in the protected area", "Lista": ans})

    except:
        return make_response({"error": "Invalid token"}, 401)

# Update Company


@app.route("/company", methods=["PUT"])
def updatecompany():
    token_j = request.json["token"]  # Token del admin
    id_company = request.json["id"]  # id de la compañia
    nombre = request.json["company_name"]  # nombre compañia
    try:
        data = jwt.decode(token_j, key=KEY, algorithms=['HS256'])
        if data['expiration'] < datetime.utcnow().timestamp():
            return make_response('Token expired', 401)
        cur = get_db().cursor()
        sql_up = f"""UPDATE company SET company_name = '{nombre}' WHERE id='{id_company}';"""
        cur.execute(sql_up)
        get_db().commit()
        return jsonify({"messaje": "Actualizacion completada."})
    except:
        return make_response({"error": "Invalid token"}, 401)


# Agregar una nueva locación


@app.route("/location", methods=["POST"])
def location():
    token_j = request.json["token"]  # company_api_key
    name = request.json["name"]
    country = request.json["country"]
    city = request.json["city"]
    meta = request.json["meta"]
    try:
        cur = get_db().cursor()
        sql = f"""SELECT id,company_api_key FROM company WHERE company_api_key='{token_j}';"""
        cur.execute(sql)
        ans = cur.fetchall()
        print(token_j)
        if (ans[0][1] == token_j):
            id_company = ans[0][0]
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

# Mostrar lista completa


@app.route("/location", methods=["GET"])
def listlocation():
    token = request.args.get('token')  # company_apy_key
    try:
        cur = get_db().cursor()
        sql = f"""SELECT l.*
                FROM location as l,company as c
                WHERE l.company_id=c.id
                AND c.company_api_key='{token}';"""
        cur.execute(sql)
        ans = cur.fetchall()
        if (len(ans) != 0):
            return jsonify({"message": "You are in the protected area", "Lista location": ans})
        else:
            return jsonify({"message": "API KEY not found."})
    except:
        return make_response({"error": "Invalid token"}, 401)


@app.route("/sensor", methods=["GET"])
def listsensors():
    token = request.args.get('token')
    cur = get_db().cursor()
    sql = f"""
    SELECT sensor.* FROM sensor, location, company
        WHERE company_api_key='{token}'
        AND company.id = location.company_id
        AND location.id = sensor.location_id;"""
    cur.execute(sql)
    ans = cur.fetchall()
    return jsonify({"sensors": ans})


@app.route("/sensor", methods=["POST"])
def create_sensor():
    company_api_key = request.json["token"]
    location_id = request.json["location_id"]
    sql_query = f"""
        SELECT company_api_key FROM company, location
        WHERE company.id = location.company_id
        AND location.id = '{location_id}';
    """
    cur = get_db().cursor()
    cur.execute(sql_query)
    ans = cur.fetchall()
    if len(ans) == 0:
        return make_response({"message": "Location not found"}, 404)
    if ans[0][0] != company_api_key:
        return make_response({"message": "Invalid company API key"}, 401)

    sensor_name = request.json["sensor_name"]
    sensor_category = request.json["sensor_category"]
    sensor_meta = request.json["sensor_meta"]
    sensor_api_key = jwt.encode({
        "sensor_name": sensor_name,
        "location_id": location_id,
        "sensor_category": sensor_category,
        "sensor_meta": sensor_meta,
    }, key=KEY)
    cur = get_db().cursor()
    sql_insert = f"""
        INSERT INTO sensor (sensor_name, sensor_category, sensor_meta, location_id, sensor_api_key)
        VALUES ('{sensor_name}', '{sensor_category}',
                '{sensor_meta}', '{location_id}', '{sensor_api_key}');
    """
    cur.execute(sql_insert)
    get_db().commit()
    return jsonify({"message": "Sensor agregado correctamente.", "sensor_api_key": sensor_api_key})


@app.route("/sensor_data", methods=["POST"])
def create_sensor_data():
    sensor_api_key = request.json["token"]
    sensor_data = request.json["data"]
    sql_query = f"""
        SELECT id FROM sensor
        WHERE sensor_api_key = '{
            sensor_api_key
        }';
    """
    cur = get_db().cursor()
    cur.execute(sql_query)
    ans = cur.fetchall()
    sensor_id = ans[0][0]
    if len(ans) == 0:
        return make_response({"message": "Sensor not found"}, 404)

    cur = get_db().cursor()
    sql_insert = f"""
        INSERT INTO sensor_data (sensor_id, data)
        VALUES ('{sensor_id}', '{dumps(sensor_data)}');
    """
    cur.execute(sql_insert)
    get_db().commit()
    return jsonify({"message": "Sensor data agregado correctamente."})


@app.route("/sensor_data", methods=["GET"])
def get_sensor_data():
    sensor_api_key = request.args.get('token')
    sql_query = f"""
        SELECT id FROM sensor
        WHERE sensor_api_key = '{
            sensor_api_key
        }';
    """
    cur = get_db().cursor()
    cur.execute(sql_query)
    ans = cur.fetchall()
    sensor_id = ans[0][0]
    if len(ans) == 0:
        return make_response({"message": "Sensor not found"}, 404)

    sql_query = f"""
        SELECT id, sensor_id, data FROM sensor_data
        WHERE sensor_id = '{sensor_id}';
    """
    cur = get_db().cursor()
    cur.execute(sql_query)
    ans = cur.fetchall()
    return jsonify({"data": ans})


# Actualizar Sensor
@app.route("/sensor", methods=["PUT"])
def update_sensor():
    sensor_token = request.json["sensor_token"]
    name = request.json["sensor_name"]
    category = request.json["sensor_category"]
    meta = request.json["sensor_meta"]
    try:
        cur = get_db().cursor()
        sql_up = f"""UPDATE sensor SET sensor_name = '{name}', sensor_category='{category}',sensor_meta='{meta}' 
        WHERE sensor_api_key='{sensor_token}';"""
        cur.execute(sql_up)
        get_db().commit()
        return jsonify({"messaje": "Actualizacion completada."})
    except:
        return make_response({"error": "Invalid token"}, 401)

# Delete Sensor
@app.route("/sensor",methods=["DELETE"])
def delete_sensor():
    try:
        sensor_token = request.json["sensor_token"]
        cur = get_db().cursor()
        sql_delete=f"""DELETE FROM sensor WHERE sensor_api_key='{sensor_token}';"""
        cur.execute(sql_delete)
        get_db().commit()
        return jsonify({"message":"Eliminacion completada"})
    except:
        return make_response({"error": "Invalid token"}, 401)

if __name__ == "__main__":
    app.run(debug=True)
