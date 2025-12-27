/**
 * System Card Component
 * Displays solar system information
 */
import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { System, RiskReport } from '../types';
import { formatSecurityStatus, getSecurityCategory } from '../utils/formatting';
import { RiskBadge } from './RiskBadge';
import { THEME } from '../config';

interface SystemCardProps {
  system: System;
  riskReport?: RiskReport;
  onPress?: () => void;
  compact?: boolean;
}

export const SystemCard: React.FC<SystemCardProps> = ({
  system,
  riskReport,
  onPress,
  compact = false,
}) => {
  const security = formatSecurityStatus(system.security_status);
  const category = getSecurityCategory(system.security_status);

  const Container = onPress ? TouchableOpacity : View;

  if (compact) {
    return (
      <Container
        style={styles.compactContainer}
        onPress={onPress}
        activeOpacity={0.7}
      >
        <View style={styles.compactLeft}>
          <Text style={styles.compactName}>{system.name}</Text>
          <Text style={[styles.compactSecurity, { color: security.color }]}>
            {security.text}
          </Text>
        </View>
        {riskReport && (
          <RiskBadge riskScore={riskReport.risk_score} size="small" />
        )}
      </Container>
    );
  }

  return (
    <Container
      style={styles.container}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={styles.header}>
        <View style={styles.titleRow}>
          <Text style={styles.name}>{system.name}</Text>
          <View style={[styles.securityBadge, { backgroundColor: security.color }]}>
            <Text style={styles.securityText}>{security.text}</Text>
          </View>
        </View>
        <Text style={styles.category}>{category}</Text>
      </View>

      {riskReport && (
        <View style={styles.riskSection}>
          <Text style={styles.riskLabel}>Risk Assessment</Text>
          <View style={styles.riskRow}>
            <RiskBadge riskScore={riskReport.risk_score} size="large" showLabel />
            <View style={styles.riskDetails}>
              <Text style={styles.riskDetail}>
                Security: {riskReport.security_score.toFixed(1)}
              </Text>
              <Text style={styles.riskDetail}>
                Kills: {riskReport.kill_score.toFixed(1)}
              </Text>
              <Text style={styles.riskDetail}>
                Pods: {riskReport.pod_score.toFixed(1)}
              </Text>
            </View>
          </View>
        </View>
      )}
    </Container>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: THEME.colors.card,
    borderRadius: THEME.borderRadius.lg,
    padding: THEME.spacing.md,
    marginVertical: THEME.spacing.xs,
  },
  compactContainer: {
    backgroundColor: THEME.colors.card,
    borderRadius: THEME.borderRadius.md,
    padding: THEME.spacing.sm,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginVertical: 2,
  },
  compactLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: THEME.spacing.sm,
  },
  compactName: {
    color: THEME.colors.text,
    fontSize: 14,
    fontWeight: '500',
  },
  compactSecurity: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  header: {
    marginBottom: THEME.spacing.sm,
  },
  titleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  name: {
    color: THEME.colors.text,
    fontSize: 18,
    fontWeight: 'bold',
  },
  securityBadge: {
    paddingHorizontal: THEME.spacing.sm,
    paddingVertical: 2,
    borderRadius: THEME.borderRadius.sm,
  },
  securityText: {
    color: '#000',
    fontSize: 12,
    fontWeight: 'bold',
  },
  category: {
    color: THEME.colors.textSecondary,
    fontSize: 12,
    marginTop: 2,
  },
  riskSection: {
    borderTopWidth: 1,
    borderTopColor: THEME.colors.border,
    paddingTop: THEME.spacing.sm,
    marginTop: THEME.spacing.xs,
  },
  riskLabel: {
    color: THEME.colors.textSecondary,
    fontSize: 11,
    textTransform: 'uppercase',
    marginBottom: THEME.spacing.xs,
  },
  riskRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: THEME.spacing.md,
  },
  riskDetails: {
    flex: 1,
  },
  riskDetail: {
    color: THEME.colors.textSecondary,
    fontSize: 12,
  },
});

export default SystemCard;
