"""Protecao simples contra tentativas repetidas (login e recuperacao de senha)."""
import time
from threading import Lock

_MAX_TENTATIVAS = 5
_JANELA_SEG = 300  # 5 minutos
_falhas = {}
_lock = Lock()

def bloqueado(chave):
    """Retorna quantos segundos faltam para liberar, ou 0 se pode tentar."""
    agora = time.time()
    with _lock:
        tentativas = [t for t in _falhas.get(chave, []) if agora - t < _JANELA_SEG]
        _falhas[chave] = tentativas
        if len(tentativas) >= _MAX_TENTATIVAS:
            return int(_JANELA_SEG - (agora - tentativas[0])) + 1
    return 0

def registrar_falha(chave):
    with _lock:
        _falhas.setdefault(chave, []).append(time.time())

def limpar(chave):
    with _lock:
        _falhas.pop(chave, None)
