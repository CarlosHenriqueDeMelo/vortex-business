import { getDb } from './database';

export type ItemCarrinho = {
  produto_uuid: string;
  nome: string;
  quantidade: number;
  preco_unitario: number;
};

export type NovaVenda = {
  empresa_id: number;
  cliente_uuid: string | null;
  forma_pagamento: 'Dinheiro' | 'Pix' | 'Cartão' | 'Nota';
  itens: ItemCarrinho[];
  desconto?: number;
  diasPrazo?: number;
};

function gerarUuid(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

function timestampAtual(): string {
  return new Date().toISOString().slice(0, 19).replace('T', ' ');
}

function normalizarValor(valor: unknown): string | number | null {
  if (valor === undefined) return null;
  if (valor === null) return null;
  if (typeof valor === 'boolean') return valor ? 1 : 0;
  return valor as string | number;
}

export async function criarVenda(dados: NovaVenda): Promise<{ vendaUuid: string; total: number }> {
  const db = await getDb();
  const agora = timestampAtual();
  const vendaUuid = gerarUuid();

  const total = dados.itens.reduce((soma, item) => soma + item.quantidade * item.preco_unitario, 0)
    - (dados.desconto ?? 0);

  await db.withTransactionAsync(async () => {
    await db.runAsync(
      `INSERT INTO vendas (uuid, empresa_id, cliente_id, forma_pagamento, desconto, total, updated_at)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [
        normalizarValor(vendaUuid),
        normalizarValor(dados.empresa_id),
        normalizarValor(dados.cliente_uuid),
        normalizarValor(dados.forma_pagamento),
        normalizarValor(dados.desconto ?? 0),
        normalizarValor(total),
        normalizarValor(agora),
      ]
    );

    for (const item of dados.itens) {
      const itemUuid = gerarUuid();
      const subtotal = item.quantidade * item.preco_unitario;
      await db.runAsync(
        `INSERT INTO itens_venda (uuid, venda_id, produto_id, quantidade, preco_unitario, subtotal, updated_at)
         VALUES (?, ?, ?, ?, ?, ?, ?)`,
        [
          normalizarValor(itemUuid),
          normalizarValor(vendaUuid),
          normalizarValor(item.produto_uuid),
          normalizarValor(item.quantidade),
          normalizarValor(item.preco_unitario),
          normalizarValor(subtotal),
          normalizarValor(agora),
        ]
      );

      await db.runAsync(
        `UPDATE produtos SET quantidade = quantidade - ?, updated_at = ? WHERE uuid = ?`,
        [normalizarValor(item.quantidade), normalizarValor(agora), normalizarValor(item.produto_uuid)]
      );
    }

    if (dados.forma_pagamento === 'Nota' && dados.cliente_uuid) {
      await db.runAsync(
        `UPDATE clientes SET divida_atual = divida_atual + ?, updated_at = ? WHERE uuid = ?`,
        [normalizarValor(total), normalizarValor(agora), normalizarValor(dados.cliente_uuid)]
      );

      const financeiroUuid = gerarUuid();
      const dias = dados.diasPrazo ?? 30;
      const vencimento = new Date(Date.now() + dias * 24 * 60 * 60 * 1000)
        .toISOString()
        .slice(0, 10);

      await db.runAsync(
        `INSERT INTO financeiro (uuid, empresa_id, cliente_id, venda_id, descricao, tipo, valor, vencimento, status, updated_at)
         VALUES (?, ?, ?, ?, ?, 'receber', ?, ?, 'pendente', ?)`,
        [
          normalizarValor(financeiroUuid),
          normalizarValor(dados.empresa_id),
          normalizarValor(dados.cliente_uuid),
          normalizarValor(vendaUuid),
          normalizarValor(`Fiado venda ${vendaUuid.slice(0, 8)}`),
          normalizarValor(total),
          normalizarValor(vencimento),
          normalizarValor(agora),
        ]
      );
    }
  });

  return { vendaUuid, total };
}
