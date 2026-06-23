import { useCallback, useState } from 'react';
import { useFocusEffect } from 'expo-router';
import { FlatList, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Colors, Spacing } from '@/constants/theme';
import { listarClientes, type Cliente } from '@/database/queries';

export default function ClientesScreen() {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [carregando, setCarregando] = useState(true);

  useFocusEffect(
    useCallback(() => {
      let ativo = true;
      setCarregando(true);
      listarClientes().then((lista) => {
        if (ativo) {
          setClientes(lista);
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
          Clientes
        </ThemedText>
        <ThemedText type="default" style={styles.subtitle}>
          Consulte fiado em aberto
        </ThemedText>

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
  divida: { color: Colors.dark.danger },
  semDivida: { color: Colors.dark.success },
  telefone: { opacity: 0.5 },
  empty: { paddingTop: Spacing.six, alignItems: 'center' },
  emptyText: { opacity: 0.4 },
});
