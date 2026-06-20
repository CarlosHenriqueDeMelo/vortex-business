import sqlite3
import os
import hashlib

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

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

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
    
    

    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso!")

if __name__ == '__main__':
    inicializar_banco()