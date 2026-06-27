import { getDb, getMeta, setMeta } from '../database/database';

const TABELAS_SYNC = [
  'clientes',
  'produtos',
  'fornecedores',
  'entradas_estoque',
  'vendas',
  'itens_venda',
  'financeiro',
] as const;

type TabelaSync = (typeof TABELAS_SYNC)[number];

const COLUNAS: Record<TabelaSync, string[]> = {
  clientes: ['empresa_id', 'nome', 'telefone', 'cidade', 'regiao', 'total_compras', 'total_gasto', 'divida_atual', 'ativo', 'documento'],
  produtos: ['empresa_id', 'nome', 'categoria', 'unidade', 'preco_custo', 'preco_venda', 'quantidade', 'quantidade_minima'],
  fornecedores: ['empresa_id', 'nome', 'categoria', 'telefone', 'email', 'ativo'],
  entradas_estoque: ['empresa_id', 'produto_id', 'fornecedor_id', 'quantidade', 'preco_custo', 'forma_pagamento', 'observacao'],
  vendas: ['empresa_id', 'cliente_id', 'forma_pagamento', 'desconto', 'total', 'cidade', 'telefone', 'observacao', 'pdf_gerado'],
  itens_venda: ['venda_id', 'produto_id', 'quantidade', 'preco_unitario', 'subtotal'],
  financeiro: ['empresa_id', 'descricao', 'tipo', 'valor', 'vencimento', 'status', 'venda_id', 'cliente_id'],
};

export type ResultadoSync = {
  sucesso: boolean;
  mensagem: string;
  enviados?: number;
  recebidos?: number;
};

function montarUrlBase(endereco: string): string {
  const limpo = endereco.trim().replace(/\/$/, '');
  if (limpo.includes(':')) return `http://${limpo}`;
  return `http://${limpo}:5000`;
}

function normalizarValor(valor: unknown): string | number | null {
  if (valor === undefined) return null;
  if (valor === null) return null;
  if (typeof valor === 'boolean') return valor ? 1 : 0;
  return valor as string | number;
}

async function lerRegistrosLocais(tabela: TabelaSync): Promise<Record<string, unknown>[]> {
  const db = await getDb();
  const colunas = ['uuid', 'updated_at', ...COLUNAS[tabela]];
  const linhas = await db.getAllAsync<Record<string, unknown>>(
    `SELECT ${colunas.join(', ')} FROM ${tabela}`
  );
  return linhas;
}

async function salvarRegistrosRecebidos(tabela: TabelaSync, registros: Record<string, unknown>[]) {
  if (registros.length === 0) return;
  const db = await getDb();
  const colunas = ['uuid', 'updated_at', ...COLUNAS[tabela]];
  const placeholders = colunas.map(() => '?').join(', ');
  const updateSets = colunas
    .filter((c) => c !== 'uuid')
    .map((c) => `${c} = excluded.${c}`)
    .join(', ');

  const sql = `INSERT INTO ${tabela} (${colunas.join(', ')}) VALUES (${placeholders})
       ON CONFLICT(uuid) DO UPDATE SET ${updateSets}
       WHERE excluded.updated_at > ${tabela}.updated_at`;

  const statement = await db.prepareAsync(sql);
  try {
    for (const registro of registros) {
      const valores = colunas.map((c) => normalizarValor(registro[c]));
      await statement.executeAsync(valores);
    }
  } finally {
    await statement.finalizeAsync();
  }
}

export async function sincronizar(
  endereco: string,
  empresaId: number,
  token: string
): Promise<ResultadoSync> {
  const urlBase = montarUrlBase(endereco);
  const ultimaSync = (await getMeta('ultima_sincronizacao')) ?? '1970-01-01 00:00:00';

  try {
    const dadosPush: Record<string, Record<string, unknown>[]> = {};
    let totalEnviados = 0;
    for (const tabela of TABELAS_SYNC) {
      const registros = await lerRegistrosLocais(tabela);
      dadosPush[tabela] = registros;
      totalEnviados += registros.length;
    }

    const respPush = await fetch(`${urlBase}/sync/push`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Sync-Token': token,
      },
      body: JSON.stringify({ empresa_id: empresaId, dados: dadosPush }),
    });

    if (!respPush.ok) {
      const erro = await respPush.json().catch(() => ({ mensagem: 'Erro desconhecido' }));
      return { sucesso: false, mensagem: erro.mensagem || `Erro no push (status ${respPush.status})` };
    }

    const params = new URLSearchParams({ empresa_id: String(empresaId), desde: ultimaSync });
    const respPull = await fetch(`${urlBase}/sync/pull?${params.toString()}`, {
      headers: { 'X-Sync-Token': token },
    });

    if (!respPull.ok) {
      const erro = await respPull.json().catch(() => ({ mensagem: 'Erro desconhecido' }));
      return { sucesso: false, mensagem: erro.mensagem || `Erro no pull (status ${respPull.status})` };
    }

    const dadosPull = await respPull.json();
    let totalRecebidos = 0;
    for (const tabela of TABELAS_SYNC) {
      const registros = dadosPull[tabela] ?? [];
      await salvarRegistrosRecebidos(tabela, registros);
      totalRecebidos += registros.length;
    }

    const agora = new Date().toISOString();
    await setMeta('ultima_sincronizacao', agora);
    await setMeta('ultimo_ip', endereco);

    return {
      sucesso: true,
      mensagem: 'Sincronização concluída',
      enviados: totalEnviados,
      recebidos: totalRecebidos,
    };
  } catch (e) {
    const detalhe = e instanceof Error ? e.message : String(e);
    return {
      sucesso: false,
      mensagem: `Não foi possível sincronizar: ${detalhe}`,
    };
  }
}
