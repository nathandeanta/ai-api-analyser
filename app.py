import hashlib

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

from config import DevelopmentConfig, ProductionConfig
from db import init_db, conect_database

app = Flask(__name__)

environment = 'development'

if environment == 'development':
    app.config.from_object(DevelopmentConfig)
elif environment == 'production':
    app.config.from_object(ProductionConfig)
else:
    raise ValueError("Unrecognized environment")

jwt = JWTManager(app)

init_db()
@app.route('/')
def index():
    return 'Hello World!'
@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.json.get('username', None)
        password = request.json.get('password', None)

        if username is None or username == '' or password is None or password == '':
            return jsonify({'error': 'username and password fields are mandatory'}), 400

        conn = conect_database()
        cursor = conn.cursor()

        password_md5 = hashlib.md5(password.encode()).hexdigest()

        cursor.execute('SELECT * FROM users WHERE username=? AND password= ?', (username, password_md5))
        user = cursor.fetchone()

        conn.close()

        if user:
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"msg": "Invalid credentials"}), 401
    except Exception as e:

        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()


@app.route('/theft', methods=['POST'])
@jwt_required()
def theft():
    desc = request.json.get('desc', None)

    if desc is None or desc == '':
        return jsonify({'error': 'desc is mandatory'}), 400

    try:

        conn = conect_database()
        cursor = conn.cursor()

        cursor.execute('SELECT description, type FROM theft')
        rows = cursor.fetchall()

        descriptions = [row[0] for row in rows]
        labels = [row[1] for row in rows]

        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(descriptions)

        X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2, random_state=42)

        model = MultinomialNB()
        model.fit(X_train, y_train)

        new_description_vectorized = vectorizer.transform([desc])
        prediction = model.predict(new_description_vectorized)

        return jsonify({"prediction": prediction[0]})
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        conn.close()

@app.route('/create/theft', methods=['POST'])
@jwt_required()
def create_theft():
    try:
        desc = request.json.get('desc', None)
        type = request.json.get('type', None)

        if desc is None or desc == '' or type is None or type == '':
            return jsonify({'error': 'desc and type fields are mandatory'}), 400

        if type not in ["Roubo", "Furto Simples", "Furto Qualificado"]:
            return jsonify({'error': 'type Roubo, Furto Simples and Furto Qualificado'}), 400

        conn = conect_database()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM theft WHERE type=? AND description= ?', (type, desc))
        theft = cursor.fetchone();

        if theft:
            return jsonify({'error': 'is already registered'}), 400

        cursor.execute('INSERT INTO theft (description, type) VALUES (?, ?)', (desc,type))
        conn.commit()

        return jsonify({"msg": "sucess"})
    except Exception as e:

        return jsonify({"error": str(e)}), 500

    finally:

        conn.close()

@app.route('/list/theft', methods=['GET'])
@jwt_required()
def list_theft():
    try:
        conn = conect_database()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM theft')
        theft = cursor.fetchall()

        theft_list = [{"id": row[0],"type": row[1], "description": row[2]} for row in theft]

        return jsonify({"theft_list": theft_list})

    except Exception as e:

        return jsonify({"error": str(e)}), 500

    finally:

        conn.close()

@app.route('/details/theft/<int:theft_id>', methods=['GET'])
@jwt_required()
def details_theft(theft_id):
    try:
        conn = conect_database()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM theft WHERE id = ?', (theft_id,))
        theft_data = cursor.fetchone()

        if theft_data:
            theft_details = {
                "id": theft_data[0],
                "type": theft_data[1],
                "description": theft_data[2]

            }
            return jsonify({"theft_details": theft_details})
        else:
            return jsonify({"message": "Item not found."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()
@app.route('/delete/theft/<int:theft_id>', methods=['DELETE'])
@jwt_required()
def delete_theft(theft_id):
    try:
        conn = conect_database()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM theft WHERE id = ?', (theft_id,))
        conn.commit()

        return jsonify({"message": "Successfully deleted!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()
@app.route('/update/theft/<int:theft_id>', methods=['PUT'])
@jwt_required()
def update_theft(theft_id):
    try:
        conn = conect_database()
        cursor = conn.cursor()

        desc = request.json.get('desc', None)
        type = request.json.get('type', None)

        if desc is None or desc == '' or type is None or type == '':
            return jsonify({'error': 'desc and type fields are mandatory'}), 400

        if type not in ["Roubo", "Furto Simples", "Furto Qualificado"]:
            return jsonify({'error': 'type Roubo, Furto Simples and Furto Qualificado'}), 400

        cursor.execute('UPDATE theft SET type = ?, description = ? WHERE id = ?', (type, desc, theft_id))
        conn.commit()

        return jsonify({"message": "Updated successfully!"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
