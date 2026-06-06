from flask import Blueprint, request, jsonify
from database.database import get_connection

financeiro_bp = Blueprint('financeiro', __name__)

@financeiro_bp.route('/financeiro', methods=['GET'])
def listar_financeiro():
    conn = get_connection()
    financeiro = conn.execute('SELECT * FROM financeiro').fetchall()
    conn.close()
    return jsonify([dict(c) for c in financeiro])

@financeiro_bp.route('/financeiro', methods=['POST'])
def criar_financeiro():
    dados = request.json
    conn = get_connection()
    conn.execute(
        'INSERT INTO financeiro (empresa_id, descricao, tipo, valor, vencimento) VALUES (?, ?, ?, ?, ?)',
        (dados['empresa_id'], dados['descricao'], dados['tipo'], dados['valor'], dados.get('vencimento'))
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Lançamento criado com sucesso!'}), 201
