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

@produtos_bp.route('/produtos/<int:id>', methods=['PUT'])
def editar_produto(id):
    dados = request.json
    conn = get_connection()
    conn.execute(
        'UPDATE produtos SET nome = ?, categoria = ?, unidade = ?, preco_custo = ?, preco_venda = ?, quantidade_minima = ? WHERE id = ?',
        (dados['nome'], dados.get('categoria'), dados.get('unidade'), dados.get('preco_custo'), dados.get('preco_venda'), dados.get('quantidade_minima'), id)
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Produto atualizado com sucesso!'}), 200

@produtos_bp.route('/produtos/<int:id>', methods=['DELETE'])
def deletar_produto(id):
    conn = get_connection()
    conn.execute('DELETE FROM produtos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Produto deletado com sucesso!'}), 200

@produtos_bp.route('/produtos/pdf', methods=['GET'])
def pdf_estoque():
    empresa_id = request.args.get('empresa_id')
    conn = get_connection()
    empresa = dict(conn.execute('SELECT * FROM empresas WHERE id = ?', (empresa_id,)).fetchone())
    produtos = conn.execute('SELECT * FROM produtos WHERE empresa_id = ?', (empresa_id,)).fetchall()
    conn.close()
    from pdf_generator import gerar_pdf_estoque
    pdf_path = gerar_pdf_estoque(empresa, [dict(p) for p in produtos])
    return jsonify({'pdf': pdf_path})
