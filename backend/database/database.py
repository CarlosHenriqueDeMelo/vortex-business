import sqlite3
import os
import hashlib
import hmac
import uuid as uuid_lib

def get_app_data_dir():
    if os.name == 'nt':
        base = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'VortexBusiness')
    else:
        base = os.path.join(os.path.expanduser('~'), '.vortex-business')
    os.makedirs(base, exist_ok=True)
    return base

DB_PATH = os.path.join(get_app_data_dir(), 'vortex.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

_PBKDF2_ITER = 200_000

def hash_senha(senha):
    """Hash com salt aleatorio (PBKDF2-SHA256). Formato: pbkdf2$iter$salt$hash"""
    salt = os.urandom(16).hex()
    h = hashlib.pbkdf2_hmac('sha256', senha.encode(), bytes.fromhex(salt), _PBKDF2_ITER).hex()
    return f"pbkdf2${_PBKDF2_ITER}${salt}${h}"

def verificar_senha(senha, armazenado):
    """Confere a senha. Aceita o formato novo e o antigo (sha256 puro)."""
    if not armazenado:
        return False
    if armazenado.startswith('pbkdf2$'):
        try:
            _, it, salt, h = armazenado.split('$')
            calc = hashlib.pbkdf2_hmac('sha256', senha.encode(), bytes.fromhex(salt), int(it)).hex()
            return hmac.compare_digest(calc, h)
        except (ValueError, TypeError):
            return False
    antigo = hashlib.sha256(senha.encode()).hexdigest()
    return hmac.compare_digest(antigo, armazenado)

def hash_legado(armazenado):
    """True se o hash ainda esta no formato antigo e deve ser regravado."""
    return bool(armazenado) and not armazenado.startswith('pbkdf2$')

def gerar_uuid():
    """Gera um UUID novo para um registro. Usar sempre que criar empresa, produto, cliente, venda, etc."""
    return str(uuid_lib.uuid4())

def timestamp_atual():
    """Retorna o timestamp atual no mesmo formato usado pelo banco (datetime local).
    Usar para preencher updated_at sempre que criar OU editar um registro."""
    conn = get_connection()
    agora = conn.execute("SELECT datetime('now', 'localtime')").fetchone()[0]
    conn.close()
    return agora

def inicializar_banco():
    conn = get_connection()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            setor TEXT,
            foto_path TEXT,
            senha_hash TEXT NOT NULL,
            pergunta_seguranca TEXT,
            resposta_seguranca TEXT,
            criado_em TEXT DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            categoria TEXT,
            telefone TEXT,
            email TEXT,
            ativo INTEGER DEFAULT 1,
            criado_em TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            categoria TEXT,
            unidade TEXT DEFAULT 'un',
            preco_custo REAL DEFAULT 0,
            preco_venda REAL DEFAULT 0,
            quantidade INTEGER DEFAULT 0,
            quantidade_minima INTEGER DEFAULT 5,
            criado_em TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS entradas_estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            fornecedor_id INTEGER,
            quantidade INTEGER NOT NULL,
            preco_custo REAL NOT NULL,
            forma_pagamento TEXT,
            data_entrada TEXT DEFAULT (datetime('now', 'localtime')),
            observacao TEXT,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id),
            FOREIGN KEY (produto_id) REFERENCES produtos(id),
            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            telefone TEXT,
            cidade TEXT,
            regiao TEXT,
            total_compras INTEGER DEFAULT 0,
            total_gasto REAL DEFAULT 0,
            divida_atual REAL DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            documento TEXT,
            criado_em TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            cliente_id INTEGER,
            forma_pagamento TEXT NOT NULL,
            desconto REAL DEFAULT 0,
            total REAL NOT NULL,
            cidade TEXT,
            telefone TEXT,
            data_venda TEXT DEFAULT (datetime('now', 'localtime')),
            observacao TEXT,
            pdf_gerado INTEGER DEFAULT 0,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS itens_venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venda_id) REFERENCES vendas(id),
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS financeiro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            tipo TEXT NOT NULL CHECK(tipo IN ('pagar', 'receber')),
            valor REAL NOT NULL,
            vencimento TEXT,
            status TEXT DEFAULT 'pendente' CHECK(status IN ('pendente', 'pago', 'cancelado', 'agendado')),
            venda_id INTEGER,
            cliente_id INTEGER,
            criado_em TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (empresa_id) REFERENCES empresas(id),
            FOREIGN KEY (venda_id) REFERENCES vendas(id),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')

    # Migracao automatica - adiciona colunas que possam estar faltando em bancos antigos
    tabelas_sync = [
        'empresas', 'fornecedores', 'produtos', 'entradas_estoque',
        'clientes', 'vendas', 'itens_venda', 'financeiro'
    ]

    colunas_extras = {
        'empresas': ['pergunta_seguranca TEXT', 'resposta_seguranca TEXT'],
        'clientes': ['ativo INTEGER DEFAULT 1', 'documento TEXT']
    }

    # Adiciona as colunas de sincronizacao (uuid, updated_at, deleted_at) em todas as tabelas
    for tabela in tabelas_sync:
        colunas_extras.setdefault(tabela, [])
        colunas_extras[tabela] += [
            'uuid TEXT',
            'updated_at TEXT',
            'deleted_at TEXT'
        ]

    for tabela, colunas in colunas_extras.items():
        existentes = [row[1] for row in c.execute(f"PRAGMA table_info({tabela})").fetchall()]
        for coluna_def in colunas:
            nome_coluna = coluna_def.split()[0]
            if nome_coluna not in existentes:
                try:
                    c.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna_def}")
                except sqlite3.OperationalError:
                    pass

    conn.commit()

    # Popula uuid e updated_at em registros antigos que ainda nao tem (uuid fica NULL apos o ALTER TABLE)
    agora = c.execute("SELECT datetime('now', 'localtime')").fetchone()[0]
    for tabela in tabelas_sync:
        linhas = c.execute(f"SELECT id FROM {tabela} WHERE uuid IS NULL").fetchall()
        for linha in linhas:
            novo_uuid = str(uuid_lib.uuid4())
            c.execute(
                f"UPDATE {tabela} SET uuid = ?, updated_at = ? WHERE id = ?",
                (novo_uuid, agora, linha['id'])
            )

    # Garante uuid unico (apos popular os antigos) - evita duplicidade em sincronizacoes futuras
    for tabela in tabelas_sync:
        try:
            c.execute(
                f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{tabela}_uuid ON {tabela}(uuid)"
            )
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso!")

if __name__ == '__main__':
    inicializar_banco()


def fazer_backup(manter=7):
    """Copia o banco para a pasta backups (1 por dia, mantendo os ultimos `manter`)."""
    import datetime
    pasta = os.path.join(get_app_data_dir(), 'backups')
    os.makedirs(pasta, exist_ok=True)
    destino = os.path.join(pasta, f"vortex_{datetime.date.today().isoformat()}.db")
    if os.path.exists(destino) or not os.path.exists(DB_PATH):
        return
    origem = sqlite3.connect(DB_PATH)
    copia = sqlite3.connect(destino)
    try:
        origem.backup(copia)  # copia consistente, mesmo com o banco em uso
    finally:
        copia.close()
        origem.close()
    antigos = sorted(f for f in os.listdir(pasta) if f.startswith('vortex_') and f.endswith('.db'))
    for f in antigos[:-manter]:
        os.remove(os.path.join(pasta, f))
