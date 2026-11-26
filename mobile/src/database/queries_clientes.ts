import { getDb, getEmpresaId } from './database';
import { gerarUuid, normalizarValor, timestampAtual } from './queries_venda';

export type NovoCliente = {
  nome: string;
  telefone?: string;
  cidade?: string;
};

/** Cadastra um cliente offline; vai para o desktop na proxima sincronizacao. */
export async function criarCliente(dados: NovoCliente): Promise<string> {
  const db = await getDb();
  const uuid = gerarUuid();
  const empresaId = await getEmpresaId();
  await db.runAsync(
    `INSERT INTO clientes (uuid, empresa_id, nome, telefone, cidade, total_compras, total_gasto, divida_atual, ativo, updated_at)
     VALUES (?, ?, ?, ?, ?, 0, 0, 0, 1, ?)`,
    [
      normalizarValor(uuid),
      empresaId,
      normalizarValor(dados.nome.trim()),
      normalizarValor(dados.telefone?.trim() || null),
      normalizarValor(dados.cidade?.trim() || null),
      normalizarValor(timestampAtual()),
    ]
  );
  return uuid;
}

/**
 * Registra pagamento de fiado offline. Abate o valor da divida e,
 * quando a divida zera, marca os lancamentos pendentes do cliente como pagos.
 */
export async function pagarFiado(clienteUuid: string, valor: number): Promise<void> {
  const db = await getDb();
  const agora = timestampAtual();
  await db.withTransactionAsync(async () => {
    const cliente = await db.getFirstAsync<{ divida_atual: number }>(
      'SELECT divida_atual FROM clientes WHERE uuid = ?',
      [clienteUuid]
    );
    if (!cliente) throw new Error('Cliente nao encontrado');
    const novaDivida = Math.max(0, Math.round((cliente.divida_atual - valor) * 100) / 100);
    await db.runAsync('UPDATE clientes SET divida_atual = ?, updated_at = ? WHERE uuid = ?', [
      novaDivida,
      agora,
      clienteUuid,
    ]);
    if (novaDivida === 0) {
      await db.runAsync(
        "UPDATE financeiro SET status = 'pago', updated_at = ? WHERE cliente_id = ? AND status = 'pendente'",
        [agora, clienteUuid]
      );
    }
  });
}
