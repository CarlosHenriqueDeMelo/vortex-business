from flask import Blueprint, request, jsonify
from database.database import get_connection

produtos_bp = Blueprint('produtos', __name__)

@produtos_bp.route('/produtos', methods=['GET'])
def listar_produtos():
    conn = get_connection()
    produtos = conn.execute('SELECT * FROM produtos').fetchall()
    conn.close()
    return jsonify([dict(c) for c in produtos])

@produtos_bp.route('/produtos', methods=['POST'])
def criar_produtos():
    dados = request.json
    conn = get_connection()
    conn.execute(
        'INSERT INTO produtos (empresa_id, nome, categoria, unidade, preco_custo, preco_venda, quantidade, quantidade_minima) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (dados['empresa_id'], dados['nome'], dados.get('categoria'), dados.get('unidade'), dados.get('preco_custo'), dados.get('preco_venda'), dados.get('quantidade'), dados.get('quantidade_minima'))
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Produto cadastrado com sucesso!'}), 201

@produtos_bp.route('/produtos/<int:id>', methods=['DELETE'])
def deletar_produto(id):
    conn = get_connection()
    conn.execute('DELETE FROM produtos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Produto deletado com sucesso!'}), 200
