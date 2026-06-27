import { useCallback, useState } from 'react';
import { useFocusEffect } from 'expo-router';
import { StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Colors, Spacing } from '@/constants/theme';
import { obterResumoDashboard, type ResumoDashboard } from '@/database/queries_dashboard';

function formatarDataHora(iso: string | null): string {
  if (!iso) return 'Nunca sincronizado';
  const data = new Date(iso);
  return data.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
}

export default function InicioScreen() {
  const [resumo, setResumo] = useState<ResumoDashboard | null>(null);

  useFocusEffect(
    useCallback(() => {
      obterResumoDashboard().then(setResumo);
    }, [])
  );

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ThemedText type="title" style={styles.title}>
          Vortex Business
        </ThemedText>
        <ThemedText type="default" style={styles.subtitle}>
          Bem-vindo de volta
        </ThemedText>

        <View style={styles.metrics}>
          <ThemedView type="backgroundElement" style={styles.metricCard}>
            <ThemedText type="small" style={styles.metricLabel}>Produtos no estoque</ThemedText>
            <ThemedText type="title" style={styles.metricValue}>
              {resumo?.totalProdutos ?? '—'}
            </ThemedText>
          </ThemedView>

          <ThemedView type="backgroundElement" style={styles.metricCard}>
            <ThemedText type="small" style={styles.metricLabel}>Clientes com fiado</ThemedText>
            <ThemedText type="title" style={styles.metricValue}>
              {resumo?.totalClientesComFiado ?? '—'}
            </ThemedText>
          </ThemedView>

          <ThemedView type="backgroundElement" style={[styles.metricCard, styles.metricCardLarga]}>
            <ThemedText type="small" style={styles.metricLabel}>Total em fiado pendente</ThemedText>
            <ThemedText type="title" style={styles.metricValueDestaque}>
              R$ {(resumo?.totalFiadoPendente ?? 0).toFixed(2)}
            </ThemedText>
          </ThemedView>
        </View>

        <ThemedView type="backgroundElement" style={styles.syncInfo}>
          <ThemedText type="small" style={styles.syncLabel}>Última sincronização</ThemedText>
          <ThemedText type="small" style={styles.syncValue}>
            {formatarDataHora(resumo?.ultimaSincronizacao ?? null)}
          </ThemedText>
        </ThemedView>
      </SafeAreaView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1, paddingHorizontal: Spacing.four, paddingTop: Spacing.five },
  title: { marginBottom: Spacing.one },
  subtitle: { opacity: 0.6, marginBottom: Spacing.four },
  metrics: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.two, marginBottom: Spacing.three },
  metricCard: {
    flexGrow: 1, flexBasis: '45%', borderRadius: Spacing.two, padding: Spacing.three, gap: Spacing.one,
  },
  metricCardLarga: { flexBasis: '100%' },
  metricLabel: { opacity: 0.5 },
  metricValue: { fontSize: 24 },
  metricValueDestaque: { fontSize: 24, color: Colors.dark.danger },
  syncInfo: {
    borderRadius: Spacing.two, padding: Spacing.three,
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
  },
  syncLabel: { opacity: 0.5 },
  syncValue: { opacity: 0.8 },
});
