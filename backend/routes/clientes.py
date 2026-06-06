from flask import Blueprint, request, jsonify
from database.database import get_connection

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/clientes', methods=['GET'])
def listar_clientes():
    conn = get_connection()
    clientes = conn.execute('SELECT * FROM clientes').fetchall()
    conn.close()
    return jsonify([dict(c) for c in clientes])

@clientes_bp.route('/clientes', methods=['POST'])
def criar_clientes():
    dados = request.json
    conn = get_connection()
    conn.execute(
        'INSERT INTO clientes (empresa_id, nome, telefone, cidade, regiao) VALUES (?, ?, ?, ?, ?)',
        (dados['empresa_id'], dados['nome'], dados.get('telefone'), dados.get('cidade'), dados.get('regiao'))
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Cliente criado com sucesso!'}), 201
