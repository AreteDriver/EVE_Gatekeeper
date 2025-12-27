/**
 * EVE Gatekeeper Configuration
 */
import Constants from 'expo-constants';

// Safe environment variable access
const getEnvVar = (key: string, fallback: string = ''): string => {
  const value = Constants.expoConfig?.extra?.[key] || process.env[key] || fallback;
  return value;
};

// API Configuration
export const API_CONFIG = {
  // Gatekeeper FastAPI backend URL
  GATEKEEPER_URL: getEnvVar('GATEKEEPER_URL', 'http://localhost:8000'),

  // ESI (EVE Swagger Interface) API
  ESI_BASE_URL: 'https://esi.evetech.net/latest',

  // zKillboard API
  ZKILLBOARD_URL: 'https://zkillboard.com/api',

  // Request timeout (ms)
  TIMEOUT: 30000,
};

// ESI OAuth Configuration (optional, for authenticated features)
export const ESI_CONFIG = {
  CLIENT_ID: getEnvVar('ESI_CLIENT_ID', ''),
  CALLBACK_URL: getEnvVar('ESI_CALLBACK_URL', 'evegatekeeper://auth'),
  AUTHORIZE_URL: 'https://login.eveonline.com/v2/oauth/authorize',
  TOKEN_URL: 'https://login.eveonline.com/v2/oauth/token',
  SCOPES: [
    'esi-location.read_location.v1',
    'esi-location.read_ship_type.v1',
    'esi-ui.write_waypoint.v1',
  ],
};

// App Theme
export const THEME = {
  colors: {
    primary: '#0a84ff',
    background: '#000000',
    card: '#1c1c1e',
    text: '#ffffff',
    textSecondary: '#8e8e93',
    border: '#38383a',

    // Security status colors
    highSec: '#00ff00',
    lowSec: '#ffaa00',
    nullSec: '#ff0000',
    wormhole: '#9900ff',

    // Risk colors
    riskGreen: '#32d74b',
    riskYellow: '#ffd60a',
    riskOrange: '#ff9f0a',
    riskRed: '#ff453a',
  },

  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  },

  borderRadius: {
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
  },
};

// Routing profiles with display info
export const ROUTE_PROFILES = {
  shortest: {
    label: 'Shortest',
    description: 'Minimum jumps, ignores danger',
    icon: 'flash',
    color: THEME.colors.riskYellow,
  },
  safer: {
    label: 'Safer',
    description: 'Balanced route, avoids high-risk systems',
    icon: 'shield-checkmark',
    color: THEME.colors.riskGreen,
  },
  paranoid: {
    label: 'Paranoid',
    description: 'Maximum safety, longest route',
    icon: 'shield',
    color: THEME.colors.primary,
  },
};

// Validate required config
export const validateConfig = (): { valid: boolean; errors: string[] } => {
  const errors: string[] = [];

  if (!API_CONFIG.GATEKEEPER_URL) {
    errors.push('GATEKEEPER_URL is not configured');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
};
