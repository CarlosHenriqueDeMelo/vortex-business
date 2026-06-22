from flask import Blueprint, request, jsonify
from database.database import get_connection, gerar_uuid, timestamp_atual
financeiro_bp = Blueprint('financeiro', __name__)
@financeiro_bp.route('/financeiro', methods=['GET'])
def listar_financeiro():
    conn = get_connection()
    lancamentos = conn.execute('SELECT * FROM financeiro').fetchall()
    conn.close()
    return jsonify([dict(l) for l in lancamentos])
@financeiro_bp.route('/financeiro', methods=['POST'])
def criar_financeiro():
    dados = request.json
    conn = get_connection()
    conn.execute(
        'INSERT INTO financeiro (empresa_id, cliente_id, descricao, tipo, valor, vencimento, status, uuid, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (dados['empresa_id'], dados.get('cliente_id'), dados['descricao'], dados['tipo'], dados['valor'], dados.get('vencimento'), dados.get('status', 'pendente'), gerar_uuid(), timestamp_atual())
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Lançamento criado com sucesso!'}), 201
@financeiro_bp.route('/financeiro/<int:id>/pagar', methods=['POST'])
def pagar_lancamento(id):
    dados = request.json or {}
    conn = get_connection()
    agora = timestamp_atual()
    lancamento = conn.execute('SELECT * FROM financeiro WHERE id = ?', (id,)).fetchone()
    if not lancamento:
        conn.close()
        return jsonify({'mensagem': 'Lancamento nao encontrado'}), 404
    conn.execute("UPDATE financeiro SET status = 'pago', updated_at = ? WHERE id = ?", (agora, id))
    if dados.get('cliente_id') and lancamento['valor']:
        conn.execute(
            'UPDATE clientes SET divida_atual = MAX(0, divida_atual - ?), updated_at = ? WHERE id = ?',
            (lancamento['valor'], agora, dados['cliente_id'])
        )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Marcado como pago!'}), 200
@financeiro_bp.route('/financeiro/pdf', methods=['GET'])
def pdf_financeiro_relatorio():
    empresa_id = request.args.get('empresa_id')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')
    conn = get_connection()
    empresa = dict(conn.execute('SELECT * FROM empresas WHERE id = ?', (empresa_id,)).fetchone())
    query = 'SELECT * FROM financeiro WHERE empresa_id = ?'
    params = [empresa_id]
    if inicio and fim:
        query += ' AND date(vencimento) BETWEEN date(?) AND date(?)'
        params.extend([inicio, fim])
    lancamentos = conn.execute(query, params).fetchall()
    conn.close()
    from pdf_generator import gerar_pdf_financeiro
    pdf_path = gerar_pdf_financeiro(empresa, [dict(l) for l in lancamentos], inicio, fim)
    return jsonify({'pdf': pdf_path})
