"""
Pruebas unitarias y de integración ligera para la aplicación Flask.
La base de datos MySQL se simula con mocks; no requiere Docker en ejecución local.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

os.environ.setdefault("MYSQL_HOST", "localhost")
os.environ.setdefault("MYSQL_USER", "testuser")
os.environ.setdefault("MYSQL_PASSWORD", "testpass")
os.environ.setdefault("MYSQL_DATABASE", "testdb")

import app as flask_app  # noqa: E402


def _mock_db_connection(for_insert=False, fetch_rows=None):
    # Construye conexión y cursor simulados para INSERT o SELECT según fetch_rows.
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    if fetch_rows is not None:
        mock_cursor.fetchall.return_value = fetch_rows
    return mock_conn, mock_cursor


class TestRutasPublicas(unittest.TestCase):
    def setUp(self):
        self.client = flask_app.app.test_client()

    # GET /: responde 200 y el texto de comprobación del servicio Flask.
    def test_raiz_devuelve_mensaje_flask(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Flask funcionando", r.get_data(as_text=True))

    # GET /home: carga la página de inicio con el mensaje de inscripciones.
    def test_home_renderiza(self):
        r = self.client.get("/home")
        self.assertEqual(r.status_code, 200)
        self.assertIn("INSCRIPCIONES", r.get_data(as_text=True))

    # GET /register: muestra el formulario con campos nombre y email esperados.
    def test_register_get_muestra_formulario(self):
        r = self.client.get("/register")
        self.assertEqual(r.status_code, 200)
        body = r.get_data(as_text=True)
        self.assertIn("Formulario de Registro", body)
        self.assertIn('name="nombre"', body)
        self.assertIn('type="email"', body)


class TestApiStatus(unittest.TestCase):
    def setUp(self):
        self.client = flask_app.app.test_client()

    # /api/status con MySQL OK: JSON online, database connected y versión 1.0.0.
    @patch("app.mysql.connector.connect")
    def test_status_bd_conectada(self, mock_connect):
        mock_connect.return_value = MagicMock()
        r = self.client.get("/api/status")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data.get("status"), "online")
        self.assertEqual(data.get("database"), "connected")
        self.assertEqual(data.get("version"), "1.0.0")

    # /api/status si falla la conexión: HTTP 500 y database error en el JSON.
    @patch("app.mysql.connector.connect")
    def test_status_bd_error_http_500(self, mock_connect):
        mock_connect.side_effect = Exception("connection refused")
        r = self.client.get("/api/status")
        self.assertEqual(r.status_code, 500)
        data = r.get_json()
        self.assertEqual(data.get("database"), "error")
        self.assertIn("error", data)


class TestRegistroPost(unittest.TestCase):
    def setUp(self):
        self.client = flask_app.app.test_client()

    # POST /register válido: página de éxito, execute y commit sobre el mock de BD.
    @patch("app.get_db_connection")
    def test_registro_exitoso_con_datos_validos(self, mock_get_conn):
        mock_conn, mock_cursor = _mock_db_connection(for_insert=True)
        mock_get_conn.return_value = mock_conn
        r = self.client.post(
            "/register",
            data={
                "nombre": "María Pérez",
                "email": "maria@ejemplo.com",
                "telefono": "3001234567",
                "programa": "ingenieria",
                "comentarios": "Interesada en becas",
                "terminos": "on",
            },
        )
        self.assertEqual(r.status_code, 200)
        text = r.get_data(as_text=True)
        self.assertIn("Registro Completado", text)
        self.assertIn("María Pérez", text)
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    # Sin campo comentarios: el INSERT recibe cadena vacía en comentarios.
    @patch("app.get_db_connection")
    def test_comentarios_opcionales_vacios(self, mock_get_conn):
        mock_conn, mock_cursor = _mock_db_connection(for_insert=True)
        mock_get_conn.return_value = mock_conn
        r = self.client.post(
            "/register",
            data={
                "nombre": "Juan",
                "email": "juan@test.com",
                "telefono": "1",
                "programa": "derecho",
                "terminos": "on",
            },
        )
        self.assertEqual(r.status_code, 200)
        args = mock_cursor.execute.call_args[0][1]
        self.assertEqual(args[4], "")

    # Sin checkbox términos: acepta_terminos en el INSERT debe ser False.
    @patch("app.get_db_connection")
    def test_acepta_terminos_false_si_no_se_envia_checkbox(self, mock_get_conn):
        mock_conn, mock_cursor = _mock_db_connection(for_insert=True)
        mock_get_conn.return_value = mock_conn
        r = self.client.post(
            "/register",
            data={
                "nombre": "SinCheck",
                "email": "s@c.com",
                "telefono": "1",
                "programa": "medicina",
            },
        )
        self.assertEqual(r.status_code, 200)
        args = mock_cursor.execute.call_args[0][1]
        self.assertIs(args[5], False)

    # Fallo al conectar/guardar: la respuesta muestra error al guardar el registro.
    @patch("app.get_db_connection")
    def test_error_bd_muestra_mensaje_en_registro(self, mock_get_conn):
        mock_get_conn.side_effect = Exception("Table 'registros' doesn't exist")
        r = self.client.post(
            "/register",
            data={
                "nombre": "X",
                "email": "x@x.com",
                "telefono": "1",
                "programa": "contabilidad",
                "terminos": "on",
            },
        )
        self.assertEqual(r.status_code, 200)
        text = r.get_data(as_text=True)
        self.assertIn("Error al guardar el registro", text)

    # POST incompleto (faltan campos): se captura el error y se informa al usuario.
    def test_campo_faltante_keyerror_manejado(self):
        r = self.client.post(
            "/register",
            data={"email": "solo@email.com"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("Error al guardar el registro", r.get_data(as_text=True))


class TestVerRegistros(unittest.TestCase):
    def setUp(self):
        self.client = flask_app.app.test_client()

    # GET /records con filas mock: el HTML incluye los datos de los registros.
    @patch("app.get_db_connection")
    def test_lista_registros_con_datos(self, mock_get_conn):
        filas = [
            {
                "id": 2,
                "nombre": "B",
                "email": "b@b.com",
                "telefono": "2",
                "programa": "derecho",
                "comentarios": "",
                "acepta_terminos": 1,
                "fecha_registro": "2026-03-29 10:00:00",
            },
            {
                "id": 1,
                "nombre": "A",
                "email": "a@a.com",
                "telefono": "1",
                "programa": "ingenieria",
                "comentarios": "hola",
                "acepta_terminos": 1,
                "fecha_registro": "2026-03-28 10:00:00",
            },
        ]
        mock_conn, mock_cursor = _mock_db_connection(fetch_rows=filas)
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        r = self.client.get("/records")
        self.assertEqual(r.status_code, 200)
        text = r.get_data(as_text=True)
        self.assertIn("B", text)
        self.assertIn("A", text)

    # Lista vacía: mensaje indicando que no hay registros en la base de datos.
    @patch("app.get_db_connection")
    def test_lista_vacia_mensaje_informativo(self, mock_get_conn):
        mock_conn, mock_cursor = _mock_db_connection(fetch_rows=[])
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        r = self.client.get("/records")
        self.assertEqual(r.status_code, 200)
        self.assertIn("No se encontraron registros", r.get_data(as_text=True))

    # Error al consultar registros: plantilla de error con mensaje y alerta.
    @patch("app.get_db_connection")
    def test_error_consulta_renderiza_error_html(self, mock_get_conn):
        mock_get_conn.side_effect = RuntimeError("DB down")
        r = self.client.get("/records")
        self.assertEqual(r.status_code, 200)
        text = r.get_data(as_text=True)
        self.assertIn("Error al consultar los registros", text)
        self.assertIn("alert-danger", text)


if __name__ == "__main__":
    unittest.main()
