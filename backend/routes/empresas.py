from flask import Blueprint, request, jsonify
from database.database import get_connection, hash_senha, verificar_senha, hash_legado, gerar_uuid, timestamp_atual
from database.seguranca import bloqueado, registrar_falha, limpar
import os
import base64

empresas_bp = Blueprint('empresas', __name__)

from database.database import get_app_data_dir
LOGOS_DIR = os.path.join(get_app_data_dir(), 'logos')
os.makedirs(LOGOS_DIR, exist_ok=True)

def salvar_logo(nome_base, b64):
    """Grava a logo com nome controlado pelo servidor (evita path traversal)."""
    try:
        conteudo = base64.b64decode(b64, validate=True)
    except Exception:
        return None
    if len(conteudo) > 5 * 1024 * 1024 or not conteudo.startswith(b'\x89PNG'):
        return None
    caminho = os.path.join(LOGOS_DIR, f"logo_{nome_base}.png")
    with open(caminho, 'wb') as f:
        f.write(conteudo)
    return caminho

@empresas_bp.route('/empresas', methods=['GET'])
def listar_empresas():
    conn = get_connection()
    empresas = conn.execute('SELECT id, nome, setor, foto_path FROM empresas').fetchall()
    conn.close()
    return jsonify([dict(e) for e in empresas])

@empresas_bp.route('/empresas', methods=['POST'])
def criar_empresa():
    dados = request.json or {}
    if not (dados.get('nome') or '').strip():
        return jsonify({'mensagem': 'Nome da empresa e obrigatorio'}), 400
    senha = dados.get('senha') or ''
    if len(senha) != 4 or not senha.isdigit():
        return jsonify({'mensagem': 'A senha deve ter 4 digitos'}), 400
    conn = get_connection()
    foto_path = None
    if dados.get('logo_base64'):
        foto_path = salvar_logo(gerar_uuid(), dados['logo_base64'])
        if foto_path is None:
            conn.close()
            return jsonify({'mensagem': 'Logo invalida'}), 400
    conn.execute(
        'INSERT INTO empresas (nome, setor, senha_hash, foto_path, pergunta_seguranca, resposta_seguranca, uuid, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (dados['nome'], dados.get('setor'), hash_senha(dados['senha']), foto_path,
         dados.get('pergunta_seguranca'),
         hash_senha(dados['resposta_seguranca'].lower().strip()) if (dados.get('resposta_seguranca') or '').strip() else None,
         gerar_uuid(), timestamp_atual())
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Empresa criada com sucesso!'}), 201

@empresas_bp.route('/empresas/login', methods=['POST'])
def login_empresa():
    dados = request.json or {}
    chave = f"login:{dados.get('id')}"
    espera = bloqueado(chave)
    if espera:
        return jsonify({'sucesso': False, 'mensagem': f'Muitas tentativas. Tente de novo em {espera}s'}), 429
    conn = get_connection()
    empresa = conn.execute(
        'SELECT id, nome, setor, foto_path, senha_hash FROM empresas WHERE id = ?', (dados.get('id'),)
    ).fetchone()
    if empresa and verificar_senha(str(dados.get('senha') or ''), empresa['senha_hash']):
        if hash_legado(empresa['senha_hash']):
            conn.execute('UPDATE empresas SET senha_hash = ? WHERE id = ?', (hash_senha(dados['senha']), empresa['id']))
            conn.commit()
        conn.close()
        limpar(chave)
        d = dict(empresa); d.pop('senha_hash', None)
        return jsonify({'sucesso': True, 'empresa': d})
    conn.close()
    registrar_falha(chave)
    return jsonify({'sucesso': False, 'mensagem': 'Senha incorreta'}), 401

@empresas_bp.route('/empresas/<int:id>', methods=['PUT'])
def editar_empresa(id):
    dados = request.json or {}
    if dados.get('senha') and not (len(dados['senha']) == 4 and dados['senha'].isdigit()):
        return jsonify({'mensagem': 'A senha deve ter 4 digitos'}), 400
    conn = get_connection()
    foto_path = None
    if dados.get('logo_base64'):
        foto_path = salvar_logo(f"empresa_{id}", dados['logo_base64'])
        if foto_path is None:
            conn.close()
            return jsonify({'mensagem': 'Logo invalida'}), 400
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
    dados = request.json or {}
    chave = f"reset:{id}"
    espera = bloqueado(chave)
    if espera:
        return jsonify({'mensagem': f'Muitas tentativas. Tente de novo em {espera}s'}), 429
    conn = get_connection()
    empresa = conn.execute('SELECT resposta_seguranca FROM empresas WHERE id = ?', (id,)).fetchone()
    if not empresa or not empresa['resposta_seguranca']:
        conn.close()
        return jsonify({'mensagem': 'Recuperacao nao configurada'}), 404
    resposta_enviada = (dados.get('resposta') or '').lower().strip()
    armazenada = empresa['resposta_seguranca']
    # respostas antigas foram salvas em texto puro: aceita uma vez e regrava com hash
    confere = armazenada == resposta_enviada if not armazenada.startswith('pbkdf2$') else verificar_senha(resposta_enviada, armazenada)
    if not resposta_enviada or not confere:
        conn.close()
        registrar_falha(chave)
        return jsonify({'mensagem': 'Resposta incorreta'}), 401
    limpar(chave)
    nova_senha = dados.get('nova_senha')
    if not nova_senha or len(nova_senha) != 4 or not nova_senha.isdigit():
        conn.close()
        return jsonify({'mensagem': 'A nova senha deve ter 4 digitos'}), 400
    conn.execute('UPDATE empresas SET senha_hash = ?, resposta_seguranca = ?, updated_at = ? WHERE id = ?', (hash_senha(nova_senha), hash_senha(resposta_enviada), timestamp_atual(), id))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Senha redefinida com sucesso!'}), 200

@empresas_bp.route('/empresas/<int:id>', methods=['DELETE'])
def deletar_empresa(id):
    conn = get_connection()
    conn.execute('DELETE FROM itens_venda WHERE venda_id IN (SELECT id FROM vendas WHERE empresa_id = ?)', (id,))
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
