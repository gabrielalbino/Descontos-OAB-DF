from flask import Flask
from flask_cors import CORS
from server.routes import routes_bp
from flask_socketio import SocketIO
from server.database import create_tables

app = Flask(__name__)

# Configurar CORS para permitir localhost:3000
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Inicialize o SocketIO
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

# Configure o SocketIO no módulo de rotas
from server.routes import init_socketio
init_socketio(socketio)

# Registra as rotas
app.register_blueprint(routes_bp)

if __name__ == "__main__":
    create_tables()
    socketio.run(app, host="0.0.0.0", port=5001, allow_unsafe_werkzeug=True)