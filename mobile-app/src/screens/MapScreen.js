/**
 * Map Screen - Main 2D map visualization
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  Text,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { Searchbar, Card, Chip, Button } from 'react-native-paper';
import { searchSystems, getSystemDetails } from '../services/api';
import { securityColors } from '../utils/theme';

export default function MapScreen({ navigation }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedSystem, setSelectedSystem] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (query) => {
    setSearchQuery(query);
    
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }

    setLoading(true);
    try {
      const data = await searchSystems(query, 10);
      setSearchResults(data.results || []);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSystemSelect = async (system) => {
    setLoading(true);
    try {
      const details = await getSystemDetails(system.system_id);
      setSelectedSystem(details);
      setSearchResults([]);
      setSearchQuery(details.name);
    } catch (error) {
      console.error('Error loading system:', error);
    } finally {
      setLoading(false);
    }
  };

  const navigateToRoute = () => {
    if (selectedSystem) {
      navigation.navigate('Route', { 
        system: selectedSystem 
      });
    }
  };

  const navigateToIntel = () => {
    if (selectedSystem) {
      navigation.navigate('Intel', { 
        systemId: selectedSystem.system_id,
        systemName: selectedSystem.name,
      });
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.searchContainer}>
        <Searchbar
          placeholder="Search systems..."
          onChangeText={handleSearch}
          value={searchQuery}
          style={styles.searchbar}
          iconColor="#3366FF"
          inputStyle={{ color: '#FFFFFF' }}
        />
      </View>

      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#3366FF" />
        </View>
      )}

      {searchResults.length > 0 && (
        <ScrollView style={styles.resultsContainer}>
          {searchResults.map((system) => (
            <TouchableOpacity
              key={system.system_id}
              onPress={() => handleSystemSelect(system)}
            >
              <Card style={styles.resultCard}>
                <Card.Content>
                  <View style={styles.resultRow}>
                    <Text style={styles.systemName}>{system.name}</Text>
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
                </Card.Content>
              </Card>
            </TouchableOpacity>
          ))}
        </ScrollView>
      )}

      {selectedSystem && (
        <View style={styles.systemDetailsContainer}>
          <Card style={styles.detailsCard}>
            <Card.Title
              title={selectedSystem.name}
              titleStyle={styles.systemTitle}
              subtitle={`Region: ${selectedSystem.region_id}`}
              subtitleStyle={styles.systemSubtitle}
            />
            <Card.Content>
              <View style={styles.detailsRow}>
                <Text style={styles.label}>Security:</Text>
                <Chip
                  style={[
                    styles.securityChip,
                    { backgroundColor: securityColors[selectedSystem.security_class] },
                  ]}
                  textStyle={styles.chipText}
                >
                  {selectedSystem.security_status.toFixed(2)} ({selectedSystem.security_class})
                </Chip>
              </View>

              <View style={styles.detailsRow}>
                <Text style={styles.label}>Planets:</Text>
                <Text style={styles.value}>{selectedSystem.planets}</Text>
              </View>

              <View style={styles.detailsRow}>
                <Text style={styles.label}>Stargates:</Text>
                <Text style={styles.value}>{selectedSystem.stargates}</Text>
              </View>

              <View style={styles.detailsRow}>
                <Text style={styles.label}>Connected Systems:</Text>
                <Text style={styles.value}>
                  {selectedSystem.connected_systems?.length || 0}
                </Text>
              </View>
            </Card.Content>
            <Card.Actions>
              <Button
                mode="contained"
                onPress={navigateToRoute}
                style={styles.actionButton}
              >
                Plan Route
              </Button>
              <Button
                mode="outlined"
                onPress={navigateToIntel}
                style={styles.actionButton}
              >
                View Intel
              </Button>
            </Card.Actions>
          </Card>
        </View>
      )}

      {!selectedSystem && !loading && searchResults.length === 0 && (
        <View style={styles.placeholderContainer}>
          <Text style={styles.placeholderText}>
            Search for a system to view details
          </Text>
          <Text style={styles.placeholderSubtext}>
            Use the search bar above to find EVE Online systems
          </Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0E27',
  },
  searchContainer: {
    padding: 16,
  },
  searchbar: {
    backgroundColor: '#1A1E3A',
    borderRadius: 8,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  resultsContainer: {
    flex: 1,
    padding: 16,
  },
  resultCard: {
    backgroundColor: '#1A1E3A',
    marginBottom: 8,
  },
  resultRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  systemName: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  securityChip: {
    height: 28,
  },
  chipText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  systemDetailsContainer: {
    padding: 16,
  },
  detailsCard: {
    backgroundColor: '#1A1E3A',
  },
  systemTitle: {
    color: '#FFFFFF',
    fontSize: 20,
  },
  systemSubtitle: {
    color: '#AAAAAA',
  },
  detailsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  label: {
    color: '#AAAAAA',
    fontSize: 14,
  },
  value: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: 'bold',
  },
  actionButton: {
    marginHorizontal: 4,
  },
  placeholderContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  placeholderText: {
    color: '#FFFFFF',
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 8,
  },
  placeholderSubtext: {
    color: '#AAAAAA',
    fontSize: 14,
    textAlign: 'center',
  },
});
