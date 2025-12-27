/**
 * Home Screen
 * Main dashboard with quick actions
 */
import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { GatekeeperAPI } from '../services/GatekeeperAPI';
import { THEME, ROUTE_PROFILES } from '../config';
import { RootStackParamList } from '../navigation/types';

type HomeScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Home'>;

export const HomeScreen: React.FC = () => {
  const navigation = useNavigation<HomeScreenNavigationProp>();
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking');

  useEffect(() => {
    checkApiStatus();
  }, []);

  const checkApiStatus = async () => {
    setApiStatus('checking');
    const isOnline = await GatekeeperAPI.testConnection();
    setApiStatus(isOnline ? 'online' : 'offline');
  };

  const StatusIndicator = () => {
    let color: string;
    let text: string;

    switch (apiStatus) {
      case 'online':
        color = THEME.colors.riskGreen;
        text = 'API Online';
        break;
      case 'offline':
        color = THEME.colors.riskRed;
        text = 'API Offline';
        break;
      default:
        color = THEME.colors.textSecondary;
        text = 'Checking...';
    }

    return (
      <View style={styles.statusContainer}>
        <View style={[styles.statusDot, { backgroundColor: color }]} />
        <Text style={[styles.statusText, { color }]}>{text}</Text>
        {apiStatus === 'checking' && (
          <ActivityIndicator size="small" color={THEME.colors.textSecondary} />
        )}
      </View>
    );
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.title}>EVE Gatekeeper</Text>
        <Text style={styles.subtitle}>Intel & Route Planning</Text>
        <StatusIndicator />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <TouchableOpacity
          style={styles.primaryButton}
          onPress={() => navigation.navigate('Route')}
        >
          <Text style={styles.primaryButtonText}>Plan Route</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Route Profiles</Text>
        <View style={styles.profilesGrid}>
          {Object.entries(ROUTE_PROFILES).map(([key, profile]) => (
            <TouchableOpacity
              key={key}
              style={[styles.profileCard, { borderColor: profile.color }]}
              onPress={() => navigation.navigate('Route', { profile: key as any })}
            >
              <Text style={[styles.profileName, { color: profile.color }]}>
                {profile.label}
              </Text>
              <Text style={styles.profileDescription}>{profile.description}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Tools</Text>
        <View style={styles.toolsGrid}>
          <TouchableOpacity
            style={styles.toolCard}
            onPress={() => navigation.navigate('Settings')}
          >
            <Text style={styles.toolName}>Settings</Text>
            <Text style={styles.toolDescription}>Configure API & preferences</Text>
          </TouchableOpacity>
        </View>
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
  header: {
    alignItems: 'center',
    paddingVertical: THEME.spacing.xl,
  },
  title: {
    color: THEME.colors.text,
    fontSize: 28,
    fontWeight: 'bold',
  },
  subtitle: {
    color: THEME.colors.textSecondary,
    fontSize: 16,
    marginTop: THEME.spacing.xs,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: THEME.spacing.md,
    gap: THEME.spacing.xs,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  statusText: {
    fontSize: 12,
    fontWeight: '500',
  },
  section: {
    marginBottom: THEME.spacing.lg,
  },
  sectionTitle: {
    color: THEME.colors.textSecondary,
    fontSize: 12,
    textTransform: 'uppercase',
    fontWeight: '600',
    marginBottom: THEME.spacing.sm,
  },
  primaryButton: {
    backgroundColor: THEME.colors.primary,
    borderRadius: THEME.borderRadius.lg,
    padding: THEME.spacing.md,
    alignItems: 'center',
  },
  primaryButtonText: {
    color: THEME.colors.text,
    fontSize: 18,
    fontWeight: 'bold',
  },
  profilesGrid: {
    gap: THEME.spacing.sm,
  },
  profileCard: {
    backgroundColor: THEME.colors.card,
    borderRadius: THEME.borderRadius.lg,
    padding: THEME.spacing.md,
    borderLeftWidth: 4,
  },
  profileName: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  profileDescription: {
    color: THEME.colors.textSecondary,
    fontSize: 12,
    marginTop: 2,
  },
  toolsGrid: {
    gap: THEME.spacing.sm,
  },
  toolCard: {
    backgroundColor: THEME.colors.card,
    borderRadius: THEME.borderRadius.lg,
    padding: THEME.spacing.md,
  },
  toolName: {
    color: THEME.colors.text,
    fontSize: 16,
    fontWeight: '600',
  },
  toolDescription: {
    color: THEME.colors.textSecondary,
    fontSize: 12,
    marginTop: 2,
  },
});

export default HomeScreen;
