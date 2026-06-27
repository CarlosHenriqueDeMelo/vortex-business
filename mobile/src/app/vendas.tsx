import { useCallback, useState } from 'react';
import { useFocusEffect } from 'expo-router';
import {
  FlatList,
  Modal,
  Pressable,
  StyleSheet,
  TextInput,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Colors, Spacing } from '@/constants/theme';
import { criarVenda, type ItemCarrinho } from '@/database/queries_venda';
import { listarClientes, listarProdutos, type Cliente, type Produto } from '@/database/queries';

const EMPRESA_ID = 1;
const FORMAS_PAGAMENTO = ['Dinheiro', 'Pix', 'Cartão', 'Nota'] as const;

export default function VendasScreen() {
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [carrinho, setCarrinho] = useState<ItemCarrinho[]>([]);
  const [clienteSelecionado, setClienteSelecionado] = useState<Cliente | null>(null);
  const [formaPagamento, setFormaPagamento] = useState<(typeof FORMAS_PAGAMENTO)[number]>('Dinheiro');
  const [modalProdutoAberto, setModalProdutoAberto] = useState(false);
  const [modalClienteAberto, setModalClienteAberto] = useState(false);
  const [busca, setBusca] = useState('');
  const [status, setStatus] = useState<'idle' | 'salvando' | 'sucesso' | 'erro'>('idle');
  const [mensagemErro, setMensagemErro] = useState('');

  useFocusEffect(
    useCallback(() => {
      listarProdutos().then(setProdutos);
      listarClientes().then(setClientes);
    }, [])
  );

  function adicionarAoCarrinho(produto: Produto) {
    setCarrinho((atual) => {
      const existente = atual.find((i) => i.produto_uuid === produto.uuid);
      if (existente) {
        return atual.map((i) =>
          i.produto_uuid === produto.uuid ? { ...i, quantidade: i.quantidade + 1 } : i
        );
      }
      return [
        ...atual,
        { produto_uuid: produto.uuid, nome: produto.nome, quantidade: 1, preco_unitario: produto.preco_venda },
      ];
    });
    setModalProdutoAberto(false);
    setBusca('');
  }

  function removerDoCarrinho(produtoUuid: string) {
    setCarrinho((atual) => atual.filter((i) => i.produto_uuid !== produtoUuid));
  }

  function alterarQuantidade(produtoUuid: string, delta: number) {
    setCarrinho((atual) =>
      atual
        .map((i) =>
          i.produto_uuid === produtoUuid ? { ...i, quantidade: Math.max(1, i.quantidade + delta) } : i
        )
    );
  }

  const total = carrinho.reduce((soma, item) => soma + item.quantidade * item.preco_unitario, 0);

  async function finalizarVenda() {
    if (carrinho.length === 0) return;
    if (formaPagamento === 'Nota' && !clienteSelecionado) {
      setStatus('erro');
      setMensagemErro('Venda fiado (Nota) precisa de um cliente selecionado');
      return;
    }

    setStatus('salvando');
    try {
      await criarVenda({
        empresa_id: EMPRESA_ID,
        cliente_uuid: clienteSelecionado?.uuid ?? null,
        forma_pagamento: formaPagamento,
        itens: carrinho,
      });
      setStatus('sucesso');
      setCarrinho([]);
      setClienteSelecionado(null);
      setFormaPagamento('Dinheiro');
      listarProdutos().then(setProdutos);
    } catch (e) {
      setStatus('erro');
      setMensagemErro('Não foi possível salvar a venda. Tente novamente.');
    }
  }

  const produtosFiltrados = produtos.filter((p) =>
    p.nome.toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ThemedText type="title" style={styles.title}>
          Vendas
        </ThemedText>
        <ThemedText type="default" style={styles.subtitle}>
          Registre uma venda no balcão
        </ThemedText>

        <FlatList
          data={carrinho}
          keyExtractor={(item) => item.produto_uuid}
          contentContainerStyle={styles.carrinhoLista}
          ListEmptyComponent={
            <View style={styles.empty}>
              <ThemedText type="default" style={styles.emptyText}>
                Carrinho vazio
              </ThemedText>
            </View>
          }
          renderItem={({ item }) => (
            <ThemedView type="backgroundElement" style={styles.itemCard}>
              <View style={styles.itemInfo}>
                <ThemedText type="smallBold">{item.nome}</ThemedText>
                <ThemedText type="small" style={styles.itemPreco}>
                  R$ {item.preco_unitario.toFixed(2)} cada
                </ThemedText>
              </View>
              <View style={styles.itemControles}>
                <Pressable onPress={() => alterarQuantidade(item.produto_uuid, -1)} style={styles.btnQtd}>
                  <ThemedText type="smallBold">−</ThemedText>
                </Pressable>
                <ThemedText type="smallBold" style={styles.qtdTexto}>{item.quantidade}</ThemedText>
                <Pressable onPress={() => alterarQuantidade(item.produto_uuid, 1)} style={styles.btnQtd}>
                  <ThemedText type="smallBold">+</ThemedText>
                </Pressable>
                <Pressable onPress={() => removerDoCarrinho(item.produto_uuid)} style={styles.btnRemover}>
                  <ThemedText type="small" style={styles.btnRemoverTexto}>Remover</ThemedText>
                </Pressable>
              </View>
            </ThemedView>
          )}
        />

        <Pressable style={styles.btnSecundario} onPress={() => setModalProdutoAberto(true)}>
          <ThemedText type="smallBold" style={styles.btnSecundarioTexto}>+ Adicionar produto</ThemedText>
        </Pressable>

        <Pressable style={styles.btnSecundario} onPress={() => setModalClienteAberto(true)}>
          <ThemedText type="smallBold" style={styles.btnSecundarioTexto}>
            {clienteSelecionado ? `Cliente: ${clienteSelecionado.nome}` : 'Selecionar cliente (opcional)'}
          </ThemedText>
        </Pressable>

        <View style={styles.formasPagamento}>
          {FORMAS_PAGAMENTO.map((forma) => (
            <Pressable
              key={forma}
              onPress={() => setFormaPagamento(forma)}
              style={[styles.formaBtn, formaPagamento === forma && styles.formaBtnAtiva]}>
              <ThemedText
                type="small"
                style={formaPagamento === forma ? styles.formaTextoAtivo : styles.formaTexto}>
                {forma}
              </ThemedText>
            </Pressable>
          ))}
        </View>

        <View style={styles.totalRow}>
          <ThemedText type="default">Total</ThemedText>
          <ThemedText type="title" style={styles.totalValor}>R$ {total.toFixed(2)}</ThemedText>
        </View>

        <Pressable
          style={styles.btnPrimary}
          onPress={finalizarVenda}
          disabled={status === 'salvando' || carrinho.length === 0}>
          <ThemedText type="smallBold" style={styles.btnText}>
            {status === 'salvando' ? 'Salvando...' : 'Finalizar venda'}
          </ThemedText>
        </Pressable>

        {status === 'sucesso' ? (
          <ThemedText type="small" style={styles.statusSucesso}>Venda registrada com sucesso</ThemedText>
        ) : null}
        {status === 'erro' ? (
          <ThemedText type="small" style={styles.statusErro}>{mensagemErro}</ThemedText>
        ) : null}
      </SafeAreaView>

      <Modal visible={modalProdutoAberto} animationType="slide" onRequestClose={() => setModalProdutoAberto(false)}>
        <ThemedView style={styles.modalContainer}>
          <SafeAreaView style={styles.modalSafeArea}>
            <ThemedText type="title">Selecionar produto</ThemedText>
            <TextInput
              style={styles.buscaInput}
              placeholder="Buscar produto..."
              placeholderTextColor={Colors.dark.textSecondary}
              value={busca}
              onChangeText={setBusca}
            />
            <FlatList
              data={produtosFiltrados}
              keyExtractor={(item) => item.uuid}
              renderItem={({ item }) => (
                <Pressable onPress={() => adicionarAoCarrinho(item)}>
                  <ThemedView type="backgroundElement" style={styles.produtoModalCard}>
                    <ThemedText type="smallBold">{item.nome}</ThemedText>
                    <ThemedText type="small" style={styles.itemPreco}>
                      R$ {item.preco_venda.toFixed(2)} — {item.quantidade} em estoque
                    </ThemedText>
                  </ThemedView>
                </Pressable>
              )}
            />
            <Pressable style={styles.btnFechar} onPress={() => setModalProdutoAberto(false)}>
              <ThemedText type="smallBold">Fechar</ThemedText>
            </Pressable>
          </SafeAreaView>
        </ThemedView>
      </Modal>

      <Modal visible={modalClienteAberto} animationType="slide" onRequestClose={() => setModalClienteAberto(false)}>
        <ThemedView style={styles.modalContainer}>
          <SafeAreaView style={styles.modalSafeArea}>
            <ThemedText type="title">Selecionar cliente</ThemedText>
            <Pressable
              onPress={() => {
                setClienteSelecionado(null);
                setModalClienteAberto(false);
              }}>
              <ThemedView type="backgroundElement" style={styles.produtoModalCard}>
                <ThemedText type="smallBold">Sem cliente</ThemedText>
              </ThemedView>
            </Pressable>
            <FlatList
              data={clientes}
              keyExtractor={(item) => item.uuid}
              renderItem={({ item }) => (
                <Pressable
                  onPress={() => {
                    setClienteSelecionado(item);
                    setModalClienteAberto(false);
                  }}>
                  <ThemedView type="backgroundElement" style={styles.produtoModalCard}>
                    <ThemedText type="smallBold">{item.nome}</ThemedText>
                  </ThemedView>
                </Pressable>
              )}
            />
            <Pressable style={styles.btnFechar} onPress={() => setModalClienteAberto(false)}>
              <ThemedText type="smallBold">Fechar</ThemedText>
            </Pressable>
          </SafeAreaView>
        </ThemedView>
      </Modal>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1, paddingHorizontal: Spacing.four, paddingTop: Spacing.five },
  title: { marginBottom: Spacing.one },
  subtitle: { opacity: 0.6, marginBottom: Spacing.three },
  carrinhoLista: { gap: Spacing.two, paddingBottom: Spacing.two },
  itemCard: { borderRadius: Spacing.two, padding: Spacing.three, gap: Spacing.two },
  itemInfo: { gap: 2 },
  itemPreco: { opacity: 0.5 },
  itemControles: { flexDirection: 'row', alignItems: 'center', gap: Spacing.two },
  btnQtd: {
    width: 28, height: 28, borderRadius: 14,
    backgroundColor: Colors.dark.border,
    alignItems: 'center', justifyContent: 'center',
  },
  qtdTexto: { minWidth: 24, textAlign: 'center' },
  btnRemover: { marginLeft: 'auto' },
  btnRemoverTexto: { color: Colors.dark.danger },
  empty: { paddingVertical: Spacing.four, alignItems: 'center' },
  emptyText: { opacity: 0.4 },
  btnSecundario: {
    borderWidth: 1, borderColor: Colors.dark.border, borderRadius: Spacing.two,
    paddingVertical: Spacing.two, alignItems: 'center', marginTop: Spacing.two,
  },
  btnSecundarioTexto: { color: Colors.dark.primaryLight },
  formasPagamento: { flexDirection: 'row', gap: Spacing.two, marginTop: Spacing.three, flexWrap: 'wrap' },
  formaBtn: {
    paddingVertical: Spacing.one, paddingHorizontal: Spacing.three,
    borderRadius: Spacing.two, borderWidth: 1, borderColor: Colors.dark.border,
  },
  formaBtnAtiva: { backgroundColor: Colors.dark.primary, borderColor: Colors.dark.primary },
  formaTexto: { opacity: 0.7 },
  formaTextoAtivo: { color: '#ffffff' },
  totalRow: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
    marginTop: Spacing.four, marginBottom: Spacing.two,
  },
  totalValor: { color: Colors.dark.primaryLight },
  btnPrimary: {
    backgroundColor: Colors.dark.primary, borderRadius: Spacing.two,
    paddingVertical: Spacing.three, alignItems: 'center', marginBottom: Spacing.four,
  },
  btnText: { color: '#ffffff' },
  statusSucesso: { color: Colors.dark.success, textAlign: 'center', marginBottom: Spacing.three },
  statusErro: { color: Colors.dark.danger, textAlign: 'center', marginBottom: Spacing.three },
  modalContainer: { flex: 1 },
  modalSafeArea: { flex: 1, paddingHorizontal: Spacing.four, paddingTop: Spacing.five, gap: Spacing.three },
  buscaInput: {
    color: Colors.dark.text, borderBottomWidth: 1, borderBottomColor: Colors.dark.border,
    paddingVertical: Spacing.two, fontSize: 16,
  },
  produtoModalCard: { borderRadius: Spacing.two, padding: Spacing.three, marginBottom: Spacing.two },
  btnFechar: {
    borderWidth: 1, borderColor: Colors.dark.border, borderRadius: Spacing.two,
    paddingVertical: Spacing.two, alignItems: 'center', marginBottom: Spacing.four,
  },
});
