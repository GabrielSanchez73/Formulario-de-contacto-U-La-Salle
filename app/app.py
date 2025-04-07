from flask import jsonify
from flask import Flask, render_template, request, redirect, url_for
import os
import mysql.connector
from datetime import datetime

app = Flask(__name__)


# Función para obtener conexión a la base de datos
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST', 'db'),
        user=os.environ.get('MYSQL_USER', 'user'),
        password=os.environ.get('MYSQL_PASSWORD', 'password'),
        database=os.environ.get('MYSQL_DATABASE', 'flask_app_db')
    )


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


@app.route('/home')
def home():
    return render_template('home.html')


# @app.route('/register', methods=['GET', 'POST'])
# def registro():
#     if request.method == 'POST':
#         # Aquí procesarías el formulario de registro
#         name = request.form['nombre']
#         email = request.form['email']
#         comment = request.form['comentarios']
#         phone = request.form['telefono']
#         program = request.form['programa']
# 
#         print()
#         print(f"Nombre: {name}, Email: {email}, Comentario: {comment}, Teléfono: {phone}, program: {program}")
#         print()
#         # ...
#         # Después de procesar, podrías redirigir
#         return redirect(url_for('home'))
#     return render_template('registro.html')


@app.route('/register', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form['nombre']
            email = request.form['email']
            telefono = request.form['telefono']
            programa = request.form['programa']
            comentarios = request.form.get('comentarios', '')
            acepta_terminos = 'terminos' in request.form

            # Obtener la fecha actual
            fecha_registro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Conectarse a la base de datos
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insertar datos en la tabla registros
            query = """
            INSERT INTO registros
            (nombre, email, telefono, programa, comentarios, acepta_terminos, fecha_registro) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (nombre, email, telefono, programa, comentarios, acepta_terminos, fecha_registro)

            cursor.execute(query, values)
            conn.commit()

            # Cerrar conexión
            cursor.close()
            conn.close()

            # Redirigir a una página de éxito o mostrar un mensaje
            return render_template('registro_exitoso.html', nombre=nombre)

        except Exception as e:
            # # Manejar errores de la base de datos
            # error_message = f"Error al guardar el registro: {str(e)}"
            # return render_template('registro.html', error=error_message)
            # Imprimir error detallado
            import traceback
            print("ERROR:", str(e))
            print(traceback.format_exc())

            # Manejar errores de la base de datos
            error_message = f"Error al guardar el registro: {str(e)}"
            return render_template('registro.html', error=error_message)

    return render_template('registro.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
