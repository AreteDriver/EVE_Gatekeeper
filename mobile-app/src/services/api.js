/**
 * API Service - Handles all API calls to the backend
 */

import axios from 'axios';

// Update this URL to match your backend API
const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Search systems by name
 */
export const searchSystems = async (query, limit = 10) => {
  try {
    const response = await api.get('/search', {
      params: { q: query, limit },
    });
    return response.data;
  } catch (error) {
    console.error('Error searching systems:', error);
    throw error;
  }
};

/**
 * Get system details
 */
export const getSystemDetails = async (systemId) => {
  try {
    const response = await api.get(`/systems/${systemId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching system details:', error);
    throw error;
  }
};

/**
 * Get systems with filters
 */
export const getSystems = async (filters = {}) => {
  try {
    const response = await api.get('/systems', { params: filters });
    return response.data;
  } catch (error) {
    console.error('Error fetching systems:', error);
    throw error;
  }
};

/**
 * Calculate route between systems
 */
export const calculateRoute = async (originId, destinationId, options = {}) => {
  try {
    const response = await api.post('/route', {
      origin_id: originId,
      destination_id: destinationId,
      ...options,
    });
    return response.data;
  } catch (error) {
    console.error('Error calculating route:', error);
    throw error;
  }
};

/**
 * Calculate fuel cost for route
 */
export const calculateFuelCost = async (route, shipType = 'Carrier', fuelPrice = 500) => {
  try {
    const response = await api.post('/route/fuel-cost', {
      route,
      ship_type: shipType,
      fuel_price: fuelPrice,
    });
    return response.data;
  } catch (error) {
    console.error('Error calculating fuel cost:', error);
    throw error;
  }
};

/**
 * Get zkillboard intel for a system
 */
export const getZKillboardIntel = async (systemId, limit = 10) => {
  try {
    const response = await api.get(`/intel/zkillboard/${systemId}`, {
      params: { limit },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching zkillboard intel:', error);
    throw error;
  }
};

/**
 * Get map statistics
 */
export const getMapStats = async () => {
  try {
    const response = await api.get('/stats');
    return response.data;
  } catch (error) {
    console.error('Error fetching map stats:', error);
    throw error;
  }
};

/**
 * Health check
 */
export const healthCheck = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Error checking health:', error);
    throw error;
  }
};

export default api;
