import { useEffect, useState } from 'react';
import { Pressable, StyleSheet, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Colors, Spacing } from '@/constants/theme';
import { getMeta, setMeta } from '@/database/database';
import { sincronizar } from '@/sync/syncClient';

const EMPRESA_ID = 1;

export default function SincronizarScreen() {
  const [ip, setIp] = useState('');
  const [token, setToken] = useState('');
  const [status, setStatus] = useState<'idle' | 'sincronizando' | 'sucesso' | 'erro'>('idle');
  const [mensagem, setMensagem] = useState('');

  useEffect(() => {
    getMeta('ultimo_ip').then((salvo) => {
      if (salvo) setIp(salvo);
    });
    getMeta('sync_token').then((salvo) => {
      if (salvo) setToken(salvo);
    });
  }, []);

  async function handleSincronizar() {
    if (!ip.trim() || !token.trim()) {
      setStatus('erro');
      setMensagem('Preencha o endereço e o código de acesso');
      return;
    }
    setStatus('sincronizando');
    setMensagem('');

    const resultado = await sincronizar(ip.trim(), EMPRESA_ID, token.trim());

    if (resultado.sucesso) {
      setStatus('sucesso');
      setMensagem(`Enviados ${resultado.enviados ?? 0}, recebidos ${resultado.recebidos ?? 0}`);
      await setMeta('ultimo_ip', ip.trim());
      await setMeta('sync_token', token.trim());
    } else {
      setStatus('erro');
      setMensagem(resultado.mensagem);
    }
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
          />

          <ThemedText type="small" style={[styles.label, styles.labelSegundo]}>
            Código de acesso
          </ThemedText>
          <TextInput
            style={styles.input}
            placeholder="Cole o código fornecido no computador"
            placeholderTextColor={Colors.dark.textSecondary}
            value={token}
            onChangeText={setToken}
            autoCapitalize="none"
            autoCorrect={false}
            secureTextEntry
          />

          <ThemedText type="small" style={styles.hint}>
            O endereço e o código aparecem na tela "Sincronização" do programa no
            computador. Configure uma vez só — os dois precisam estar na mesma rede Wi-Fi
            no momento de sincronizar.
          </ThemedText>
        </ThemedView>

        <Pressable
          style={styles.btnPrimary}
          onPress={handleSincronizar}
          disabled={status === 'sincronizando'}>
          <ThemedText type="smallBold" style={styles.btnText}>
            {status === 'sincronizando' ? 'Sincronizando...' : 'Sincronizar agora'}
          </ThemedText>
        </Pressable>

        {status === 'sucesso' ? (
          <ThemedText type="small" style={styles.statusSucesso}>
            Sincronizado com sucesso{mensagem ? ` — ${mensagem}` : ''}
          </ThemedText>
        ) : null}
        {status === 'erro' ? (
          <ThemedText type="small" style={styles.statusErro}>
            {mensagem || 'Não foi possível conectar.'}
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
  labelSegundo: { marginTop: Spacing.two },
  input: {
    color: Colors.dark.text,
    fontSize: 16,
    fontFamily: 'monospace',
    borderBottomWidth: 1,
    borderBottomColor: Colors.dark.border,
    paddingVertical: Spacing.two,
  },
  hint: { opacity: 0.4, lineHeight: 18, marginTop: Spacing.two },
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
