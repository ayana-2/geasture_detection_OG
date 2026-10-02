// frontend/src/services/locationService.js
import axios from 'axios';
import api from './api';

const API_URL = '/api/locations';

class LocationService {
  // Get all locations with filters
  getLocations(params = {}) {
    return api.get(API_URL, { params });
  }

  // Get single location
  getLocation(id) {
    return api.get(`${API_URL}/${id}`);
  }

  // Create location
  createLocation(locationData) {
    return api.post(API_URL, locationData);
  }

  // Update location
  updateLocation(id, locationData) {
    return api.put(`${API_URL}/${id}`, locationData);
  }

  // Delete location
  deleteLocation(id) {
    return api.delete(`${API_URL}/${id}`);
  }

  // Get locations within radius
  getLocationsInRadius(zipcode, distance, coordinates) {
    return api.get(`${API_URL}/radius/${zipcode}/${distance}`, {
      params: coordinates
    });
  }

  // Upload location photo
  uploadLocationPhoto(id, photoFile) {
    const formData = new FormData();
    formData.append('file', photoFile);
    
    return api.put(`${API_URL}/${id}/photo`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }

  // Search locations by coordinates
  searchNearbyLocations(lat, lng, radius = 5000) {
    return api.get(API_URL, {
      params: {
        coordinates: `${lng},${lat}`,
        radius
      }
    });
  }
}

export default new LocationService();