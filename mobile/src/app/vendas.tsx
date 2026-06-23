import { Pressable, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Colors, Spacing } from '@/constants/theme';

export default function VendasScreen() {
  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        <ThemedText type="title" style={styles.title}>
          Vendas
        </ThemedText>
        <ThemedText type="default" style={styles.subtitle}>
          Registre uma venda no balcão
        </ThemedText>

        <View style={styles.placeholder}>
          <ThemedText type="default" style={styles.placeholderText}>
            Carrinho de venda em construção
          </ThemedText>
        </View>

        <Pressable style={styles.btnPrimary}>
          <ThemedText type="defaultSemiBold" style={styles.btnText}>
            Nova venda
          </ThemedText>
        </Pressable>
      </SafeAreaView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  safeArea: { flex: 1, paddingHorizontal: Spacing.four, paddingTop: Spacing.five },
  title: { marginBottom: Spacing.one },
  subtitle: { opacity: 0.6, marginBottom: Spacing.four },
  placeholder: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  placeholderText: { opacity: 0.4 },
  btnPrimary: {
    backgroundColor: Colors.dark.primary,
    borderRadius: Spacing.two,
    paddingVertical: Spacing.three,
    alignItems: 'center',
    marginBottom: Spacing.four,
  },
  btnText: { color: '#ffffff' },
});
