/**
 * Settings Screen
 */

import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Text,
} from 'react-native';
import {
  Card,
  Switch,
  Button,
  TextInput,
  List,
} from 'react-native-paper';

export default function SettingsScreen() {
  const [apiUrl, setApiUrl] = useState('http://localhost:5000/api');
  const [darkMode, setDarkMode] = useState(true);
  const [notifications, setNotifications] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [defaultShipType, setDefaultShipType] = useState('Carrier');
  const [fuelPrice, setFuelPrice] = useState('500');

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Title title="API Configuration" titleStyle={styles.cardTitle} />
        <Card.Content>
          <TextInput
            label="API Base URL"
            value={apiUrl}
            onChangeText={setApiUrl}
            style={styles.input}
            mode="outlined"
          />
          <Text style={styles.helpText}>
            Configure the backend API endpoint
          </Text>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Route Settings" titleStyle={styles.cardTitle} />
        <Card.Content>
          <TextInput
            label="Default Ship Type"
            value={defaultShipType}
            onChangeText={setDefaultShipType}
            style={styles.input}
            mode="outlined"
          />
          <TextInput
            label="Default Fuel Price (ISK)"
            value={fuelPrice}
            onChangeText={setFuelPrice}
            keyboardType="numeric"
            style={styles.input}
            mode="outlined"
          />
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="App Preferences" titleStyle={styles.cardTitle} />
        <Card.Content>
          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>Dark Mode</Text>
            <Switch value={darkMode} onValueChange={setDarkMode} />
          </View>
          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>Notifications</Text>
            <Switch value={notifications} onValueChange={setNotifications} />
          </View>
          <View style={styles.settingRow}>
            <Text style={styles.settingLabel}>Auto-refresh Intel</Text>
            <Switch value={autoRefresh} onValueChange={setAutoRefresh} />
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="About" titleStyle={styles.cardTitle} />
        <Card.Content>
          <List.Item
            title="Version"
            description="0.1.0"
            titleStyle={styles.listTitle}
            descriptionStyle={styles.listDescription}
          />
          <List.Item
            title="Developer"
            description="EVE Map Team"
            titleStyle={styles.listTitle}
            descriptionStyle={styles.listDescription}
          />
          <List.Item
            title="Data Source"
            description="EVE ESI API & zkillboard"
            titleStyle={styles.listTitle}
            descriptionStyle={styles.listDescription}
          />
        </Card.Content>
      </Card>

      <View style={styles.actionContainer}>
        <Button
          mode="contained"
          onPress={() => console.log('Settings saved')}
          style={styles.saveButton}
        >
          Save Settings
        </Button>
        <Button
          mode="outlined"
          onPress={() => console.log('Cache cleared')}
          style={styles.clearButton}
        >
          Clear Cache
        </Button>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0E27',
    padding: 16,
  },
  card: {
    backgroundColor: '#1A1E3A',
    marginBottom: 16,
  },
  cardTitle: {
    color: '#FFFFFF',
  },
  input: {
    backgroundColor: '#2A2E4A',
    marginBottom: 8,
  },
  helpText: {
    color: '#AAAAAA',
    fontSize: 12,
    marginTop: 4,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  settingLabel: {
    color: '#FFFFFF',
    fontSize: 16,
  },
  listTitle: {
    color: '#FFFFFF',
  },
  listDescription: {
    color: '#AAAAAA',
  },
  actionContainer: {
    marginVertical: 16,
  },
  saveButton: {
    marginBottom: 8,
  },
  clearButton: {
    marginBottom: 16,
  },
});
