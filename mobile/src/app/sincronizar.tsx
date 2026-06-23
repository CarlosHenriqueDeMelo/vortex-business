import { useState } from 'react';
import { Pressable, StyleSheet, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Colors, Spacing } from '@/constants/theme';

export default function SincronizarScreen() {
  const [ip, setIp] = useState('');
  const [status, setStatus] = useState<'idle' | 'sincronizando' | 'sucesso' | 'erro'>('idle');

  function handleSincronizar() {
    if (!ip.trim()) return;
    setStatus('sincronizando');
  }

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ThemedText type="title" style={styles.title}>
          Sincronização
        </ThemedText>
        <ThemedText type="default" style={styles.subtitle}>
          Conecte com o computador da loja
        </ThemedText>

        <ThemedView type="backgroundElement" style={styles.card}>
          <ThemedText type="small" style={styles.label}>
            Endereço do computador
          </ThemedText>
          <TextInput
            style={styles.input}
            placeholder="192.168.1.50:5000"
            placeholderTextColor={Colors.dark.textSecondary}
            value={ip}
            onChangeText={setIp}
            autoCapitalize="none"
            autoCorrect={false}
            keyboardType="default"
          />
          <ThemedText type="small" style={styles.hint}>
            Esse endereço aparece na tela "Sincronização" do programa no computador.
            Os dois precisam estar na mesma rede Wi-Fi.
          </ThemedText>
        </ThemedView>

        <Pressable style={styles.btnPrimary} onPress={handleSincronizar}>
          <ThemedText type="defaultSemiBold" style={styles.btnText}>
            {status === 'sincronizando' ? 'Sincronizando...' : 'Sincronizar agora'}
          </ThemedText>
        </Pressable>

        {status === 'sucesso' ? (
          <ThemedText type="small" style={styles.statusSucesso}>
            Sincronizado com sucesso
          </ThemedText>
        ) : null}
        {status === 'erro' ? (
          <ThemedText type="small" style={styles.statusErro}>
            Não foi possível conectar. Verifique o endereço e a rede Wi-Fi.
          </ThemedText>
        ) : null}
      </SafeAreaView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1, paddingHorizontal: Spacing.four, paddingTop: Spacing.five },
  title: { marginBottom: Spacing.one },
  subtitle: { opacity: 0.6, marginBottom: Spacing.four },
  card: { borderRadius: Spacing.two, padding: Spacing.three, gap: Spacing.two, marginBottom: Spacing.four },
  label: { opacity: 0.6, textTransform: 'uppercase', letterSpacing: 0.5 },
  input: {
    color: Colors.dark.text,
    fontSize: 18,
    fontFamily: 'monospace',
    borderBottomWidth: 1,
    borderBottomColor: Colors.dark.border,
    paddingVertical: Spacing.two,
  },
  hint: { opacity: 0.4, lineHeight: 18 },
  btnPrimary: {
    backgroundColor: Colors.dark.primary,
    borderRadius: Spacing.two,
    paddingVertical: Spacing.three,
    alignItems: 'center',
  },
  btnText: { color: '#ffffff' },
  statusSucesso: { color: Colors.dark.success, textAlign: 'center', marginTop: Spacing.three },
  statusErro: { color: Colors.dark.danger, textAlign: 'center', marginTop: Spacing.three },
});
