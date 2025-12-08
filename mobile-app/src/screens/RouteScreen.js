/**
 * Route Planning Screen
 */

import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Text,
  ActivityIndicator,
} from 'react-native';
import {
  Searchbar,
  Card,
  Button,
  Chip,
  Switch,
  TextInput,
} from 'react-native-paper';
import { searchSystems, calculateRoute, calculateFuelCost } from '../services/api';
import { securityColors } from '../utils/theme';

export default function RouteScreen({ route: navigationRoute }) {
  const [origin, setOrigin] = useState(navigationRoute?.params?.system || null);
  const [destination, setDestination] = useState(null);
  const [originQuery, setOriginQuery] = useState('');
  const [destQuery, setDestQuery] = useState('');
  const [originResults, setOriginResults] = useState([]);
  const [destResults, setDestResults] = useState([]);
  const [route, setRoute] = useState(null);
  const [fuelCost, setFuelCost] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Route options
  const [avoidLowSec, setAvoidLowSec] = useState(false);
  const [avoidNullSec, setAvoidNullSec] = useState(true);
  const [shipType, setShipType] = useState('Carrier');

  const handleOriginSearch = async (query) => {
    setOriginQuery(query);
    if (query.length < 2) {
      setOriginResults([]);
      return;
    }

    try {
      const data = await searchSystems(query, 5);
      setOriginResults(data.results || []);
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  const handleDestSearch = async (query) => {
    setDestQuery(query);
    if (query.length < 2) {
      setDestResults([]);
      return;
    }

    try {
      const data = await searchSystems(query, 5);
      setDestResults(data.results || []);
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  const selectOrigin = (system) => {
    setOrigin(system);
    setOriginQuery(system.name);
    setOriginResults([]);
  };

  const selectDestination = (system) => {
    setDestination(system);
    setDestQuery(system.name);
    setDestResults([]);
  };

  const calculateRouteHandler = async () => {
    if (!origin || !destination) {
      return;
    }

    setLoading(true);
    try {
      // Calculate route
      const routeData = await calculateRoute(
        origin.system_id,
        destination.system_id,
        {
          avoid_low_sec: avoidLowSec,
          avoid_null_sec: avoidNullSec,
        }
      );

      setRoute(routeData);

      // Calculate fuel cost
      const systemIds = routeData.route.map(r => r.system_id);
      const fuelData = await calculateFuelCost(systemIds, shipType);
      setFuelCost(fuelData);
    } catch (error) {
      console.error('Route calculation error:', error);
      setRoute(null);
      setFuelCost(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Title title="Origin" titleStyle={styles.cardTitle} />
        <Card.Content>
          <Searchbar
            placeholder="Search origin system..."
            onChangeText={handleOriginSearch}
            value={originQuery}
            style={styles.searchbar}
          />
          {originResults.map((system) => (
            <Button
              key={system.system_id}
              mode="text"
              onPress={() => selectOrigin(system)}
              style={styles.resultButton}
            >
              {system.name} ({system.security_status.toFixed(1)})
            </Button>
          ))}
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Destination" titleStyle={styles.cardTitle} />
        <Card.Content>
          <Searchbar
            placeholder="Search destination system..."
            onChangeText={handleDestSearch}
            value={destQuery}
            style={styles.searchbar}
          />
          {destResults.map((system) => (
            <Button
              key={system.system_id}
              mode="text"
              onPress={() => selectDestination(system)}
              style={styles.resultButton}
            >
              {system.name} ({system.security_status.toFixed(1)})
            </Button>
          ))}
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Title title="Route Options" titleStyle={styles.cardTitle} />
        <Card.Content>
          <View style={styles.optionRow}>
            <Text style={styles.optionLabel}>Avoid Low Sec</Text>
            <Switch value={avoidLowSec} onValueChange={setAvoidLowSec} />
          </View>
          <View style={styles.optionRow}>
            <Text style={styles.optionLabel}>Avoid Null Sec</Text>
            <Switch value={avoidNullSec} onValueChange={setAvoidNullSec} />
          </View>
          <View style={styles.optionRow}>
            <Text style={styles.optionLabel}>Ship Type</Text>
            <TextInput
              value={shipType}
              onChangeText={setShipType}
              style={styles.shipInput}
              mode="outlined"
            />
          </View>
        </Card.Content>
      </Card>

      <Button
        mode="contained"
        onPress={calculateRouteHandler}
        disabled={!origin || !destination || loading}
        style={styles.calculateButton}
        loading={loading}
      >
        Calculate Route
      </Button>

      {route && (
        <Card style={styles.card}>
          <Card.Title
            title={`Route: ${route.origin} → ${route.destination}`}
            titleStyle={styles.cardTitle}
            subtitle={`${route.total_jumps} jumps`}
            subtitleStyle={styles.cardSubtitle}
          />
          <Card.Content>
            <ScrollView style={styles.routeList}>
              {route.route.map((system, index) => (
                <View key={system.system_id} style={styles.routeItem}>
                  <Text style={styles.jumpNumber}>{index + 1}</Text>
                  <Text style={styles.systemNameInRoute}>{system.name}</Text>
                  <Chip
                    style={[
                      styles.securityChip,
                      { backgroundColor: securityColors[system.security_class] },
                    ]}
                    textStyle={styles.chipText}
                  >
                    {system.security_status.toFixed(1)}
                  </Chip>
                </View>
              ))}
            </ScrollView>
          </Card.Content>
        </Card>
      )}

      {fuelCost && (
        <Card style={styles.card}>
          <Card.Title title="Fuel Cost" titleStyle={styles.cardTitle} />
          <Card.Content>
            <View style={styles.fuelRow}>
              <Text style={styles.fuelLabel}>Ship Type:</Text>
              <Text style={styles.fuelValue}>{fuelCost.ship_type}</Text>
            </View>
            <View style={styles.fuelRow}>
              <Text style={styles.fuelLabel}>Total Jumps:</Text>
              <Text style={styles.fuelValue}>{fuelCost.total_jumps}</Text>
            </View>
            <View style={styles.fuelRow}>
              <Text style={styles.fuelLabel}>Fuel per Jump:</Text>
              <Text style={styles.fuelValue}>{fuelCost.fuel_per_jump} units</Text>
            </View>
            <View style={styles.fuelRow}>
              <Text style={styles.fuelLabel}>Total Fuel:</Text>
              <Text style={styles.fuelValue}>{fuelCost.total_fuel} units</Text>
            </View>
            <View style={styles.fuelRow}>
              <Text style={styles.fuelLabel}>Fuel Price:</Text>
              <Text style={styles.fuelValue}>{fuelCost.fuel_price} ISK/unit</Text>
            </View>
            <View style={[styles.fuelRow, styles.totalRow]}>
              <Text style={styles.totalLabel}>Total Cost:</Text>
              <Text style={styles.totalValue}>
                {fuelCost.total_cost.toLocaleString()} ISK
              </Text>
            </View>
          </Card.Content>
        </Card>
      )}
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
  cardSubtitle: {
    color: '#AAAAAA',
  },
  searchbar: {
    backgroundColor: '#2A2E4A',
    marginBottom: 8,
  },
  resultButton: {
    justifyContent: 'flex-start',
  },
  optionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  optionLabel: {
    color: '#FFFFFF',
    fontSize: 16,
  },
  shipInput: {
    width: 150,
    backgroundColor: '#2A2E4A',
  },
  calculateButton: {
    marginBottom: 16,
  },
  routeList: {
    maxHeight: 300,
  },
  routeItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#2A2E4A',
  },
  jumpNumber: {
    color: '#AAAAAA',
    fontSize: 14,
    width: 30,
  },
  systemNameInRoute: {
    color: '#FFFFFF',
    fontSize: 14,
    flex: 1,
  },
  securityChip: {
    height: 24,
  },
  chipText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: 'bold',
  },
  fuelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  fuelLabel: {
    color: '#AAAAAA',
    fontSize: 14,
  },
  fuelValue: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: 'bold',
  },
  totalRow: {
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: '#2A2E4A',
  },
  totalLabel: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  totalValue: {
    color: '#3366FF',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
