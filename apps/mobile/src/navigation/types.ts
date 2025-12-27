/**
 * Navigation Types
 */

export type RootStackParamList = {
  Home: undefined;
  Route: { profile?: 'shortest' | 'safer' | 'paranoid' } | undefined;
  Settings: undefined;
};
