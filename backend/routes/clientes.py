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

@clientes_bp.route('/clientes/<int:id>', methods=['DELETE'])
def deletar_clientes(id):
    conn = get_connection()
    conn.execute('DELETE FROM clientes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Cliente deletado com sucesso!'}), 200

@clientes_bp.route('/clientes/<int:id>/pagar-fiado', methods=['POST'])
def pagar_fiado(id):
    dados = request.json
    conn = get_connection()
    conn.execute(
        'UPDATE clientes SET divida_atual = divida_atual - ? WHERE id = ?',
        (dados['valor'], id)
    )
    conn.execute(
        "UPDATE financeiro SET status = 'pago' WHERE cliente_id = ? AND status = 'pendente'",
        (id,)
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Fiado marcado como pago!'}), 200

@clientes_bp.route('/clientes/<int:id>/relatorio', methods=['GET'])
def relatorio_cliente(id):
    conn = get_connection()
    cliente = dict(conn.execute('SELECT * FROM clientes WHERE id = ?', (id,)).fetchone())
    fiados = conn.execute(
        "SELECT f.*, v.data_venda FROM financeiro f LEFT JOIN vendas v ON f.venda_id = v.id WHERE f.cliente_id = ? AND f.tipo = 'receber' AND f.status = 'pendente'",
        (id,)
    ).fetchall()
    conn.close()
    return jsonify({'cliente': cliente, 'fiados': [dict(f) for f in fiados]})

@clientes_bp.route('/clientes/<int:id>/pdf', methods=['GET'])
def pdf_cliente(id):
    empresa_id = request.args.get('empresa_id')
    conn = get_connection()
    cliente = dict(conn.execute('SELECT * FROM clientes WHERE id = ?', (id,)).fetchone())
    empresa = dict(conn.execute('SELECT * FROM empresas WHERE id = ?', (empresa_id,)).fetchone())
    fiados = conn.execute(
        "SELECT f.*, v.data_venda, v.observacao as obs_venda FROM financeiro f LEFT JOIN vendas v ON f.venda_id = v.id WHERE f.cliente_id = ? AND f.tipo = 'receber' AND f.status = 'pendente'",
        (id,)
    ).fetchall()
    fiados_list = []
    for f in fiados:
        fd = dict(f)
        if fd.get('venda_id'):
            itens = conn.execute(
                "SELECT iv.*, p.nome as produto_nome FROM itens_venda iv JOIN produtos p ON iv.produto_id = p.id WHERE iv.venda_id = ?",
                (fd['venda_id'],)
            ).fetchall()
            fd['itens'] = [dict(i) for i in itens]
        else:
            fd['itens'] = []
        fiados_list.append(fd)
    conn.close()
    from pdf_generator import gerar_pdf_cliente
    pdf_path = gerar_pdf_cliente(cliente, fiados_list, empresa)
    return jsonify({'pdf': pdf_path})

@clientes_bp.route('/clientes/<int:id>', methods=['PUT'])
def editar_cliente(id):
    dados = request.json
    conn = get_connection()
    conn.execute(
        'UPDATE clientes SET nome = ?, telefone = ?, cidade = ?, regiao = ? WHERE id = ?',
        (dados['nome'], dados.get('telefone'), dados.get('cidade'), dados.get('regiao'), id)
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Cliente atualizado!'}), 200
