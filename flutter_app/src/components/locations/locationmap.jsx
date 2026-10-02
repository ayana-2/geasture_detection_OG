// frontend/src/components/locations/LocationMap.jsx
import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './LocationMap.css';

// Fix for default markers in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const LocationMap = ({ locations, userLocation }) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef([]);

  useEffect(() => {
    // Initialize map
    if (!mapInstanceRef.current && mapRef.current) {
      const center = userLocation 
        ? [userLocation.lat, userLocation.lng]
        : locations.length > 0
        ? [locations[0].coordinates.latitude, locations[0].coordinates.longitude]
        : [40.7128, -74.0060]; // Default to NYC

      mapInstanceRef.current = L.map(mapRef.current).setView(center, 13);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(mapInstanceRef.current);

      // Add user location marker if available
      if (userLocation) {
        const userIcon = L.divIcon({
          html: '<div class="user-marker"><i class="fas fa-user"></i></div>',
          className: 'user-location-marker',
          iconSize: [30, 30]
        });

        L.marker([userLocation.lat, userLocation.lng], {
          icon: userIcon,
          zIndexOffset: 1000
        }).addTo(mapInstanceRef.current)
          .bindPopup('Your Location');
      }
    }

    // Clear existing markers
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    // Add markers for locations
    locations.forEach(location => {
      const { latitude, longitude } = location.coordinates;
      
      // Custom marker based on location type
      let iconColor;
      switch(location.type) {
        case 'restaurant': iconColor = '#e53935'; break;
        case 'hotel': iconColor = '#3949ab'; break;
        case 'museum': iconColor = '#43a047'; break;
        case 'park': iconColor = '#2e7d32'; break;
        default: iconColor = '#757575';
      }

      const customIcon = L.divIcon({
        html: `<div style="background-color: ${iconColor}" class="custom-marker">
                <i class="fas fa-${getIconForType(location.type)}"></i>
              </div>`,
        className: 'custom-div-icon',
        iconSize: [30, 30],
        iconAnchor: [15, 30]
      });

      const marker = L.marker([latitude, longitude], { icon: customIcon })
        .addTo(mapInstanceRef.current)
        .bindPopup(`
          <div class="map-popup">
            <h4>${location.name}</h4>
            <p>${location.address.city}, ${location.address.state}</p>
            <p><small>${location.type}</small></p>
            ${location.rating ? `<p>⭐ ${location.rating}/5</p>` : ''}
            <a href="/locations/${location._id}">View Details</a>
          </div>
        `);

      markersRef.current.push(marker);
    });

    // Fit bounds to show all markers
    if (locations.length > 0 && mapInstanceRef.current) {
      const group = L.featureGroup(markersRef.current);
      mapInstanceRef.current.fitBounds(group.getBounds().pad(0.1));
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [locations, userLocation]);

  const getIconForType = (type) => {
    const icons = {
      restaurant: 'utensils',
      hotel: 'bed',
      museum: 'landmark',
      park: 'tree',
      mall: 'shopping-bag',
      office: 'building',
      residential: 'home',
      other: 'map-marker-alt'
    };
    return icons[type] || 'map-marker-alt';
  };

  return (
    <div className="location-map-container">
      <div ref={mapRef} className="location-map"></div>
      <div className="map-legend">
        <h4>Legend</h4>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#e53935' }}></span>
          <span>Restaurant</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#3949ab' }}></span>
          <span>Hotel</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#43a047' }}></span>
          <span>Museum</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#2e7d32' }}></span>
          <span>Park</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#757575' }}></span>
          <span>Other</span>
        </div>
        {userLocation && (
          <div className="legend-item">
            <span className="legend-user"><i className="fas fa-user"></i></span>
            <span>Your Location</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default LocationMap;