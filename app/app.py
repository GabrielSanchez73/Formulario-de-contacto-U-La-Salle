from flask import jsonify
from flask import Flask, render_template, request, redirect, url_for
import os
import mysql.connector
from datetime import datetime

app = Flask(__name__)



def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST', 'db'),
        user=os.environ.get('MYSQL_USER', 'user'),
        password=os.environ.get('MYSQL_PASSWORD', 'password'),
        database=os.environ.get('MYSQL_DATABASE', 'flask_app_db')
    )


@app.route('/')
def hello():
    return "¡Flask funcionando en Docker!"


@app.route('/api/status')
def status():
    try:
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


@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            email = request.form['email']
            telefono = request.form['telefono']
            programa = request.form['programa']
            comentarios = request.form.get('comentarios', '')
            acepta_terminos = 'terminos' in request.form

            fecha_registro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn = get_db_connection()
            cursor = conn.cursor()

            query = """
            INSERT INTO registros
            (nombre, email, telefono, programa, comentarios, acepta_terminos, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (nombre, email, telefono, programa, comentarios, acepta_terminos, fecha_registro)

            cursor.execute(query, values)
            conn.commit()

            cursor.close()
            conn.close()

            return render_template('registro_exitoso.html', nombre=nombre)

        except Exception as e:
            import traceback
            print("ERROR:", str(e))
            print(traceback.format_exc())

            error_message = f"Error al guardar el registro: {str(e)}"
            return render_template('registro.html', error=error_message)

    return render_template('registro.html')


@app.route('/records', methods=['GET'])
def ver_registros():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT id, nombre, email, telefono, programa, comentarios,
               acepta_terminos, fecha_registro
        FROM registros
        ORDER BY fecha_registro DESC
        """

        cursor.execute(query)
        registros = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('ver_registros.html', registros=registros)

    except Exception as e:
        import traceback
        print("ERROR en consulta:", str(e))
        print(traceback.format_exc())

        error_message = f"Error al consultar los registros: {str(e)}"
        return render_template('error.html', error=error_message)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
