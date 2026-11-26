from flask import Blueprint, request, jsonify
from database.database import get_connection, timestamp_atual
from database.sync_auth import requer_token_sync

sync_bp = Blueprint('sync', __name__)

# Colunas sincronizaveis (sem 'id', que e local de cada banco). deleted_at propaga exclusoes.
TABELAS_SYNC = {
    'clientes': ['empresa_id', 'nome', 'telefone', 'cidade', 'regiao', 'total_compras', 'total_gasto', 'divida_atual', 'ativo', 'documento', 'deleted_at'],
    'produtos': ['empresa_id', 'nome', 'categoria', 'unidade', 'preco_custo', 'preco_venda', 'quantidade', 'quantidade_minima', 'deleted_at'],
    'fornecedores': ['empresa_id', 'nome', 'categoria', 'telefone', 'email', 'ativo', 'deleted_at'],
    'entradas_estoque': ['empresa_id', 'produto_id', 'fornecedor_id', 'quantidade', 'preco_custo', 'forma_pagamento', 'observacao', 'deleted_at'],
    'vendas': ['empresa_id', 'cliente_id', 'forma_pagamento', 'desconto', 'total', 'cidade', 'telefone', 'observacao', 'pdf_gerado', 'deleted_at'],
    'itens_venda': ['venda_id', 'produto_id', 'quantidade', 'preco_unitario', 'subtotal', 'deleted_at'],
    'financeiro': ['empresa_id', 'descricao', 'tipo', 'valor', 'vencimento', 'status', 'venda_id', 'cliente_id', 'deleted_at'],
}

# No desktop as relacoes usam o id inteiro local; no protocolo de sync (e no celular)
# usam o uuid. Aqui ficam as colunas de relacao e a tabela a que apontam.
FK = {
    'entradas_estoque': {'produto_id': 'produtos', 'fornecedor_id': 'fornecedores'},
    'vendas': {'cliente_id': 'clientes'},
    'itens_venda': {'venda_id': 'vendas', 'produto_id': 'produtos'},
    'financeiro': {'venda_id': 'vendas', 'cliente_id': 'clientes'},
}
FK_OBRIGATORIA = {('entradas_estoque', 'produto_id'), ('itens_venda', 'venda_id'), ('itens_venda', 'produto_id')}


def uuid_para_id(conn, tabela, uuid_valor):
    if uuid_valor in (None, ''):
        return None
    linha = conn.execute(f"SELECT id FROM {tabela} WHERE uuid = ?", (str(uuid_valor),)).fetchone()
    return linha['id'] if linha else None


def id_para_uuid(conn, tabela, id_valor):
    if id_valor in (None, ''):
        return None
    linha = conn.execute(f"SELECT uuid FROM {tabela} WHERE id = ?", (id_valor,)).fetchone()
    return linha['uuid'] if linha else None


def upsert_registro(conn, tabela, registro):
    """Insere se o uuid nao existe; atualiza se o recebido for mais recente.
    Retorna True se processou, False se ignorou (sem uuid ou relacao obrigatoria inexistente)."""
    colunas = TABELAS_SYNC[tabela]
    uuid_registro = registro.get('uuid')
    if not uuid_registro:
        return False

    valores_dict = {col: registro.get(col) for col in colunas}
    for coluna, tabela_pai in FK.get(tabela, {}).items():
        id_local = uuid_para_id(conn, tabela_pai, valores_dict[coluna])
        if id_local is None and valores_dict[coluna] not in (None, '') and (tabela, coluna) in FK_OBRIGATORIA:
            return False
        valores_dict[coluna] = id_local
    valores = [valores_dict[c] for c in colunas]

    existente = conn.execute(f"SELECT id, updated_at FROM {tabela} WHERE uuid = ?", (uuid_registro,)).fetchone()
    recebido = registro.get('updated_at') or timestamp_atual()

    if existente is None:
        nomes = ', '.join(colunas + ['uuid', 'updated_at'])
        marcas = ', '.join(['?'] * (len(colunas) + 2))
        conn.execute(f"INSERT INTO {tabela} ({nomes}) VALUES ({marcas})", valores + [uuid_registro, recebido])
    elif recebido > (existente['updated_at'] or ''):
        sets = ', '.join([f"{c} = ?" for c in colunas])
        conn.execute(f"UPDATE {tabela} SET {sets}, updated_at = ? WHERE uuid = ?", valores + [recebido, uuid_registro])
    return True


@sync_bp.route('/sync/empresas', methods=['GET'])
@requer_token_sync
def sync_empresas():
    """Lista id/nome das empresas para o celular escolher qual sincronizar (sem dados sensiveis)."""
    conn = get_connection()
    linhas = conn.execute('SELECT id, nome FROM empresas ORDER BY id').fetchall()
    conn.close()
    return jsonify([dict(l) for l in linhas])


@sync_bp.route('/sync/push', methods=['POST'])
@requer_token_sync
def sync_push():
    dados = request.get_json(silent=True) or {}
    if not dados.get('empresa_id'):
        return jsonify({'mensagem': 'empresa_id e obrigatorio'}), 400

    registros = dados.get('dados') or {}
    conn = get_connection()
    resultado, ignorados = {}, {}
    try:
        for tabela in TABELAS_SYNC:  # ordem importa: pais antes dos filhos
            ok = nok = 0
            for item in registros.get(tabela, []):
                if upsert_registro(conn, tabela, item):
                    ok += 1
                else:
                    nok += 1
            resultado[tabela] = ok
            if nok:
                ignorados[tabela] = nok
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'mensagem': f'Erro ao processar sincronizacao: {e}'}), 500
    finally:
        conn.close()
    return jsonify({'mensagem': 'Sincronizacao recebida com sucesso!', 'processados': resultado, 'ignorados': ignorados}), 200


@sync_bp.route('/sync/pull', methods=['GET'])
@requer_token_sync
def sync_pull():
    empresa_id = request.args.get('empresa_id')
    desde = request.args.get('desde', '1970-01-01 00:00:00')
    if not empresa_id:
        return jsonify({'mensagem': 'empresa_id e obrigatorio'}), 400

    # aceita ISO ('2026-06-22T09:00:00.000Z') e o formato do banco ('2026-06-22 09:00:00')
    desde = desde.replace('T', ' ').replace('Z', '')
    if '.' in desde:
        desde = desde.split('.')[0]

    conn = get_connection()
    resultado = {}
    for tabela, colunas in TABELAS_SYNC.items():
        if tabela == 'itens_venda':
            linhas = conn.execute(
                "SELECT iv.* FROM itens_venda iv JOIN vendas v ON iv.venda_id = v.id "
                "WHERE v.empresa_id = ? AND iv.updated_at > ?", (empresa_id, desde)).fetchall()
        else:
            linhas = conn.execute(
                f"SELECT * FROM {tabela} WHERE empresa_id = ? AND updated_at > ?", (empresa_id, desde)).fetchall()
        saida = []
        for linha in linhas:
            reg = {'uuid': linha['uuid'], 'updated_at': linha['updated_at']}
            for c in colunas:
                reg[c] = linha[c]
            for coluna, tabela_pai in FK.get(tabela, {}).items():
                reg[coluna] = id_para_uuid(conn, tabela_pai, reg[coluna])
            saida.append(reg)
        resultado[tabela] = saida
    conn.close()
    return jsonify(resultado), 200
