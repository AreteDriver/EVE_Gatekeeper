/**
 * Settings Screen
 * Configure API URL and app preferences
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { GatekeeperAPI } from '../services/GatekeeperAPI';
import { THEME } from '../config';

const STORAGE_KEY = '@gatekeeper_api_url';

export const SettingsScreen: React.FC = () => {
  const [apiUrl, setApiUrl] = useState(GatekeeperAPI.getBaseUrl());
  const [testing, setTesting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'unknown' | 'success' | 'failed'>('unknown');

  useEffect(() => {
    loadSavedUrl();
  }, []);

  const loadSavedUrl = async () => {
    try {
      const savedUrl = await AsyncStorage.getItem(STORAGE_KEY);
      if (savedUrl) {
        setApiUrl(savedUrl);
        GatekeeperAPI.setBaseUrl(savedUrl);
      }
    } catch (err) {
      console.error('Failed to load saved URL:', err);
    }
  };

  const handleTestConnection = async () => {
    setTesting(true);
    setConnectionStatus('unknown');

    // Temporarily set the URL for testing
    const originalUrl = GatekeeperAPI.getBaseUrl();
    GatekeeperAPI.setBaseUrl(apiUrl.trim());

    try {
      const success = await GatekeeperAPI.testConnection();
      setConnectionStatus(success ? 'success' : 'failed');

      if (!success) {
        // Restore original URL if test failed
        GatekeeperAPI.setBaseUrl(originalUrl);
      }
    } catch {
      setConnectionStatus('failed');
      GatekeeperAPI.setBaseUrl(originalUrl);
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    if (!apiUrl.trim()) {
      Alert.alert('Error', 'Please enter a valid API URL');
      return;
    }

    try {
      await AsyncStorage.setItem(STORAGE_KEY, apiUrl.trim());
      GatekeeperAPI.setBaseUrl(apiUrl.trim());
      Alert.alert('Success', 'API URL saved successfully');
    } catch (err) {
      Alert.alert('Error', 'Failed to save settings');
    }
  };

  const handleReset = async () => {
    Alert.alert(
      'Reset Settings',
      'Are you sure you want to reset to default settings?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Reset',
          style: 'destructive',
          onPress: async () => {
            const defaultUrl = 'http://localhost:8000';
            setApiUrl(defaultUrl);
            GatekeeperAPI.setBaseUrl(defaultUrl);
            await AsyncStorage.removeItem(STORAGE_KEY);
            setConnectionStatus('unknown');
          },
        },
      ]
    );
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>API Configuration</Text>

        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>Gatekeeper API URL</Text>
          <TextInput
            style={styles.input}
            value={apiUrl}
            onChangeText={setApiUrl}
            placeholder="http://localhost:8000"
            placeholderTextColor={THEME.colors.textSecondary}
            autoCapitalize="none"
            autoCorrect={false}
            keyboardType="url"
          />
          <Text style={styles.inputHint}>
            Enter the URL of your Gatekeeper backend server
          </Text>
        </View>

        <View style={styles.statusContainer}>
          <Text style={styles.statusLabel}>Connection Status:</Text>
          <View style={styles.statusRow}>
            {connectionStatus === 'success' && (
              <>
                <View style={[styles.statusDot, { backgroundColor: THEME.colors.riskGreen }]} />
                <Text style={[styles.statusText, { color: THEME.colors.riskGreen }]}>
                  Connected
                </Text>
              </>
            )}
            {connectionStatus === 'failed' && (
              <>
                <View style={[styles.statusDot, { backgroundColor: THEME.colors.riskRed }]} />
                <Text style={[styles.statusText, { color: THEME.colors.riskRed }]}>
                  Connection Failed
                </Text>
              </>
            )}
            {connectionStatus === 'unknown' && (
              <Text style={styles.statusText}>Not tested</Text>
            )}
          </View>
        </View>

        <View style={styles.buttonRow}>
          <TouchableOpacity
            style={[styles.button, styles.testButton]}
            onPress={handleTestConnection}
            disabled={testing}
          >
            {testing ? (
              <ActivityIndicator color={THEME.colors.text} size="small" />
            ) : (
              <Text style={styles.buttonText}>Test Connection</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.saveButton]}
            onPress={handleSave}
          >
            <Text style={styles.buttonText}>Save</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        <View style={styles.aboutCard}>
          <Text style={styles.aboutTitle}>EVE Gatekeeper</Text>
          <Text style={styles.aboutText}>Version 1.0.0</Text>
          <Text style={styles.aboutDescription}>
            Intel and route planning companion for EVE Online pilots.
          </Text>
        </View>
      </View>

      <View style={styles.section}>
        <TouchableOpacity style={styles.resetButton} onPress={handleReset}>
          <Text style={styles.resetButtonText}>Reset to Defaults</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: THEME.colors.background,
  },
  content: {
    padding: THEME.spacing.md,
  },
  section: {
    marginBottom: THEME.spacing.xl,
  },
  sectionTitle: {
    color: THEME.colors.textSecondary,
    fontSize: 12,
    textTransform: 'uppercase',
    fontWeight: '600',
    marginBottom: THEME.spacing.sm,
  },
  inputGroup: {
    marginBottom: THEME.spacing.md,
  },
  inputLabel: {
    color: THEME.colors.text,
    fontSize: 14,
    fontWeight: '500',
    marginBottom: THEME.spacing.xs,
  },
  input: {
    backgroundColor: THEME.colors.card,
    borderRadius: THEME.borderRadius.md,
    padding: THEME.spacing.md,
    color: THEME.colors.text,
    fontSize: 16,
    borderWidth: 1,
    borderColor: THEME.colors.border,
  },
  inputHint: {
    color: THEME.colors.textSecondary,
    fontSize: 12,
    marginTop: THEME.spacing.xs,
  },
  statusContainer: {
    marginBottom: THEME.spacing.md,
  },
  statusLabel: {
    color: THEME.colors.textSecondary,
    fontSize: 12,
    marginBottom: THEME.spacing.xs,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: THEME.spacing.xs,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  statusText: {
    color: THEME.colors.textSecondary,
    fontSize: 14,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: THEME.spacing.sm,
  },
  button: {
    flex: 1,
    paddingVertical: THEME.spacing.md,
    borderRadius: THEME.borderRadius.md,
    alignItems: 'center',
  },
  testButton: {
    backgroundColor: THEME.colors.card,
    borderWidth: 1,
    borderColor: THEME.colors.border,
  },
  saveButton: {
    backgroundColor: THEME.colors.primary,
  },
  buttonText: {
    color: THEME.colors.text,
    fontSize: 14,
    fontWeight: '600',
  },
  aboutCard: {
    backgroundColor: THEME.colors.card,
    borderRadius: THEME.borderRadius.lg,
    padding: THEME.spacing.md,
  },
  aboutTitle: {
    color: THEME.colors.text,
    fontSize: 18,
    fontWeight: 'bold',
  },
  aboutText: {
    color: THEME.colors.textSecondary,
    fontSize: 12,
    marginTop: 2,
  },
  aboutDescription: {
    color: THEME.colors.textSecondary,
    fontSize: 14,
    marginTop: THEME.spacing.sm,
  },
  resetButton: {
    paddingVertical: THEME.spacing.md,
    alignItems: 'center',
  },
  resetButtonText: {
    color: THEME.colors.riskRed,
    fontSize: 14,
  },
});

export default SettingsScreen;
