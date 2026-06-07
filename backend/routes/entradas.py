from flask import Blueprint, request, jsonify
from database.database import get_connection

entrada_bp = Blueprint('entrada', __name__)

@entrada_bp.route('/entradas', methods=['GET'])
def listar_entradas():
    conn = get_connection()
    entradas = conn.execute('SELECT * FROM entradas_estoque').fetchall()
    conn.close()
    return jsonify([dict(e) for e in entradas])

@entrada_bp.route('/entradas', methods=['POST'])
def criar_entrada():
    dados = request.json
    conn = get_connection()
    conn.execute(
        'INSERT INTO entradas_estoque (empresa_id, produto_id, fornecedor_id, quantidade, preco_custo, forma_pagamento, observacao) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (dados['empresa_id'], dados['produto_id'], dados.get('fornecedor_id'), dados['quantidade'], dados['preco_custo'], dados.get('forma_pagamento'), dados.get('observacao'))
    )
    conn.execute(
        'UPDATE produtos SET quantidade = quantidade + ? WHERE id = ?',
        (dados['quantidade'], dados['produto_id'])
    )
    conn.execute(
        'UPDATE produtos SET preco_custo = ? WHERE id = ?',
        (dados['preco_custo'], dados['produto_id'])
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Entrada registrada com sucesso!'}), 201
