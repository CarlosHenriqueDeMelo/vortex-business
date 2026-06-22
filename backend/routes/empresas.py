from flask import Blueprint, request, jsonify
from database.database import get_connection, hash_senha, gerar_uuid, timestamp_atual
import os
import base64

empresas_bp = Blueprint('empresas', __name__)

from database.database import get_app_data_dir
LOGOS_DIR = os.path.join(get_app_data_dir(), 'logos')
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
        'INSERT INTO empresas (nome, setor, senha_hash, foto_path, pergunta_seguranca, resposta_seguranca, uuid, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (dados['nome'], dados.get('setor'), hash_senha(dados['senha']), foto_path,
         dados.get('pergunta_seguranca'),
         dados.get('resposta_seguranca', '').lower().strip() if dados.get('resposta_seguranca') else None,
         gerar_uuid(), timestamp_atual())
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
    agora = timestamp_atual()
    if foto_path and dados.get('senha'):
        conn.execute(
            'UPDATE empresas SET nome = ?, setor = ?, foto_path = ?, senha_hash = ?, updated_at = ? WHERE id = ?',
            (dados['nome'], dados.get('setor'), foto_path, hash_senha(dados['senha']), agora, id)
        )
    elif foto_path:
        conn.execute(
            'UPDATE empresas SET nome = ?, setor = ?, foto_path = ?, updated_at = ? WHERE id = ?',
            (dados['nome'], dados.get('setor'), foto_path, agora, id)
        )
    elif dados.get('senha'):
        conn.execute(
            'UPDATE empresas SET nome = ?, setor = ?, senha_hash = ?, updated_at = ? WHERE id = ?',
            (dados['nome'], dados.get('setor'), hash_senha(dados['senha']), agora, id)
        )
    else:
        conn.execute(
            'UPDATE empresas SET nome = ?, setor = ?, updated_at = ? WHERE id = ?',
            (dados['nome'], dados.get('setor'), agora, id)
        )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Empresa atualizada com sucesso!'}), 200

@empresas_bp.route('/empresas/<int:id>/pergunta', methods=['GET'])
def obter_pergunta(id):
    conn = get_connection()
    empresa = conn.execute('SELECT pergunta_seguranca FROM empresas WHERE id = ?', (id,)).fetchone()
    conn.close()
    if not empresa or not empresa['pergunta_seguranca']:
        return jsonify({'mensagem': 'Esta empresa nao configurou recuperacao de senha'}), 404
    return jsonify({'pergunta': empresa['pergunta_seguranca']})

@empresas_bp.route('/empresas/<int:id>/resetar-senha', methods=['POST'])
def resetar_senha(id):
    dados = request.json
    conn = get_connection()
    empresa = conn.execute('SELECT resposta_seguranca FROM empresas WHERE id = ?', (id,)).fetchone()
    if not empresa or not empresa['resposta_seguranca']:
        conn.close()
        return jsonify({'mensagem': 'Recuperacao nao configurada'}), 404
    resposta_enviada = (dados.get('resposta') or '').lower().strip()
    if not resposta_enviada or resposta_enviada != empresa['resposta_seguranca']:
        conn.close()
        return jsonify({'mensagem': 'Resposta incorreta'}), 401
    nova_senha = dados.get('nova_senha')
    if not nova_senha or len(nova_senha) < 4:
        conn.close()
        return jsonify({'mensagem': 'Nova senha invalida'}), 400
    conn.execute('UPDATE empresas SET senha_hash = ?, updated_at = ? WHERE id = ?', (hash_senha(nova_senha), timestamp_atual(), id))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Senha redefinida com sucesso!'}), 200

@empresas_bp.route('/empresas/<int:id>', methods=['DELETE'])
def deletar_empresa(id):
    conn = get_connection()
    conn.execute('DELETE FROM vendas WHERE empresa_id = ?', (id,))
    conn.execute('DELETE FROM clientes WHERE empresa_id = ?', (id,))
    conn.execute('DELETE FROM produtos WHERE empresa_id = ?', (id,))
    conn.execute('DELETE FROM fornecedores WHERE empresa_id = ?', (id,))
    conn.execute('DELETE FROM financeiro WHERE empresa_id = ?', (id,))
    conn.execute('DELETE FROM entradas_estoque WHERE empresa_id = ?', (id,))
    conn.execute('DELETE FROM empresas WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Empresa excluida com sucesso!'}), 200
