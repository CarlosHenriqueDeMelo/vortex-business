from flask import Flask, jsonify, request
from flask_cors import CORS
from database.database import inicializar_banco
from routes.empresas import empresas_bp
from routes.clientes import clientes_bp
from routes.produtos import produtos_bp
from routes.vendas import vendas_bp
from routes.fornecedores import fornecedores_bp
from routes.financeiro import financeiro_bp
from routes.entradas import entrada_bp
from routes.sync import sync_bp
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
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # sync completo cabe folgado

LOCAIS = ('127.0.0.1', '::1', '::ffff:127.0.0.1')

@app.before_request
def proteger_api():
    """O servidor escuta na rede (para o celular sincronizar), entao:
    - de outro aparelho so e permitido /sync/*, e as rotas exigem o token;
    - do proprio PC, bloqueia paginas web externas (Origin http/https)."""
    if request.method == 'OPTIONS':
        return None
    if request.remote_addr not in LOCAIS:
        if not request.path.startswith('/sync/'):
            return jsonify({'mensagem': 'Acesso negado'}), 403
        return None
    origem = request.headers.get('Origin')
    if origem and origem.startswith(('http://', 'https://')) and not origem.startswith(('http://127.0.0.1', 'http://localhost')):
        return jsonify({'mensagem': 'Origem nao permitida'}), 403
    return None

CORS(app)

app.register_blueprint(empresas_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(produtos_bp)
app.register_blueprint(vendas_bp)
app.register_blueprint(fornecedores_bp)
app.register_blueprint(financeiro_bp)
app.register_blueprint(entrada_bp)
app.register_blueprint(sync_bp)

from database.database import fazer_backup
try:
    fazer_backup()  # backup diario antes de qualquer migracao/uso
except Exception:
    logging.exception('Falha no backup diario')
inicializar_banco()
from database.sync_auth import obter_token
obter_token()  # garante que o token de sincronizacao exista desde a primeira execucao

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
