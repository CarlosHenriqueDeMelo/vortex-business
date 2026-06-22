from flask import Blueprint, request, jsonify
from database.database import get_connection, gerar_uuid, timestamp_atual
from database.sync_auth import requer_token_sync

sync_bp = Blueprint('sync', __name__)

# Define as colunas sincronizaveis de cada tabela (sem incluir 'id', que e local de cada banco)
TABELAS_SYNC = {
    'clientes': ['empresa_id', 'nome', 'telefone', 'cidade', 'regiao', 'total_compras', 'total_gasto', 'divida_atual', 'ativo', 'documento'],
    'produtos': ['empresa_id', 'nome', 'categoria', 'unidade', 'preco_custo', 'preco_venda', 'quantidade', 'quantidade_minima'],
    'fornecedores': ['empresa_id', 'nome', 'categoria', 'telefone', 'email', 'ativo'],
    'entradas_estoque': ['empresa_id', 'produto_id', 'fornecedor_id', 'quantidade', 'preco_custo', 'forma_pagamento', 'observacao'],
    'vendas': ['empresa_id', 'cliente_id', 'forma_pagamento', 'desconto', 'total', 'cidade', 'telefone', 'observacao', 'pdf_gerado'],
    'itens_venda': ['venda_id', 'produto_id', 'quantidade', 'preco_unitario', 'subtotal'],
    'financeiro': ['empresa_id', 'descricao', 'tipo', 'valor', 'vencimento', 'status', 'venda_id', 'cliente_id'],
}

def upsert_registro(conn, tabela, registro):
    """Insere o registro se o uuid nao existe, ou atualiza se ja existe."""
    colunas = TABELAS_SYNC[tabela]
    uuid_registro = registro.get('uuid')
    if not uuid_registro:
        return False  # registro sem uuid e invalido para sync, ignora

    existente = conn.execute(
        f"SELECT id, updated_at FROM {tabela} WHERE uuid = ?", (uuid_registro,)
    ).fetchone()

    valores = [registro.get(col) for col in colunas]

    if existente is None:
        # Nao existe ainda - insere
        placeholders = ', '.join(['?'] * (len(colunas) + 2))
        nomes_colunas = ', '.join(colunas + ['uuid', 'updated_at'])
        conn.execute(
            f"INSERT INTO {tabela} ({nomes_colunas}) VALUES ({placeholders})",
            valores + [uuid_registro, registro.get('updated_at') or timestamp_atual()]
        )
    else:
        # Ja existe - so atualiza se o registro recebido for mais recente
        updated_at_recebido = registro.get('updated_at') or ''
        updated_at_local = existente['updated_at'] or ''
        if updated_at_recebido > updated_at_local:
            sets = ', '.join([f"{col} = ?" for col in colunas])
            conn.execute(
                f"UPDATE {tabela} SET {sets}, updated_at = ? WHERE uuid = ?",
                valores + [updated_at_recebido, uuid_registro]
            )
    return True

@sync_bp.route('/sync/push', methods=['POST'])
@requer_token_sync
def sync_push():
    dados = request.json
    empresa_id = dados.get('empresa_id')
    if not empresa_id:
        return jsonify({'mensagem': 'empresa_id e obrigatorio'}), 400

    registros = dados.get('dados', {})
    conn = get_connection()
    resultado = {}

    try:
        for tabela in TABELAS_SYNC:
            itens = registros.get(tabela, [])
            count = 0
            for item in itens:
                if upsert_registro(conn, tabela, item):
                    count += 1
            resultado[tabela] = count
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'mensagem': f'Erro ao processar sincronizacao: {str(e)}'}), 500

    conn.close()
    return jsonify({'mensagem': 'Sincronizacao recebida com sucesso!', 'processados': resultado}), 200

@sync_bp.route('/sync/pull', methods=['GET'])
@requer_token_sync
def sync_pull():
    empresa_id = request.args.get('empresa_id')
    desde = request.args.get('desde', '1970-01-01 00:00:00')
    if not empresa_id:
        return jsonify({'mensagem': 'empresa_id e obrigatorio'}), 400

    # Normaliza o formato da data: aceita tanto ISO ('2026-06-22T09:00:00')
    # quanto o formato usado no banco ('2026-06-22 09:00:00'), pois a
    # comparacao no SQLite e feita como texto e os dois formatos nao sao
    # comparaveis diretamente.
    desde = desde.replace('T', ' ')
    if '.' in desde:
        desde = desde.split('.')[0]  # remove milissegundos, se houver

    conn = get_connection()
    resultado = {}

    for tabela, colunas in TABELAS_SYNC.items():
        if 'empresa_id' in colunas:
            query = f"SELECT * FROM {tabela} WHERE empresa_id = ? AND updated_at > ?"
            linhas = conn.execute(query, (empresa_id, desde)).fetchall()
        else:
            if tabela == 'itens_venda':
                query = """
                    SELECT iv.* FROM itens_venda iv
                    JOIN vendas v ON iv.venda_id = v.id
                    WHERE v.empresa_id = ? AND iv.updated_at > ?
                """
                linhas = conn.execute(query, (empresa_id, desde)).fetchall()
            else:
                linhas = []
        resultado[tabela] = [dict(l) for l in linhas]

    conn.close()
    return jsonify(resultado), 200
