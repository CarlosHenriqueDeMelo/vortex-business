from flask import Blueprint, request, jsonify
from database.database import get_connection

vendas_bp = Blueprint('vendas', __name__)

@vendas_bp.route('/vendas', methods=['GET'])
def listar_vendas():
    conn = get_connection()
    vendas = conn.execute('SELECT * FROM vendas').fetchall()
    conn.close()
    return jsonify([dict(c) for c in vendas])

@vendas_bp.route('/vendas', methods=['POST'])
def criar_venda():
    dados = request.json
    conn = get_connection()
    conn.execute(
        'INSERT INTO vendas (empresa_id, cliente_id, forma_pagamento, desconto, total, cidade, telefone, observacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (dados['empresa_id'], dados.get('cliente_id'), dados['forma_pagamento'], dados.get('desconto', 0), dados['total'], dados.get('cidade'), dados.get('telefone'), dados.get('observacao'))
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Venda registrada com sucesso!'}), 201
