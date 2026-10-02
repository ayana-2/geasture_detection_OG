// backend/services/geocodingService.js
const axios = require('axios');

class GeocodingService {
  constructor() {
    this.nominatimUrl = 'https://nominatim.openstreetmap.org/search';
  }

  async geocodeAddress(address) {
    try {
      const response = await axios.get(this.nominatimUrl, {
        params: {
          q: address,
          format: 'json',
          limit: 1
        },
        headers: {
          'User-Agent': 'YourApp/1.0'
        }
      });

      if (response.data && response.data.length > 0) {
        const result = response.data[0];
        return {
          latitude: parseFloat(result.lat),
          longitude: parseFloat(result.lon),
          address: result.display_name
        };
      }
      return null;
    } catch (error) {
      console.error('Geocoding error:', error);
      return null;
    }
  }

  async reverseGeocode(lat, lon) {
    try {
      const response = await axios.get('https://nominatim.openstreetmap.org/reverse', {
        params: {
          lat,
          lon,
          format: 'json'
        },
        headers: {
          'User-Agent': 'YourApp/1.0'
        }
      });

      if (response.data) {
        return {
          address: response.data.display_name,
          components: response.data.address
        };
      }
      return null;
    } catch (error) {
      console.error('Reverse geocoding error:', error);
      return null;
    }
  }
}

module.exports = new GeocodingService();