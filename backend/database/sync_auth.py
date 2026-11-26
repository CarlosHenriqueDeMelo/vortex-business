import hmac
import os
import secrets
from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv

# Carrega o .env (procura na pasta backend, onde esse arquivo deve estar)
load_dotenv()

def obter_token():
    """Token de sincronizacao: VORTEX_SYNC_TOKEN do .env (se existir) ou o arquivo
    sync_token na pasta de dados, criado automaticamente na primeira execucao."""
    token = (os.environ.get('VORTEX_SYNC_TOKEN') or '').strip()
    if token:
        return token
    from database.database import get_app_data_dir
    caminho = os.path.join(get_app_data_dir(), 'sync_token')
    try:
        if os.path.exists(caminho):
            with open(caminho, encoding='utf-8') as f:
                existente = f.read().strip()
            if existente:
                return existente
        novo = secrets.token_urlsafe(9)  # 12 caracteres
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(novo)
        try:
            os.chmod(caminho, 0o600)
        except OSError:
            pass
        return novo
    except OSError:
        return None  # sem token => sincronizacao bloqueada (fail-safe)

def token_valido(token_recebido):
    """Compara (em tempo constante) o token recebido com o esperado."""
    token_esperado = obter_token()
    if not token_esperado or not token_recebido:
        return False
    return hmac.compare_digest(token_recebido.encode(), token_esperado.encode())

def requer_token_sync(funcao):
    """Decorador que protege rotas de sincronizacao com o token do .env"""
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        token_recebido = request.headers.get('X-Sync-Token')
        if not token_valido(token_recebido):
            return jsonify({'mensagem': 'Token de sincronizacao invalido ou ausente'}), 401
        return funcao(*args, **kwargs)
    return wrapper
