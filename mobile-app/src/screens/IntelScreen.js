/**
 * Intel Screen - zkillboard integration
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Text,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { Searchbar, Card, Chip, Button } from 'react-native-paper';
import { searchSystems, getZKillboardIntel } from '../services/api';
import { dangerColors, securityColors } from '../utils/theme';

export default function IntelScreen({ route }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedSystemId, setSelectedSystemId] = useState(
    route?.params?.systemId || null
  );
  const [selectedSystemName, setSelectedSystemName] = useState(
    route?.params?.systemName || ''
  );
  const [intel, setIntel] = useState(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (selectedSystemId) {
      loadIntel();
    }
  }, [selectedSystemId]);

  const loadIntel = async () => {
    if (!selectedSystemId) return;

    setLoading(true);
    try {
      const data = await getZKillboardIntel(selectedSystemId, 15);
      setIntel(data);
    } catch (error) {
      console.error('Error loading intel:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadIntel();
    setRefreshing(false);
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }

    try {
      const data = await searchSystems(query, 10);
      setSearchResults(data.results || []);
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  const handleSystemSelect = (system) => {
    setSelectedSystemId(system.system_id);
    setSelectedSystemName(system.name);
    setSearchQuery(system.name);
    setSearchResults([]);
  };

  const formatISK = (value) => {
    if (value >= 1000000000) {
      return `${(value / 1000000000).toFixed(2)}B`;
    } else if (value >= 1000000) {
      return `${(value / 1000000).toFixed(2)}M`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(2)}K`;
    }
    return value.toString();
  };

  const formatTime = (timeString) => {
    if (!timeString) return 'Unknown';
    
    const date = new Date(timeString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) {
      return `${diffMins}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else {
      return `${diffDays}d ago`;
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.searchContainer}>
        <Searchbar
          placeholder="Search system for intel..."
          onChangeText={handleSearch}
          value={searchQuery}
          style={styles.searchbar}
        />
      </View>

      {searchResults.length > 0 && (
        <ScrollView style={styles.resultsContainer}>
          {searchResults.map((system) => (
            <Button
              key={system.system_id}
              mode="text"
              onPress={() => handleSystemSelect(system)}
              style={styles.resultButton}
            >
              {system.name} ({system.security_status.toFixed(1)})
            </Button>
          ))}
        </ScrollView>
      )}

      {loading && !refreshing && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#3366FF" />
        </View>
      )}

      {intel && (
        <ScrollView
          style={styles.intelContainer}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
          }
        >
          <Card style={styles.summaryCard}>
            <Card.Title
              title={selectedSystemName}
              titleStyle={styles.cardTitle}
              subtitle={`Recent Activity`}
              subtitleStyle={styles.cardSubtitle}
            />
            <Card.Content>
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Total Kills:</Text>
                <Text style={styles.summaryValue}>{intel.total_kills}</Text>
              </View>
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Total Value:</Text>
                <Text style={styles.summaryValue}>
                  {formatISK(intel.total_value_destroyed)} ISK
                </Text>
              </View>
              <View style={styles.summaryRow}>
                <Text style={styles.summaryLabel}>Danger Rating:</Text>
                <Chip
                  style={[
                    styles.dangerChip,
                    { backgroundColor: dangerColors[intel.danger_rating] },
                  ]}
                  textStyle={styles.chipText}
                >
                  {intel.danger_rating.toUpperCase()}
                </Chip>
              </View>
            </Card.Content>
          </Card>

          {intel.kills && intel.kills.length > 0 ? (
            intel.kills.map((kill) => (
              <Card key={kill.killmail_id} style={styles.killCard}>
                <Card.Content>
                  <View style={styles.killHeader}>
                    <Text style={styles.killTime}>{formatTime(kill.kill_time)}</Text>
                    <Text style={styles.killValue}>
                      {formatISK(kill.total_value)} ISK
                    </Text>
                  </View>
                  <View style={styles.killDetails}>
                    <Text style={styles.killLabel}>Ship Type ID:</Text>
                    <Text style={styles.killDetailValue}>{kill.victim_ship_type}</Text>
                  </View>
                  <View style={styles.killDetails}>
                    <Text style={styles.killLabel}>Attackers:</Text>
                    <Text style={styles.killDetailValue}>{kill.attacker_count}</Text>
                  </View>
                  {kill.is_solo && (
                    <Chip style={styles.soloChip} textStyle={styles.chipText}>
                      SOLO
                    </Chip>
                  )}
                  {kill.is_npc && (
                    <Chip style={styles.npcChip} textStyle={styles.chipText}>
                      NPC
                    </Chip>
                  )}
                </Card.Content>
              </Card>
            ))
          ) : (
            <Card style={styles.noDataCard}>
              <Card.Content>
                <Text style={styles.noDataText}>
                  No recent kills found in this system
                </Text>
                <Text style={styles.noDataSubtext}>
                  This system appears to be relatively safe
                </Text>
              </Card.Content>
            </Card>
          )}
        </ScrollView>
      )}

      {!selectedSystemId && !loading && (
        <View style={styles.placeholderContainer}>
          <Text style={styles.placeholderText}>
            Select a system to view intel
          </Text>
          <Text style={styles.placeholderSubtext}>
            Search for a system to see zkillboard data
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
  },
  resultsContainer: {
    maxHeight: 200,
    paddingHorizontal: 16,
  },
  resultButton: {
    justifyContent: 'flex-start',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  intelContainer: {
    flex: 1,
    padding: 16,
  },
  summaryCard: {
    backgroundColor: '#1A1E3A',
    marginBottom: 16,
  },
  cardTitle: {
    color: '#FFFFFF',
  },
  cardSubtitle: {
    color: '#AAAAAA',
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  summaryLabel: {
    color: '#AAAAAA',
    fontSize: 14,
  },
  summaryValue: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: 'bold',
  },
  dangerChip: {
    height: 28,
  },
  chipText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  killCard: {
    backgroundColor: '#1A1E3A',
    marginBottom: 12,
  },
  killHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  killTime: {
    color: '#AAAAAA',
    fontSize: 12,
  },
  killValue: {
    color: '#FF9900',
    fontSize: 14,
    fontWeight: 'bold',
  },
  killDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  killLabel: {
    color: '#AAAAAA',
    fontSize: 13,
  },
  killDetailValue: {
    color: '#FFFFFF',
    fontSize: 13,
  },
  soloChip: {
    marginTop: 8,
    backgroundColor: '#00FF00',
    alignSelf: 'flex-start',
  },
  npcChip: {
    marginTop: 8,
    backgroundColor: '#888888',
    alignSelf: 'flex-start',
  },
  noDataCard: {
    backgroundColor: '#1A1E3A',
  },
  noDataText: {
    color: '#FFFFFF',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 8,
  },
  noDataSubtext: {
    color: '#AAAAAA',
    fontSize: 14,
    textAlign: 'center',
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
