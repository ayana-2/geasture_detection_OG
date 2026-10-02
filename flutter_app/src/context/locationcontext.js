// frontend/src/context/LocationContext.js
import React, { createContext, useState, useContext, useEffect } from 'react';
import locationService from '../services/locationservice';

const LocationContext = createContext();

export const useLocations = () => useContext(LocationContext);

export const LocationProvider = ({ children }) => {
  const [locations, setLocations] = useState([]);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    type: '',
    city: '',
    minRating: 0,
    search: '',
    sortBy: 'name',
    sortOrder: 'asc',
    page: 1,
    limit: 10
  });
  const [pagination, setPagination] = useState({});
  const [userLocation, setUserLocation] = useState(null);

  // Get user's current location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude
          });
        },
        (error) => {
          console.error('Error getting location:', error);
          setUserLocation({ lat: 40.7128, lng: -74.0060 }); // Default to NYC
        }
      );
    }
  }, []);

  // Fetch locations
  const fetchLocations = async (customFilters = {}) => {
    try {
      setLoading(true);
      const allFilters = { ...filters, ...customFilters };
      const response = await locationService.getLocations(allFilters);
      
      setLocations(response.data.data);
      setPagination(response.data.pagination);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch locations');
      console.error('Error fetching locations:', err);
    } finally {
      setLoading(false);
    }
  };

  // Create location
  const createLocation = async (locationData) => {
    try {
      const response = await locationService.createLocation(locationData);
      setLocations([...locations, response.data.data]);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create location');
      throw err;
    }
  };

  // Update location
  const updateLocation = async (id, locationData) => {
    try {
      const response = await locationService.updateLocation(id, locationData);
      setLocations(locations.map(loc => 
        loc._id === id ? response.data.data : loc
      ));
      if (currentLocation?._id === id) {
        setCurrentLocation(response.data.data);
      }
      return response.data;
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to update location');
      throw err;
    }
  };

  // Delete location
  const deleteLocation = async (id) => {
    try {
      await locationService.deleteLocation(id);
      setLocations(locations.filter(loc => loc._id !== id));
      if (currentLocation?._id === id) {
        setCurrentLocation(null);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete location');
      throw err;
    }
  };

  // Search nearby locations
  const searchNearby = async (lat, lng, radius = 5000) => {
    try {
      setLoading(true);
      const response = await locationService.searchNearbyLocations(lat, lng, radius);
      setLocations(response.data.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to search nearby');
      console.error('Error searching nearby:', err);
    } finally {
      setLoading(false);
    }
  };

  // Update filters
  const updateFilters = (newFilters) => {
    setFilters({ ...filters, ...newFilters, page: 1 });
    fetchLocations(newFilters);
  };

  // Clear filters
  const clearFilters = () => {
    const defaultFilters = {
      type: '',
      city: '',
      minRating: 0,
      search: '',
      sortBy: 'name',
      sortOrder: 'asc',
      page: 1,
      limit: 10
    };
    setFilters(defaultFilters);
    fetchLocations(defaultFilters);
  };

  // Pagination
  const goToPage = (page) => {
    setFilters({ ...filters, page });
    fetchLocations({ page });
  };

  const value = {
    locations,
    currentLocation,
    loading,
    error,
    filters,
    pagination,
    userLocation,
    setCurrentLocation,
    fetchLocations,
    createLocation,
    updateLocation,
    deleteLocation,
    searchNearby,
    updateFilters,
    clearFilters,
    goToPage
  };

  return (
    <LocationContext.Provider value={value}>
      {children}
    </LocationContext.Provider>
  );
};