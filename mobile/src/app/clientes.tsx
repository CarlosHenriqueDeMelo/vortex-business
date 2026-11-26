import { useCallback, useState } from 'react';
import { useFocusEffect } from 'expo-router';
import { Alert, FlatList, Modal, Pressable, StyleSheet, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Colors, Spacing } from '@/constants/theme';
import { listarClientes, type Cliente } from '@/database/queries';
import { criarCliente, pagarFiado } from '@/database/queries_clientes';

export default function ClientesScreen() {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [carregando, setCarregando] = useState(true);

  const [novoAberto, setNovoAberto] = useState(false);
  const [nome, setNome] = useState('');
  const [telefone, setTelefone] = useState('');
  const [cidade, setCidade] = useState('');
  const [pagando, setPagando] = useState<Cliente | null>(null);
  const [valorPago, setValorPago] = useState('');

  const recarregar = useCallback(async () => {
    setClientes(await listarClientes());
    setCarregando(false);
  }, []);

  useFocusEffect(
    useCallback(() => {
      setCarregando(true);
      recarregar();
    }, [recarregar])
  );

  async function salvarCliente() {
    if (!nome.trim()) {
      Alert.alert('Atenção', 'Informe o nome do cliente.');
      return;
    }
    try {
      await criarCliente({ nome, telefone, cidade });
      setNome('');
      setTelefone('');
      setCidade('');
      setNovoAberto(false);
      await recarregar();
    } catch (e) {
      Alert.alert('Erro', e instanceof Error ? e.message : 'Não foi possível salvar.');
    }
  }

  function abrirPagamento(c: Cliente) {
    setPagando(c);
    setValorPago(c.divida_atual.toFixed(2));
  }

  async function confirmarPagamento() {
    if (!pagando) return;
    const valor = parseFloat(valorPago.replace(',', '.'));
    if (!valor || valor <= 0) {
      Alert.alert('Atenção', 'Informe um valor válido.');
      return;
    }
    try {
      await pagarFiado(pagando.uuid, Math.min(valor, pagando.divida_atual));
      setPagando(null);
      await recarregar();
    } catch (e) {
      Alert.alert('Erro', e instanceof Error ? e.message : 'Não foi possível registrar.');
    }
  }

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ThemedText type="title" style={styles.title}>
          Clientes
        </ThemedText>
        <ThemedText type="default" style={styles.subtitle}>
          Toque em um fiado para dar baixa
        </ThemedText>

        <Pressable style={styles.btnNovo} onPress={() => setNovoAberto(true)}>
          <ThemedText type="smallBold" style={styles.btnTexto}>
            + Novo cliente
          </ThemedText>
        </Pressable>

        <FlatList
          data={clientes}
          keyExtractor={(item) => item.uuid}
          contentContainerStyle={styles.listContent}
          ListEmptyComponent={
            !carregando ? (
              <View style={styles.empty}>
                <ThemedText type="default" style={styles.emptyText}>
                  Nenhum cliente sincronizado ainda
                </ThemedText>
              </View>
            ) : null
          }
          renderItem={({ item }) => (
            <Pressable
              disabled={!(item.divida_atual > 0)}
              onPress={() => abrirPagamento(item)}>
            <ThemedView type="backgroundElement" style={styles.card}>
              <View style={styles.cardRow}>
                <ThemedText type="smallBold">{item.nome}</ThemedText>
                {item.divida_atual > 0 ? (
                  <ThemedText type="smallBold" style={styles.divida}>
                    R$ {item.divida_atual.toFixed(2)}
                  </ThemedText>
                ) : (
                  <ThemedText type="small" style={styles.semDivida}>
                    Sem fiado
                  </ThemedText>
                )}
              </View>
              {item.telefone ? (
                <ThemedText type="small" style={styles.telefone}>
                  {item.telefone}
                </ThemedText>
              ) : null}
            </ThemedView>
            </Pressable>
          )}
        />

        <Modal visible={novoAberto} transparent animationType="slide">
          <View style={styles.overlay}>
            <ThemedView type="backgroundElement" style={styles.sheet}>
              <ThemedText type="subtitle">Novo cliente</ThemedText>
              <TextInput style={styles.input} placeholder="Nome *" placeholderTextColor={Colors.dark.textSecondary} value={nome} onChangeText={setNome} />
              <TextInput style={styles.input} placeholder="Telefone" placeholderTextColor={Colors.dark.textSecondary} keyboardType="phone-pad" value={telefone} onChangeText={setTelefone} />
              <TextInput style={styles.input} placeholder="Cidade" placeholderTextColor={Colors.dark.textSecondary} value={cidade} onChangeText={setCidade} />
              <View style={styles.botoes}>
                <Pressable style={[styles.btn, styles.btnCancel]} onPress={() => setNovoAberto(false)}>
                  <ThemedText type="smallBold">Cancelar</ThemedText>
                </Pressable>
                <Pressable style={styles.btn} onPress={salvarCliente}>
                  <ThemedText type="smallBold" style={styles.btnTexto}>Salvar</ThemedText>
                </Pressable>
              </View>
            </ThemedView>
          </View>
        </Modal>

        <Modal visible={!!pagando} transparent animationType="slide">
          <View style={styles.overlay}>
            <ThemedView type="backgroundElement" style={styles.sheet}>
              <ThemedText type="subtitle">Baixa de fiado</ThemedText>
              <ThemedText type="small">
                {pagando?.nome} deve R$ {pagando?.divida_atual.toFixed(2)}
              </ThemedText>
              <TextInput style={styles.input} keyboardType="decimal-pad" placeholder="Valor pago" placeholderTextColor={Colors.dark.textSecondary} value={valorPago} onChangeText={setValorPago} />
              <View style={styles.botoes}>
                <Pressable style={[styles.btn, styles.btnCancel]} onPress={() => setPagando(null)}>
                  <ThemedText type="smallBold">Cancelar</ThemedText>
                </Pressable>
                <Pressable style={styles.btn} onPress={confirmarPagamento}>
                  <ThemedText type="smallBold" style={styles.btnTexto}>Confirmar</ThemedText>
                </Pressable>
              </View>
            </ThemedView>
          </View>
        </Modal>
      </SafeAreaView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1, paddingHorizontal: Spacing.four, paddingTop: Spacing.five },
  title: { marginBottom: Spacing.one },
  subtitle: { opacity: 0.6, marginBottom: Spacing.four },
  listContent: { gap: Spacing.two, paddingBottom: Spacing.six },
  card: { borderRadius: Spacing.two, padding: Spacing.three, gap: Spacing.half },
  cardRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  divida: { color: Colors.dark.danger },
  semDivida: { color: Colors.dark.success },
  telefone: { opacity: 0.5 },
  btnNovo: { backgroundColor: Colors.dark.primary, borderRadius: Spacing.two, padding: Spacing.three, alignItems: 'center', marginBottom: Spacing.three },
  btnTexto: { color: '#fff' },
  overlay: { flex: 1, justifyContent: 'flex-end', backgroundColor: 'rgba(0,0,0,0.6)' },
  sheet: { padding: Spacing.four, gap: Spacing.three, borderTopLeftRadius: Spacing.four, borderTopRightRadius: Spacing.four },
  input: { backgroundColor: Colors.dark.background, color: Colors.dark.text, borderRadius: Spacing.two, padding: Spacing.three },
  botoes: { flexDirection: 'row', gap: Spacing.two },
  btn: { flex: 1, backgroundColor: Colors.dark.primary, borderRadius: Spacing.two, padding: Spacing.three, alignItems: 'center' },
  btnCancel: { backgroundColor: Colors.dark.backgroundSelected },
  empty: { paddingTop: Spacing.six, alignItems: 'center' },
  emptyText: { opacity: 0.4 },
});
