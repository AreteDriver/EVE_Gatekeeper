/**
 * Risk Badge Component
 * Displays risk score with color indicator
 */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { formatRiskScore } from '../utils/formatting';
import { THEME } from '../config';

interface RiskBadgeProps {
  riskScore: number;
  size?: 'small' | 'medium' | 'large';
  showLabel?: boolean;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  riskScore,
  size = 'medium',
  showLabel = false,
}) => {
  const { text, color, label } = formatRiskScore(riskScore);

  const sizeStyles = {
    small: { badge: styles.badgeSmall, text: styles.textSmall },
    medium: { badge: styles.badgeMedium, text: styles.textMedium },
    large: { badge: styles.badgeLarge, text: styles.textLarge },
  };

  return (
    <View style={styles.container}>
      <View style={[styles.badge, sizeStyles[size].badge, { backgroundColor: color }]}>
        <Text style={[styles.text, sizeStyles[size].text]}>{text}</Text>
      </View>
      {showLabel && <Text style={[styles.label, { color }]}>{label}</Text>}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
  },
  badge: {
    borderRadius: THEME.borderRadius.md,
    justifyContent: 'center',
    alignItems: 'center',
  },
  badgeSmall: {
    paddingHorizontal: THEME.spacing.xs,
    paddingVertical: 2,
    minWidth: 28,
  },
  badgeMedium: {
    paddingHorizontal: THEME.spacing.sm,
    paddingVertical: THEME.spacing.xs,
    minWidth: 36,
  },
  badgeLarge: {
    paddingHorizontal: THEME.spacing.md,
    paddingVertical: THEME.spacing.sm,
    minWidth: 48,
  },
  text: {
    color: '#000',
    fontWeight: 'bold',
  },
  textSmall: {
    fontSize: 10,
  },
  textMedium: {
    fontSize: 12,
  },
  textLarge: {
    fontSize: 16,
  },
  label: {
    fontSize: 10,
    marginTop: 2,
    fontWeight: '500',
  },
});

export default RiskBadge;
