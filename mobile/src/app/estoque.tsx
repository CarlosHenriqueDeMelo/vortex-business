import { useCallback, useState } from 'react';
import { useFocusEffect } from 'expo-router';
import { FlatList, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Colors, Spacing } from '@/constants/theme';
import { listarProdutos, type Produto } from '@/database/queries';

export default function EstoqueScreen() {
  const [produtos, setProdutos] = useState<Produto[]>([]);
  const [carregando, setCarregando] = useState(true);

  useFocusEffect(
    useCallback(() => {
      let ativo = true;
      setCarregando(true);
      listarProdutos().then((lista) => {
        if (ativo) {
          setProdutos(lista);
          setCarregando(false);
        }
      });
      return () => {
        ativo = false;
      };
    }, [])
  );

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ThemedText type="title" style={styles.title}>
          Estoque
        </ThemedText>
        <ThemedText type="default" style={styles.subtitle}>
          Consulte produtos e preços
        </ThemedText>

        <FlatList
          data={produtos}
          keyExtractor={(item) => item.uuid}
          contentContainerStyle={styles.listContent}
          ListEmptyComponent={
            !carregando ? (
              <View style={styles.empty}>
                <ThemedText type="default" style={styles.emptyText}>
                  Nenhum produto sincronizado ainda
                </ThemedText>
              </View>
            ) : null
          }
          renderItem={({ item }) => (
            <ThemedView type="backgroundElement" style={styles.card}>
              <View style={styles.cardRow}>
                <ThemedText type="smallBold">{item.nome}</ThemedText>
                <ThemedText type="smallBold" style={styles.preco}>
                  R$ {item.preco_venda.toFixed(2)}
                </ThemedText>
              </View>
              <ThemedText type="small" style={styles.estoqueInfo}>
                {item.quantidade} em estoque
              </ThemedText>
            </ThemedView>
          )}
        />
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
  preco: { color: Colors.dark.primaryLight },
  estoqueInfo: { opacity: 0.5 },
  empty: { paddingTop: Spacing.six, alignItems: 'center' },
  emptyText: { opacity: 0.4 },
});
