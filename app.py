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


@app.route('/theft', methods=['POST'])
@jwt_required()
def theft():
    desc = request.json.get('desc', None)

    if desc is None or desc == '':
        return jsonify({'error': 'desc is mandatory'}), 400

    try:

        descriptions = [
            "Roubo no metrô com ameaça.",
            "Furto simples enquanto caminhava, sem vestígios.",
            "Furto qualificado com arrombamento e destruição.",
            "Roubo roubaram meu celular, o ladrao estava armado",
            "Roubo em um café com violência.",
            "Furto simples, celular desapareceu sem vestígios.",
            "Furto simples, me roubaram e eu nao vi.",
            "Furto simples, estava andando pela rua e me roubaram e eu nem senti.",
            "Furto simples, deixei o celular encima da mesa e quando fui perceber nao estava mais la.",
        ]

        labels = ["Roubo", "Furto Simples", "Furto Qualificado", "Roubo", "Roubo", "Furto Simples", "Furto Simples",
                  "Furto Simples", "Furto Simples"]

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


if __name__ == '__main__':
    app.run(debug=True)
