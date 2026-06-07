from flask import Blueprint, request, jsonify
from database.database import get_connection
from pdf_generator import gerar_pdf_venda

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
    cursor = conn.execute(
        'INSERT INTO vendas (empresa_id, cliente_id, forma_pagamento, desconto, total, cidade, telefone, observacao) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (dados['empresa_id'], dados.get('cliente_id'), dados['forma_pagamento'], dados.get('desconto', 0), dados['total'], dados.get('cidade'), dados.get('telefone'), dados.get('observacao'))
    )
    venda_id = cursor.lastrowid
    itens = dados.get('itens', [])
    for item in itens:
        conn.execute(
            'INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal) VALUES (?, ?, ?, ?, ?)',
            (venda_id, item['produto_id'], item['quantidade'], item['preco_unitario'], item['subtotal'])
        )
        conn.execute(
            'UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?',
            (item['quantidade'], item['produto_id'])
        )
    conn.commit()
    venda = dict(conn.execute('SELECT * FROM vendas WHERE id = ?', (venda_id,)).fetchone())
    empresa = dict(conn.execute('SELECT * FROM empresas WHERE id = ?', (dados['empresa_id'],)).fetchone())
    cliente = None
    if dados.get('cliente_id'):
        row = conn.execute('SELECT * FROM clientes WHERE id = ?', (dados['cliente_id'],)).fetchone()
        if row:
            cliente = dict(row)
    conn.close()
    pdf_path = gerar_pdf_venda(venda, itens, empresa, cliente)
    return jsonify({'mensagem': 'Venda registrada com sucesso!', 'venda_id': venda_id, 'pdf': pdf_path}), 201
