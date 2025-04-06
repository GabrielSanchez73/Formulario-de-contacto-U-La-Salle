from flask import Flask, jsonify
import os
import mysql.connector

app = Flask(__name__)

# Ruta raíz
@app.route('/')
def hello():
    return "¡Flask funcionando en Docker!"

# Endpoint que devuelve JSON
@app.route('/api/status')
def status():
    try:
        # Verificar conexión a MySQL
        conn = mysql.connector.connect(
            host=os.environ.get('MYSQL_HOST', 'db'),
            user=os.environ.get('MYSQL_USER', 'user'),
            password=os.environ.get('MYSQL_PASSWORD', 'password'),
            database=os.environ.get('MYSQL_DATABASE', 'flask_app_db')
        )
        conn.close()
        return jsonify({
            "status": "online",
            "database": "connected",
            "version": "1.0.0"
        })
    except Exception as e:
        return jsonify({
            "status": "online",
            "database": "error",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
