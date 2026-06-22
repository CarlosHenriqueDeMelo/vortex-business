from flask import Blueprint, request, jsonify
from database.database import get_connection, gerar_uuid, timestamp_atual
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
    agora = timestamp_atual()
    cursor = conn.execute(
        'INSERT INTO vendas (empresa_id, cliente_id, forma_pagamento, desconto, total, cidade, telefone, observacao, uuid, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (dados['empresa_id'], dados.get('cliente_id'), dados['forma_pagamento'], dados.get('desconto', 0), dados['total'], dados.get('cidade'), dados.get('telefone'), dados.get('observacao'), gerar_uuid(), agora)
    )
    venda_id = cursor.lastrowid
    itens = dados.get('itens', [])
    for item in itens:
        conn.execute(
            'INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario, subtotal, uuid, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (venda_id, item['produto_id'], item['quantidade'], item['preco_unitario'], item['subtotal'], gerar_uuid(), agora)
        )
        conn.execute(
            'UPDATE produtos SET quantidade = quantidade - ?, updated_at = ? WHERE id = ?',
            (item['quantidade'], agora, item['produto_id'])
        )
    if dados['forma_pagamento'] == 'Nota' and dados.get('cliente_id'):
        conn.execute(
            'UPDATE clientes SET divida_atual = divida_atual + ?, updated_at = ? WHERE id = ?',
            (dados['total'], agora, dados['cliente_id'])
        )
        dias = dados.get('dias_prazo') or 30
        conn.execute(
            "INSERT INTO financeiro (empresa_id, cliente_id, venda_id, descricao, tipo, valor, vencimento, status, uuid, updated_at) VALUES (?, ?, ?, ?, 'receber', ?, date('now', '+' || ? || ' days'), 'pendente', ?, ?)",
            (dados['empresa_id'], dados['cliente_id'], venda_id, f"Fiado venda #{venda_id}", dados['total'], dias, gerar_uuid(), agora)
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
@vendas_bp.route('/clientes/<int:id>/pagar-fiado', methods=['POST'])
def pagar_fiado(id):
    dados = request.json
    conn = get_connection()
    agora = timestamp_atual()
    conn.execute(
        'UPDATE clientes SET divida_atual = divida_atual - ?, updated_at = ? WHERE id = ?',
        (dados['valor'], agora, id)
    )
    conn.execute(
        "UPDATE financeiro SET status = 'pago', updated_at = ? WHERE cliente_id = ? AND status = 'pendente'",
        (agora, id)
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Fiado marcado como pago!'}), 200
@vendas_bp.route('/vendas/pdf', methods=['GET'])
def pdf_vendas_periodo():
    empresa_id = request.args.get('empresa_id')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')
    conn = get_connection()
    empresa = dict(conn.execute('SELECT * FROM empresas WHERE id = ?', (empresa_id,)).fetchone())
    query = 'SELECT * FROM vendas WHERE empresa_id = ?'
    params = [empresa_id]
    if inicio and fim:
        query += ' AND date(data_venda) BETWEEN date(?) AND date(?)'
        params.extend([inicio, fim])
    vendas = conn.execute(query, params).fetchall()
    conn.close()
    from pdf_generator import gerar_pdf_vendas_periodo
    pdf_path = gerar_pdf_vendas_periodo(empresa, [dict(v) for v in vendas], inicio, fim)
    return jsonify({'pdf': pdf_path})
