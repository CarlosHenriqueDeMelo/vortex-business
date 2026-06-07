from flask import Blueprint, request, jsonify
from database.database import get_connection, hash_senha
import os
import base64

empresas_bp = Blueprint('empresas', __name__)

LOGOS_DIR = os.path.join(os.path.dirname(__file__), '..', 'logos')
os.makedirs(LOGOS_DIR, exist_ok=True)

@empresas_bp.route('/empresas', methods=['GET'])
def listar_empresas():
    conn = get_connection()
    empresas = conn.execute('SELECT id, nome, setor, foto_path FROM empresas').fetchall()
    conn.close()
    return jsonify([dict(e) for e in empresas])

@empresas_bp.route('/empresas', methods=['POST'])
def criar_empresa():
    dados = request.json
    conn = get_connection()
    foto_path = None
    if dados.get('logo_base64'):
        nome_logo = f"logo_{dados['nome'].replace(' ', '_')}.png"
        caminho = os.path.join(LOGOS_DIR, nome_logo)
        with open(caminho, 'wb') as f:
            f.write(base64.b64decode(dados['logo_base64']))
        foto_path = caminho
    conn.execute(
        'INSERT INTO empresas (nome, setor, senha_hash, foto_path) VALUES (?, ?, ?, ?)',
        (dados['nome'], dados.get('setor'), hash_senha(dados['senha']), foto_path)
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Empresa criada com sucesso!'}), 201

@empresas_bp.route('/empresas/login', methods=['POST'])
def login_empresa():
    dados = request.json
    conn = get_connection()
    empresa = conn.execute(
        'SELECT id, nome, setor, foto_path FROM empresas WHERE id = ? AND senha_hash = ?',
        (dados['id'], hash_senha(dados['senha']))
    ).fetchone()
    conn.close()
    if empresa:
        return jsonify({'sucesso': True, 'empresa': dict(empresa)})
    return jsonify({'sucesso': False, 'mensagem': 'Senha incorreta'}), 401

@empresas_bp.route('/empresas/<int:id>', methods=['PUT'])
def editar_empresa(id):
    dados = request.json
    conn = get_connection()
    foto_path = None
    if dados.get('logo_base64'):
        nome_logo = f"logo_{id}.png"
        caminho = os.path.join(LOGOS_DIR, nome_logo)
        with open(caminho, 'wb') as f:
            f.write(base64.b64decode(dados['logo_base64']))
        foto_path = caminho
    if foto_path and dados.get('senha'):
        conn.execute(
            'UPDATE empresas SET nome = ?, setor = ?, foto_path = ?, senha_hash = ? WHERE id = ?',
            (dados['nome'], dados.get('setor'), foto_path, hash_senha(dados['senha']), id)
        )
    elif foto_path:
        conn.execute(
            'UPDATE empresas SET nome = ?, setor = ?, foto_path = ? WHERE id = ?',
            (dados['nome'], dados.get('setor'), foto_path, id)
        )
    elif dados.get('senha'):
        conn.execute(
            'UPDATE empresas SET nome = ?, setor = ?, senha_hash = ? WHERE id = ?',
            (dados['nome'], dados.get('setor'), hash_senha(dados['senha']), id)
        )
    else:
        conn.execute(
            'UPDATE empresas SET nome = ?, setor = ? WHERE id = ?',
            (dados['nome'], dados.get('setor'), id)
        )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Empresa atualizada com sucesso!'}), 200
