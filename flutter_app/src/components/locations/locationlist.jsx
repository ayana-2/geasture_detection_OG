// frontend/src/components/locations/LocationList.jsx
import React, { useState, useEffect } from 'react';
import { useLocations } from '../../context/locationcontext';
import LocationCard from './LocationCard';
import LocationFilters from './LocationFilters';
import LocationMap from './LocationMap';
import './LocationList.css';

const LocationList = () => {
  const {
    locations,
    loading,
    error,
    fetchLocations,
    userLocation,
    searchNearby,
    pagination,
    goToPage
  } = useLocations();

  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'map'
  const [showNearby, setShowNearby] = useState(false);

  useEffect(() => {
    fetchLocations();
  }, []);

  const handleSearchNearby = () => {
    if (userLocation) {
      searchNearby(userLocation.lat, userLocation.lng);
      setShowNearby(true);
    }
  };

  const handleClearNearby = () => {
    fetchLocations();
    setShowNearby(false);
  };

  if (loading) return <div className="loading">Loading locations...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="location-list-container">
      <div className="location-header">
        <h1>Locations</h1>
        <div className="header-actions">
          {userLocation && (
            <button 
              onClick={showNearby ? handleClearNearby : handleSearchNearby}
              className="btn btn-primary"
            >
              {showNearby ? 'Show All Locations' : 'Show Nearby Locations'}
            </button>
          )}
          <div className="view-toggle">
            <button
              className={`btn ${viewMode === 'grid' ? 'btn-active' : ''}`}
              onClick={() => setViewMode('grid')}
            >
              <i className="fas fa-th"></i> Grid
            </button>
            <button
              className={`btn ${viewMode === 'map' ? 'btn-active' : ''}`}
              onClick={() => setViewMode('map')}
            >
              <i className="fas fa-map"></i> Map
            </button>
          </div>
        </div>
      </div>

      <LocationFilters />

      {viewMode === 'map' ? (
        <LocationMap locations={locations} userLocation={userLocation} />
      ) : (
        <>
          <div className="location-grid">
            {locations.length === 0 ? (
              <div className="no-results">
                <p>No locations found. Try adjusting your filters.</p>
              </div>
            ) : (
              locations.map(location => (
                <LocationCard key={location._id} location={location} />
              ))
            )}
          </div>

          {pagination && (
            <div className="pagination">
              {pagination.prev && (
                <button onClick={() => goToPage(pagination.prev.page)}>
                  Previous
                </button>
              )}
              <span>Page {pagination.current || 1}</span>
              {pagination.next && (
                <button onClick={() => goToPage(pagination.next.page)}>
                  Next
                </button>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default LocationList;