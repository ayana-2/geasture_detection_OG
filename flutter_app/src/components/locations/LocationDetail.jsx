// frontend/src/components/locations/LocationDetail.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useLocations } from '../../context/locationcontext';
import './LocationDetail.css';

const LocationDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { currentLocation, setCurrentLocation, deleteLocation } = useLocations();
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isOpenNow, setIsOpenNow] = useState(false);

  useEffect(() => {
    // Fetch location details here or get from context
  }, [id]);

  useEffect(() => {
    if (currentLocation?.openingHours) {
      // Check if location is open now
      const checkIfOpen = () => {
        const now = new Date();
        const day = now.toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase();
        const hours = currentLocation.openingHours[day];
        
        if (!hours || !hours.open || !hours.close) {
          setIsOpenNow(false);
          return;
        }
        
        const currentTime = now.getHours() * 100 + now.getMinutes();
        const openTime = parseInt(hours.open.replace(':', ''));
        const closeTime = parseInt(hours.close.replace(':', ''));
        
        setIsOpenNow(currentTime >= openTime && currentTime <= closeTime);
      };
      
      checkIfOpen();
      const interval = setInterval(checkIfOpen, 60000); // Check every minute
      
      return () => clearInterval(interval);
    }
  }, [currentLocation]);

  if (!currentLocation) {
    return <div>Loading...</div>;
  }

  const handleEdit = () => {
    navigate(`/locations/${id}/edit`);
  };

  const handleDelete = async () => {
    try {
      await deleteLocation(id);
      navigate('/locations');
    } catch (error) {
      console.error('Error deleting location:', error);
    }
  };

  const openInMaps = () => {
    const { latitude, longitude } = currentLocation.coordinates;
    window.open(`https://www.google.com/maps?q=${latitude},${longitude}`, '_blank');
  };

  const openDirections = () => {
    const { latitude, longitude } = currentLocation.coordinates;
    window.open(`https://www.google.com/maps/dir/?api=1&destination=${latitude},${longitude}`, '_blank');
  };

  return (
    <div className="location-detail">
      {/* Header with image gallery */}
      <div className="location-header">
        <div className="location-images">
          {currentLocation.images && currentLocation.images.length > 0 ? (
            <img 
              src={`/uploads/${currentLocation.images[0]}`} 
              alt={currentLocation.name}
              className="main-image"
            />
          ) : (
            <div className="image-placeholder">
              <i className="fas fa-map-marker-alt"></i>
            </div>
          )}
        </div>
        
        <div className="location-header-info">
          <div className="location-title">
            <h1>{currentLocation.name}</h1>
            <div className="location-actions">
              <button className="btn btn-outline" onClick={handleEdit}>
                <i className="fas fa-edit"></i> Edit
              </button>
              <button 
                className="btn btn-danger" 
                onClick={() => setShowDeleteModal(true)}
              >
                <i className="fas fa-trash"></i> Delete
              </button>
            </div>
          </div>
          
          <div className="location-meta">
            <span className="location-type">{currentLocation.type}</span>
            <span className={`status-badge ${isOpenNow ? 'open' : 'closed'}`}>
              <i className={`fas fa-circle ${isOpenNow ? 'open' : 'closed'}`}></i>
              {isOpenNow ? 'Open Now' : 'Closed'}
            </span>
            <span className="rating">
              <i className="fas fa-star"></i> {currentLocation.rating || 'N/A'}
            </span>
          </div>
          
          <p className="location-description">{currentLocation.description}</p>
        </div>
      </div>
      
      <div className="location-content">
        <div className="content-left">
          {/* Address and Contact */}
          <div className="info-section">
            <h3><i className="fas fa-map-marker-alt"></i> Address</h3>
            <p className="address">
              {currentLocation.address.street}<br />
              {currentLocation.address.city}, {currentLocation.address.state} {currentLocation.address.postalCode}<br />
              {currentLocation.address.country}
            </p>
            <div className="map-actions">
              <button className="btn btn-outline" onClick={openInMaps}>
                <i className="fas fa-map"></i> View on Map
              </button>
              <button className="btn btn-primary" onClick={openDirections}>
                <i className="fas fa-directions"></i> Get Directions
              </button>
            </div>
          </div>
          
          {/* Contact Information */}
          <div className="info-section">
            <h3><i className="fas fa-phone-alt"></i> Contact</h3>
            {currentLocation.contact?.phone && (
              <p><i className="fas fa-phone"></i> {currentLocation.contact.phone}</p>
            )}
            {currentLocation.contact?.email && (
              <p><i className="fas fa-envelope"></i> {currentLocation.contact.email}</p>
            )}
            {currentLocation.contact?.website && (
              <p>
                <i className="fas fa-globe"></i> 
                <a href={currentLocation.contact.website} target="_blank" rel="noopener noreferrer">
                  {currentLocation.contact.website}
                </a>
              </p>
            )}
          </div>
          
          {/* Opening Hours */}
          <div className="info-section">
            <h3><i className="fas fa-clock"></i> Opening Hours</h3>
            <div className="opening-hours">
              {Object.entries(currentLocation.openingHours || {}).map(([day, hours]) => (
                <div key={day} className={`hour-row ${day === new Date().toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase() ? 'today' : ''}`}>
                  <span className="day">{day.charAt(0).toUpperCase() + day.slice(1)}</span>
                  <span className="hours">
                    {hours.open && hours.close ? `${hours.open} - ${hours.close}` : 'Closed'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        <div className="content-right">
          {/* Amenities */}
          <div className="info-section">
            <h3><i className="fas fa-star"></i> Amenities</h3>
            <div className="amenities-grid">
              {currentLocation.amenities?.map((amenity, index) => (
                <div key={index} className="amenity-item">
                  <i className="fas fa-check"></i> {amenity}
                </div>
              ))}
            </div>
          </div>
          
          {/* Coordinates */}
          <div className="info-section">
            <h3><i className="fas fa-location-dot"></i> Coordinates</h3>
            <p>Latitude: {currentLocation.coordinates.latitude}</p>
            <p>Longitude: {currentLocation.coordinates.longitude}</p>
          </div>
          
          {/* Additional Info */}
          <div className="info-section">
            <h3><i className="fas fa-info-circle"></i> Additional Information</h3>
            <p>Created: {new Date(currentLocation.createdAt).toLocaleDateString()}</p>
            <p>Last Updated: {new Date(currentLocation.updatedAt).toLocaleDateString()}</p>
          </div>
        </div>
      </div>
      
      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Delete Location</h3>
            <p>Are you sure you want to delete "{currentLocation.name}"? This action cannot be undone.</p>
            <div className="modal-actions">
              <button 
                className="btn btn-outline" 
                onClick={() => setShowDeleteModal(false)}
              >
                Cancel
              </button>
              <button 
                className="btn btn-danger" 
                onClick={handleDelete}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LocationDetail;