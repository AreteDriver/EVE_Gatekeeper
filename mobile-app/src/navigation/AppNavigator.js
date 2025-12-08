/**
 * App Navigator - Main navigation configuration
 */

import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

import MapScreen from '../screens/MapScreen';
import RouteScreen from '../screens/RouteScreen';
import IntelScreen from '../screens/IntelScreen';
import SettingsScreen from '../screens/SettingsScreen';

const Tab = createBottomTabNavigator();

export default function AppNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Map') {
            iconName = focused ? 'map' : 'map-outline';
          } else if (route.name === 'Route') {
            iconName = focused ? 'navigate' : 'navigate-outline';
          } else if (route.name === 'Intel') {
            iconName = focused ? 'shield' : 'shield-outline';
          } else if (route.name === 'Settings') {
            iconName = focused ? 'settings' : 'settings-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#3366FF',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: {
          backgroundColor: '#1A1E3A',
          borderTopColor: '#2A2E4A',
        },
        headerStyle: {
          backgroundColor: '#1A1E3A',
        },
        headerTintColor: '#FFFFFF',
      })}
    >
      <Tab.Screen name="Map" component={MapScreen} />
      <Tab.Screen name="Route" component={RouteScreen} />
      <Tab.Screen name="Intel" component={IntelScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
}
