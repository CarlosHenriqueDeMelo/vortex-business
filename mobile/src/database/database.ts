import * as SQLite from 'expo-sqlite';

const DB_NAME = 'vortex.db';

let dbInstance: SQLite.SQLiteDatabase | null = null;

/**
 * Retorna a conexao unica com o banco local, abrindo e
 * inicializando o schema na primeira chamada.
 */
export async function getDb(): Promise<SQLite.SQLiteDatabase> {
  if (dbInstance) return dbInstance;

  const db = await SQLite.openDatabaseAsync(DB_NAME);
  await inicializarBanco(db);
  dbInstance = db;
  return db;
}

async function inicializarBanco(db: SQLite.SQLiteDatabase) {
  await db.execAsync(`
    PRAGMA journal_mode = WAL;

    CREATE TABLE IF NOT EXISTS clientes (
      uuid TEXT PRIMARY KEY,
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
      updated_at TEXT NOT NULL,
      deleted_at TEXT
    );

    CREATE TABLE IF NOT EXISTS produtos (
      uuid TEXT PRIMARY KEY,
      empresa_id INTEGER NOT NULL,
      nome TEXT NOT NULL,
      categoria TEXT,
      unidade TEXT DEFAULT 'un',
      preco_custo REAL DEFAULT 0,
      preco_venda REAL DEFAULT 0,
      quantidade INTEGER DEFAULT 0,
      quantidade_minima INTEGER DEFAULT 5,
      updated_at TEXT NOT NULL,
      deleted_at TEXT
    );

    CREATE TABLE IF NOT EXISTS fornecedores (
      uuid TEXT PRIMARY KEY,
      empresa_id INTEGER NOT NULL,
      nome TEXT NOT NULL,
      categoria TEXT,
      telefone TEXT,
      email TEXT,
      ativo INTEGER DEFAULT 1,
      updated_at TEXT NOT NULL,
      deleted_at TEXT
    );

    CREATE TABLE IF NOT EXISTS entradas_estoque (
      uuid TEXT PRIMARY KEY,
      empresa_id INTEGER NOT NULL,
      produto_id TEXT NOT NULL,
      fornecedor_id TEXT,
      quantidade INTEGER NOT NULL,
      preco_custo REAL NOT NULL,
      forma_pagamento TEXT,
      observacao TEXT,
      updated_at TEXT NOT NULL,
      deleted_at TEXT
    );

    CREATE TABLE IF NOT EXISTS vendas (
      uuid TEXT PRIMARY KEY,
      empresa_id INTEGER NOT NULL,
      cliente_id TEXT,
      forma_pagamento TEXT NOT NULL,
      desconto REAL DEFAULT 0,
      total REAL NOT NULL,
      cidade TEXT,
      telefone TEXT,
      observacao TEXT,
      pdf_gerado INTEGER DEFAULT 0,
      updated_at TEXT NOT NULL,
      deleted_at TEXT
    );

    CREATE TABLE IF NOT EXISTS itens_venda (
      uuid TEXT PRIMARY KEY,
      venda_id TEXT NOT NULL,
      produto_id TEXT NOT NULL,
      quantidade INTEGER NOT NULL,
      preco_unitario REAL NOT NULL,
      subtotal REAL NOT NULL,
      updated_at TEXT NOT NULL,
      deleted_at TEXT
    );

    CREATE TABLE IF NOT EXISTS financeiro (
      uuid TEXT PRIMARY KEY,
      empresa_id INTEGER NOT NULL,
      descricao TEXT NOT NULL,
      tipo TEXT NOT NULL,
      valor REAL NOT NULL,
      vencimento TEXT,
      status TEXT DEFAULT 'pendente',
      venda_id TEXT,
      cliente_id TEXT,
      updated_at TEXT NOT NULL,
      deleted_at TEXT
    );

    CREATE TABLE IF NOT EXISTS sync_meta (
      chave TEXT PRIMARY KEY,
      valor TEXT
    );
  `);
}

/** Le um valor simples de configuracao (ex: ip do desktop, ultima sincronizacao) */
export async function getMeta(chave: string): Promise<string | null> {
  const db = await getDb();
  const row = await db.getFirstAsync<{ valor: string }>(
    'SELECT valor FROM sync_meta WHERE chave = ?',
    [chave]
  );
  return row?.valor ?? null;
}

/** Salva um valor simples de configuracao */
export async function setMeta(chave: string, valor: string): Promise<void> {
  const db = await getDb();
  await db.runAsync(
    'INSERT INTO sync_meta (chave, valor) VALUES (?, ?) ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor',
    [chave, valor]
  );
}
