/**
 * Theme configuration
 */

import { DefaultTheme } from 'react-native-paper';

export const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#3366FF',      // High sec blue
    accent: '#FF9900',       // Low sec orange
    background: '#0A0E27',   // Dark space background
    surface: '#1A1E3A',
    text: '#FFFFFF',
    error: '#FF0000',        // Null sec red
    success: '#00FF00',
    warning: '#FF9900',
  },
  dark: true,
};

export const securityColors = {
  high_sec: '#3366FF',
  low_sec: '#FF9900',
  null_sec: '#FF0000',
  wormhole: '#9933FF',
};

export const dangerColors = {
  safe: '#00FF00',
  moderate: '#FFAA00',
  dangerous: '#FF0000',
  unknown: '#888888',
};
