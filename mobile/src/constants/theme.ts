/**
 * Tema visual do Vortex Business Mobile.
 * Segue a identidade visual do desktop: tema escuro, roxo #534AB7.
 */

import '@/global.css';

import { Platform } from 'react-native';

export const Colors = {
  light: {
    text: '#ffffff',
    background: '#0d0d0f',
    backgroundElement: '#161618',
    backgroundSelected: '#1a1040',
    textSecondary: '#aaaaaa',
    primary: '#534AB7',
    primaryLight: '#7F77DD',
    border: '#1e1e22',
    success: '#1D9E75',
    warning: '#EF9F27',
    danger: '#E24B4A',
    info: '#378ADD',
  },
  dark: {
    text: '#ffffff',
    background: '#0d0d0f',
    backgroundElement: '#161618',
    backgroundSelected: '#1a1040',
    textSecondary: '#aaaaaa',
    primary: '#534AB7',
    primaryLight: '#7F77DD',
    border: '#1e1e22',
    success: '#1D9E75',
    warning: '#EF9F27',
    danger: '#E24B4A',
    info: '#378ADD',
  },
} as const;

export type ThemeColor = keyof typeof Colors.light & keyof typeof Colors.dark;

export const Fonts = Platform.select({
  ios: {
    sans: 'system-ui',
    serif: 'ui-serif',
    rounded: 'ui-rounded',
    mono: 'ui-monospace',
  },
  default: {
    sans: 'normal',
    serif: 'serif',
    rounded: 'normal',
    mono: 'monospace',
  },
  web: {
    sans: 'var(--font-display)',
    serif: 'var(--font-serif)',
    rounded: 'var(--font-rounded)',
    mono: 'var(--font-mono)',
  },
});

export const Spacing = {
  half: 2,
  one: 4,
  two: 8,
  three: 16,
  four: 24,
  five: 32,
  six: 64,
} as const;

export const BottomTabInset = Platform.select({ ios: 50, android: 80 }) ?? 0;
export const MaxContentWidth = 800;
