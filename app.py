from datetime import datetime
from flask import Flask, request, render_template, jsonify
import random
from flask_mysqldb import MySQL
import time
home_data = {'kitchen': {'light': False, 'temp': 20.0, 'brightness': 0, 'heating': True},
             'bathroom': {'light': False, 'temp': 20.4, 'brightness': 0},
             'hallway': {'light': False, 'temp': 19.3, 'brightness': 0},
             'bedroom': {'light': False, 'temp': 21.3, 'brightness': 0},
             'balcony': {'light': False, 'temp': 14.0, 'brightness': 0},
             }

app = Flask(__name__)

# Настройки подключения к MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'new_schema'
mysql = MySQL(app)


def initialize_home_data():
    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT TEMP FROM heat_configuration WHERE id = 0")
        result = cursor.fetchone()
        if result:
            home_data['kitchen']['temp'] = result[0]
            print(f"Initial kitchen temperature: {home_data['kitchen']['temp']}")
        cursor.close()


@app.route('/')
def main():
    return render_template("index.html", **home_data)


@app.route('/<room>/<device>/<action>', methods=['GET', 'POST'])
def proceed(room, device, action):
    if request.method == 'GET':
        if device == 'light' and action == 'toggle':
            home_data[room]['light'] = not home_data[room]['light']
            print(f'Changed {device} in {room} to {home_data[room][device]}')
            return jsonify({'state': home_data[room]['light']})

        if device == 'temp' and action == 'update':
            temp = {}
            for room_name in home_data:
                if room_name != 'kitchen':
                    home_data[room_name]['temp'] += random.random() / 2
                    temp[room_name + "Temp"] = home_data[room_name]['temp']
                    print(f'Changed {device} in {room_name} to {home_data[room_name][device]}')
            return jsonify(temp)

        if device == 'temp' and action == 'getinfo':
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT ON_TEMP FROM heat_configuration WHERE id = 0")
            result1 = cursor.fetchone()
            cursor.execute("SELECT OFF_TEMP FROM heat_configuration WHERE id = 0")
            result2 = cursor.fetchone()
            data = {'on_temp': result1[0],
                    'off_temp': result2[0],
                    'heating': home_data['kitchen']['heating'],
                    'temp': home_data['kitchen']['temp']}
            cursor.close()
            return jsonify(data)

        if device == 'temp' and action == 'gettemp':
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT TEMP FROM heat_configuration WHERE id = 0")
            result = cursor.fetchone()
            cursor.close()
            return jsonify({'temp': result[0]})

    if request.method == 'POST':
        if device == 'light' and action == 'brightness':
            home_data[room]['brightness'] = int(request.form.get('brightness'))
            print(f'Changed {device} in {room} to {home_data[room][action]}')
            return jsonify({'brightness': home_data[room]['brightness']})

        if device == 'temp' and action == 'changethresholds':
            temp_kind = request.form.get('temp_kind')
            temp = float(request.form.get('temp'))
            cursor = mysql.connection.cursor()
            if temp_kind == 'high':
                cursor.execute("SELECT ON_TEMP FROM heat_configuration WHERE id = 0")
                result = cursor.fetchone()
                if result[0] <= temp:
                    cursor.execute("UPDATE heat_configuration SET OFF_TEMP = %s WHERE ID = 0", (temp,))
            elif temp_kind == 'low':
                cursor.execute("SELECT OFF_TEMP FROM heat_configuration WHERE id = 0")
                result = cursor.fetchone()
                if result[0] >= temp:
                    cursor.execute("UPDATE heat_configuration SET ON_TEMP = %s WHERE ID = 0", (temp,))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'temp': temp})

        if device == 'temp' and action == 'update':
            cursor = mysql.connection.cursor()
            if request.form.get('heating') == 'true':
                home_data['kitchen']['temp'] = float(request.form.get('temp')) + random.uniform(0.11, 0.33)
                home_data['kitchen']['heating'] = True
            else:
                home_data['kitchen']['temp'] = float(request.form.get('temp')) + random.uniform(-0.33, -0.11)
                home_data['kitchen']['heating'] = False
            now = datetime.now()
            cursor.execute("UPDATE heat_configuration SET TEMP = %s WHERE ID = 0", (home_data['kitchen']['temp'],))
            cursor.execute("INSERT INTO logs VALUES (NULL, %s, %s, %s, %s)", (now.strftime('%Y-%m-%d %H:%M:%S'),
                                                                              home_data['kitchen']['temp'],"Kitchen","Web"))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'temp': home_data['kitchen']['temp'], 'heating': home_data['kitchen']['heating']})


def start_flask():
    initialize_home_data()
    app.run(host='0.0.0.0', port=5000)
