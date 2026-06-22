from flask import Blueprint, request, jsonify
from database.database import get_connection, gerar_uuid, timestamp_atual
fornecedores_bp = Blueprint('fornecedores', __name__)
@fornecedores_bp.route('/fornecedores', methods=['GET'])
def listar_fornecedores():
    conn = get_connection()
    fornecedores = conn.execute('SELECT * FROM fornecedores').fetchall()
    conn.close()
    return jsonify([dict(c) for c in fornecedores])
@fornecedores_bp.route('/fornecedores', methods=['POST'])
def criar_fornecedores():
    dados = request.json
    conn = get_connection()
    conn.execute(
        'INSERT INTO fornecedores (empresa_id, nome, categoria, telefone, email, uuid, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (dados['empresa_id'], dados['nome'], dados.get('categoria'), dados.get('telefone'), dados.get('email'), gerar_uuid(), timestamp_atual())
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Fornecedor criado com sucesso!'}), 201
@fornecedores_bp.route('/fornecedores/<int:id>', methods=['DELETE'])
def deletar_fornecedor(id):
    conn = get_connection()
    conn.execute('DELETE FROM fornecedores WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Fornecedor deletado com sucesso!'}), 200
@fornecedores_bp.route('/fornecedores/<int:id>', methods=['PUT'])
def editar_fornecedor(id):
    dados = request.json
    conn = get_connection()
    conn.execute(
        'UPDATE fornecedores SET nome = ?, categoria = ?, telefone = ?, updated_at = ? WHERE id = ?',
        (dados['nome'], dados.get('categoria'), dados.get('telefone'), timestamp_atual(), id)
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Fornecedor atualizado!'}), 200
