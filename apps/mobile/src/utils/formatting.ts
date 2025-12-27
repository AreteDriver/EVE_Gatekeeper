/**
 * Formatting utilities for EVE Gatekeeper
 */
import { THEME } from '../config';

/**
 * Format security status with color
 */
export const formatSecurityStatus = (
  security: number
): { text: string; color: string } => {
  const rounded = Math.round(security * 10) / 10;
  let color: string;

  if (security >= 0.5) {
    color = THEME.colors.highSec;
  } else if (security > 0.0) {
    color = THEME.colors.lowSec;
  } else {
    color = THEME.colors.nullSec;
  }

  return {
    text: rounded.toFixed(1),
    color,
  };
};

/**
 * Get security category label
 */
export const getSecurityCategory = (
  security: number
): 'High-Sec' | 'Low-Sec' | 'Null-Sec' => {
  if (security >= 0.5) return 'High-Sec';
  if (security > 0.0) return 'Low-Sec';
  return 'Null-Sec';
};

/**
 * Format risk score with color
 */
export const formatRiskScore = (
  riskScore: number
): { text: string; color: string; label: string } => {
  let color: string;
  let label: string;

  if (riskScore < 25) {
    color = THEME.colors.riskGreen;
    label = 'Safe';
  } else if (riskScore < 50) {
    color = THEME.colors.riskYellow;
    label = 'Caution';
  } else if (riskScore < 75) {
    color = THEME.colors.riskOrange;
    label = 'Dangerous';
  } else {
    color = THEME.colors.riskRed;
    label = 'Deadly';
  }

  return {
    text: Math.round(riskScore).toString(),
    color,
    label,
  };
};

/**
 * Format distance in light years
 */
export const formatDistance = (distance: number): string => {
  if (distance < 1) {
    return `${(distance * 1000).toFixed(0)} km`;
  }
  return `${distance.toFixed(2)} LY`;
};

/**
 * Format number with commas
 */
export const formatNumber = (value: number): string => {
  return value.toLocaleString();
};

/**
 * Format jump count
 */
export const formatJumps = (jumps: number): string => {
  if (jumps === 1) return '1 jump';
  return `${jumps} jumps`;
};

/**
 * Format fuel amount with units
 */
export const formatFuel = (amount: number, fuelType?: string): string => {
  const formatted = formatNumber(Math.ceil(amount));
  if (fuelType) {
    return `${formatted} ${fuelType}`;
  }
  return `${formatted} isotopes`;
};

/**
 * Truncate text with ellipsis
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - 3) + '...';
};

/**
 * Get time estimate for route (rough estimate based on jumps)
 */
export const estimateRouteTime = (jumps: number): string => {
  // Assume ~30 seconds per jump average (warp + align + gate)
  const totalSeconds = jumps * 30;

  if (totalSeconds < 60) {
    return `~${totalSeconds}s`;
  }

  const minutes = Math.ceil(totalSeconds / 60);
  if (minutes < 60) {
    return `~${minutes} min`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `~${hours}h ${remainingMinutes}m`;
};

/**
 * Get risk color from risk color name
 */
export const getRiskColor = (riskColor: string): string => {
  switch (riskColor) {
    case 'green':
      return THEME.colors.riskGreen;
    case 'yellow':
      return THEME.colors.riskYellow;
    case 'orange':
      return THEME.colors.riskOrange;
    case 'red':
      return THEME.colors.riskRed;
    default:
      return THEME.colors.textSecondary;
  }
};
