from flask import Flask
from flask_cors import CORS
from database.database import inicializar_banco
from routes.empresas import empresas_bp
from routes.clientes import clientes_bp
from routes.produtos import produtos_bp
from routes.vendas import vendas_bp
from routes.fornecedores import fornecedores_bp
from routes.financeiro import financeiro_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(empresas_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(produtos_bp)
app.register_blueprint(vendas_bp)
app.register_blueprint(fornecedores_bp)
app.register_blueprint(financeiro_bp)

inicializar_banco()

@app.route('/')
def index():
    return {'status': 'Vortex rodando!'}

if __name__ == '__main__':
    app.run(port=5000, debug=True)
