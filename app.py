#Task 1 Setting up Flask Environment and Database Connection
#Created new venv called gym_venv and installed pips for flask, flask-marshmallow, and mysql-connector-python
from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
import mysql.connector
from mysql.connector import Error
from password import my_password


app = Flask(__name__)
ma = Marshmallow(app)
#creates flask application sets up marshmallow

class MemberSchema(ma.Schema):
    name = fields.Str(required=True)
    id = fields.Int(dump_only=True)
    age = fields.Int(required=True)

    class Meta:
        fields = ("name", "id", "age")

class WorkoutSessionSchema(ma.Schema):
    session_id = fields.Int(dump_only=True)
    member_id= fields.Int(required=True)
    session_date = fields.Date(required=True)
    session_time = fields.Str(required=True)
    activity = fields.Str(required=True)

    class Meta:
        fields = ("session_id", "member_id", "session_date", "session_time", "activity")

#Creates classes for our the two SQL Database tables we are connecting too

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

workout_session_schema = WorkoutSessionSchema()
workout_sessions_schema = WorkoutSessionSchema(many=True)

#calls the classes we just defined

def get_db_connection():
    db_name = 'fitness_center_database_assignment'
    user = 'root'
    password = my_password
    host = '127.0.0.1'

    try:
        conn = mysql.connector.connect(
            database = db_name,
            user = user,
            password = password,
            host = host
        )

        return conn
    except Error as e:
        print(f"Error: {e}")
        return None
#Connects to database

@app.route('/')
def home():
    return "Gym Database Assignment"
#Home page

#Task 2 Implementing CRUD Operations for members

@app.route("/members", methods=["GET"])
def get_members():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM Members"

        cursor.execute(query)
        members = cursor.fetchall()

        return members_schema.jsonify(members)

    except Error as e:
        print(f"Error: {e}")
        return jsonify( {"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

'''
Creates a route to retrieve information from the members database and returns a JSON response with serialized data.
Handles any Errors with a JSON response and closes our connection and cursor in the finally block
'''

@app.route("/members", methods=["POST"])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400

    try:
        conn= get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        new_member = (member_data['name'], member_data['age'])
        query = "INSERT INTO Members (name, age) VALUES (%s, %s)"
        
        cursor.execute(query, new_member)
        conn.commit()

        return jsonify({"message": "New member successfully added"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error":"Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
'''
Works similarly to our GET method however this time it is a post mehod and our query now uses INSERT INTO syntax passing a new row into our database
with the raw data we can add using POSTMAN once it is passed through the new_member tuple
'''

@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400

    try:
        conn= get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        updated_member = (member_data['name'], member_data['age'], id)

        query = "UPDATE Members SET Name = %s, Age = %s WHERE id =%s"

        cursor.execute(query, updated_member)
        conn.commit()

        return jsonify({"message": "Member successfully updated"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error":"Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
'''
Route to update name and age through a PUT method in POSTMAN. Uses UPDATE, SET, WHERE syntax in the query and passes through the updated member tuple that intakes the raw data we add in POSTMAN 
'''

@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):

    try:
        conn= get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        member_to_remove = (id,)

        cursor.execute("SELECT * FROM Members WHERE id=%s", member_to_remove)
        member = cursor.fetchone()
        if not member:
            return jsonify({"error": "Member not found"}), 404

        query = "DELETE FROM Members WHERE id=%s"
        cursor.execute(query, member_to_remove) 
        conn.commit()

        return jsonify({"message": "Member successfully removed"}), 200
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error":"Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
'''
Route to delete a member located with a specific member id. It is important to note that this route will not work
unless the member does not have any workout sessions associated with them because the foreign key relationship remains intact.
Much like our PUT method the id we are using is located in the URL and this is what is used in the tuple to delete the member from our database.
'''
#Task 3 Managing Workout Sessions
@app.route("/workoutsessions", methods=["GET"])
def get_workout_sessions():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM WorkoutSessions"

        cursor.execute(query)
        workout_sessions = cursor.fetchall()

        return workout_sessions_schema.jsonify(workout_sessions)

    except Error as e:
        print(f"Error: {e}")
        return jsonify( {"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Route to return all Workout Sessions

@app.route("/workoutsessions", methods=["POST"])
def add_workout_session():
    try:
        workout_session_data = workout_session_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400

    try:
        conn= get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        new_session = (workout_session_data['member_id'], workout_session_data['session_date'], workout_session_data['session_time'], workout_session_data['activity'])
        query = "INSERT INTO WorkoutSessions (member_id, session_date, session_time, activity) VALUES (%s, %s, %s, %s)"
        
        cursor.execute(query, new_session)
        conn.commit()

        return jsonify({"message": "New session successfully added"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error":"Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

#Route to add a Workout Session

@app.route("/workoutsessions/<int:session_id>", methods=["PUT"])
def update_workout_session(session_id):
    try:
        workout_session_data = workout_session_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400

    try:
        conn= get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        updated_workout = (workout_session_data['member_id'], workout_session_data['session_date'], workout_session_data['session_time'], workout_session_data['activity'], session_id)

        query = "UPDATE WorkoutSessions SET member_id = %s, session_date = %s, session_time = %s, activity = %s WHERE session_id =%s"

        cursor.execute(query, updated_workout)
        conn.commit()

        return jsonify({"message": "Workout successfully updated"}), 201
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error":"Internal Server Error"}), 500
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

#Route to update a Workout Session

@app.route("/workoutsessions_by_member", methods=["POST"])
def workout_sessions_by_member():
    try:
        member = request.json.get('member')
        
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor(dictionary=True)
        query = "SELECT ws.session_id, ws.member_id, ws.session_date, ws.session_time, ws.activity, m.name FROM WorkoutSessions ws, Members m WHERE m.id = ws.member_id AND m.name =%s"
        member_id_input = (member,)

        cursor.execute(query, member_id_input)
        workouts = cursor.fetchall()

        return workout_sessions_schema.jsonify(workouts)

    except Error as e:
        print(f"Error: {e}")
        return jsonify( {"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Looks up workout sessions for a specific member name entered into POSTMAN raw data body

if __name__ == '__main__':
    app.run(debug=True)
#runs flask application
