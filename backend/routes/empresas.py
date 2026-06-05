from flask import Blueprint, request, jsonify
from database.database import get_connection, hash_senha

empresas_bp = Blueprint('empresas', __name__)

@empresas_bp.route('/empresas', methods=['GET'])
def listar_empresas():
    conn = get_connection()
    empresas = conn.execute(
        'SELECT id, nome, setor, foto_path FROM empresas'
    ).fetchall()
    conn.close()
    return jsonify([dict(e) for e in empresas])

@empresas_bp.route('/empresas', methods=['POST'])
def criar_empresa():
    dados = request.json
    conn = get_connection()
    conn.execute(
        'INSERT INTO empresas (nome, setor, senha_hash) VALUES (?, ?, ?)',
        (dados['nome'], dados.get('setor'), hash_senha(dados['senha']))
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Empresa criada com sucesso!'}), 201

@empresas_bp.route('/empresas/login', methods=['POST'])
def login_empresa():
    dados = request.json
    conn = get_connection()
    empresa = conn.execute(
        'SELECT id, nome, setor FROM empresas WHERE id = ? AND senha_hash = ?',
        (dados['id'], hash_senha(dados['senha']))
    ).fetchone()
    conn.close()
    if empresa:
        return jsonify({'sucesso': True, 'empresa': dict(empresa)})
    return jsonify({'sucesso': False, 'mensagem': 'Senha incorreta'}), 401