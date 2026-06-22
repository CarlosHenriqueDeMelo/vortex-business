from flask import Flask, jsonify
from flask_cors import CORS
from database.database import inicializar_banco
from routes.empresas import empresas_bp
from routes.clientes import clientes_bp
from routes.produtos import produtos_bp
from routes.vendas import vendas_bp
from routes.fornecedores import fornecedores_bp
from routes.financeiro import financeiro_bp
from routes.entradas import entrada_bp
import logging
import os
import traceback

log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'vortex.log'),
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s'
)

app = Flask(__name__)
CORS(app)

app.register_blueprint(empresas_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(produtos_bp)
app.register_blueprint(vendas_bp)
app.register_blueprint(fornecedores_bp)
app.register_blueprint(financeiro_bp)
app.register_blueprint(entrada_bp)

inicializar_banco()

@app.errorhandler(500)
def erro_interno(e):
    tb = traceback.format_exc()
    logging.error(f"Erro 500: {tb}")
    print(f"ERRO 500 DETALHADO:\n{tb}")
    return jsonify({'mensagem': 'Erro interno no servidor.', 'detalhe': str(e)}), 500

@app.route('/')
def index():
    return {'status': 'Vortex rodando!'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
