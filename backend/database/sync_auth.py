import os
from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv

# Carrega o .env (procura na pasta backend, onde esse arquivo deve estar)
load_dotenv()

def token_valido(token_recebido):
    """Compara o token recebido com o token configurado no .env"""
    token_esperado = os.environ.get('VORTEX_SYNC_TOKEN')
    if not token_esperado:
        # Se nao tem token configurado, bloqueia por seguranca (fail-safe)
        return False
    if not token_recebido:
        return False
    return token_recebido == token_esperado

def requer_token_sync(funcao):
    """Decorador que protege rotas de sincronizacao com o token do .env"""
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        token_recebido = request.headers.get('X-Sync-Token')
        if not token_valido(token_recebido):
            return jsonify({'mensagem': 'Token de sincronizacao invalido ou ausente'}), 401
        return funcao(*args, **kwargs)
    return wrapper
