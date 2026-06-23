import { getDb } from './database';

export type Produto = {
  uuid: string;
  empresa_id: number;
  nome: string;
  categoria: string | null;
  unidade: string | null;
  preco_custo: number;
  preco_venda: number;
  quantidade: number;
  quantidade_minima: number;
  updated_at: string;
};

export type Cliente = {
  uuid: string;
  empresa_id: number;
  nome: string;
  telefone: string | null;
  cidade: string | null;
  regiao: string | null;
  divida_atual: number;
  updated_at: string;
};

/** Lista produtos ativos (nao deletados), ordenados por nome */
export async function listarProdutos(): Promise<Produto[]> {
  const db = await getDb();
  return db.getAllAsync<Produto>(
    'SELECT * FROM produtos WHERE deleted_at IS NULL ORDER BY nome ASC'
  );
}

/** Lista clientes ativos, ordenados por nome */
export async function listarClientes(): Promise<Cliente[]> {
  const db = await getDb();
  return db.getAllAsync<Cliente>(
    'SELECT * FROM clientes WHERE deleted_at IS NULL ORDER BY nome ASC'
  );
}

/** Lista clientes que possuem fiado em aberto, ordenados pelo maior valor devido */
export async function listarClientesComFiado(): Promise<Cliente[]> {
  const db = await getDb();
  return db.getAllAsync<Cliente>(
    'SELECT * FROM clientes WHERE deleted_at IS NULL AND divida_atual > 0 ORDER BY divida_atual DESC'
  );
}
