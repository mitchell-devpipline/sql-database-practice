import psycopg2
from flask import Flask, request, jsonify

conn = psycopg2.connect("dbname='users'")
cursor = conn.cursor()


def create_all():
    cursor.execute("""
      CREATE TABLE IF NOT EXISTS Users (
         user_id SERIAL PRIMARY KEY,
         first_name VARCHAR NOT NULL,
         last_name VARCHAR,
         email VARCHAR NOT NULL UNIQUE,
         phone VARCHAR,
         city VARCHAR,
         state VARCHAR,
         org_id int,
         active smallint DEFAULT 0
      );
   """)
    print("Creating tables...")
    conn.commit()


create_all()

app = Flask(__name__)


@app.route('/user/add', methods=['POST'])
def user_add():
    post_data = request.get_json()

    first_name = post_data.get('first_name')
    if not first_name:
        return jsonify("Name is Required"), 400

    last_name = post_data.get('last_name')

    email = post_data.get('email')
    if not email:
        return jsonify("Email is Required and must be Unique"), 400

    phone = post_data.get('phone')
    city = post_data.get('city')
    state = post_data.get('state')
    org_id = post_data.get('org_id')
    active = post_data.get('active')

    cursor.execute("INSERT INTO Users (first_name, last_name, email, phone, city, state, org_id, active) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", [first_name, last_name, email, phone, city, state, org_id, active])
    conn.commit()
    return jsonify(post_data), 200


@app.route('/user/get/<user_id>', methods=["GET"])
def get_user_by_id(user_id):
    cursor.execute("SELECT user_id, first_name, last_name, email, phone, city, state, org_id, active FROM users WHERE user_id = %s", [user_id])
    result = cursor.fetchone()
    if not result:
        return jsonify("User is not in database"), 400

    return jsonify(result), 200


@app.route('/users/get', methods=['GET'])
def get_all_users():

    cursor.execute("Select first_name, last_name, email, phone, city, state, org_id, active FROM Users")
    results = cursor.fetchall()
    if not results:
        return jsonify("No users in DB"), 404

    end_result = []
    for result in results:

        result_dict = {
            'first_name': result[0],
            'last_name': result[1],
            'email': result[2],
            'phone': result[3],
            'city': result[4],
            'state': result[5],
            'org_id': result[6],
            'active': result[7]
        }
        end_result.append(result_dict)

    return jsonify(end_result), 200


@app.route('/user/delete/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    cursor.execute("DELETE FROM Users WHERE user_id = %s", [user_id])
    conn.commit()
    return jsonify("User deleted"), 200


@app.route('/user/activate/<user_id>', methods=['PATCH'])
def activate_user(user_id):
    cursor.execute("UPDATE Users SET active = 1 WHERE user_id = %s", [user_id])
    conn.commit()
    return jsonify("User Active status updated."), 200


@app.route('/user/deactivate/<user_id>', methods=['PATCH'])
def dectivate_user(user_id):
    cursor.execute("UPDATE Users SET active = 0 WHERE user_id = %s", [user_id])
    conn.commit()
    return jsonify("User Active status updated."), 200


if __name__ == "__main__":
    app.run(port="8086", host="0.0.0.0")
