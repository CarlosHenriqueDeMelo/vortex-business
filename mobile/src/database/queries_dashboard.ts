import { getDb } from './database';

export type ResumoDashboard = {
  totalProdutos: number;
  totalClientesComFiado: number;
  totalFiadoPendente: number;
  ultimaSincronizacao: string | null;
};

/** Calcula um resumo rapido para a tela inicial */
export async function obterResumoDashboard(): Promise<ResumoDashboard> {
  const db = await getDb();

  const produtos = await db.getFirstAsync<{ total: number }>(
    'SELECT COUNT(*) as total FROM produtos WHERE deleted_at IS NULL'
  );

  const fiado = await db.getFirstAsync<{ qtd: number; soma: number | null }>(
    'SELECT COUNT(*) as qtd, SUM(divida_atual) as soma FROM clientes WHERE deleted_at IS NULL AND divida_atual > 0'
  );

  const meta = await db.getFirstAsync<{ valor: string }>(
    "SELECT valor FROM sync_meta WHERE chave = 'ultima_sincronizacao'"
  );

  return {
    totalProdutos: produtos?.total ?? 0,
    totalClientesComFiado: fiado?.qtd ?? 0,
    totalFiadoPendente: fiado?.soma ?? 0,
    ultimaSincronizacao: meta?.valor ?? null,
  };
}
