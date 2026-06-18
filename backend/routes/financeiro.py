from flask import Blueprint, request, jsonify
from database.database import get_connection

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
        'INSERT INTO financeiro (empresa_id, cliente_id, descricao, tipo, valor, vencimento, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (dados['empresa_id'], dados.get('cliente_id'), dados['descricao'], dados['tipo'], dados['valor'], dados.get('vencimento'), dados.get('status', 'pendente'))
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Lançamento criado com sucesso!'}), 201

@financeiro_bp.route('/financeiro/<int:id>/pagar', methods=['POST'])
def pagar_lancamento(id):
    dados = request.json or {}
    conn = get_connection()
    lancamento = conn.execute('SELECT * FROM financeiro WHERE id = ?', (id,)).fetchone()
    if not lancamento:
        conn.close()
        return jsonify({'mensagem': 'Lancamento nao encontrado'}), 404
    conn.execute("UPDATE financeiro SET status = 'pago' WHERE id = ?", (id,))
    if dados.get('cliente_id') and lancamento['valor']:
        conn.execute(
            'UPDATE clientes SET divida_atual = MAX(0, divida_atual - ?) WHERE id = ?',
            (lancamento['valor'], dados['cliente_id'])
        )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Marcado como pago!'}), 200
