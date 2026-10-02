// frontend/src/components/locations/LocationForm.jsx
import React, { useState } from 'react';
import { useLocations } from '../../context/locationcontext';
import './LocationForm.css';

const LocationForm = ({ location, onClose, isEdit = false }) => {
  const { createLocation, updateLocation } = useLocations();
  const [formData, setFormData] = useState({
    name: location?.name || '',
    address: {
      street: location?.address?.street || '',
      city: location?.address?.city || '',
      state: location?.address?.state || '',
      country: location?.address?.country || 'USA',
      postalCode: location?.address?.postalCode || ''
    },
    coordinates: {
      latitude: location?.coordinates?.latitude || '',
      longitude: location?.coordinates?.longitude || ''
    },
    type: location?.type || 'other',
    description: location?.description || '',
    amenities: location?.amenities || [],
    contact: {
      phone: location?.contact?.phone || '',
      email: location?.contact?.email || '',
      website: location?.contact?.website || ''
    }
  });

  const [currentAmenity, setCurrentAmenity] = useState('');
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    
    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const addAmenity = () => {
    if (currentAmenity.trim() && !formData.amenities.includes(currentAmenity.trim())) {
      setFormData(prev => ({
        ...prev,
        amenities: [...prev.amenities, currentAmenity.trim()]
      }));
      setCurrentAmenity('');
    }
  };

  const removeAmenity = (amenity) => {
    setFormData(prev => ({
      ...prev,
      amenities: prev.amenities.filter(a => a !== amenity)
    }));
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) newErrors.name = 'Name is required';
    if (!formData.address.city.trim()) newErrors.city = 'City is required';
    if (!formData.coordinates.latitude || isNaN(formData.coordinates.latitude)) 
      newErrors.latitude = 'Valid latitude is required';
    if (!formData.coordinates.longitude || isNaN(formData.coordinates.longitude)) 
      newErrors.longitude = 'Valid longitude is required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      const locationData = {
        ...formData,
        coordinates: {
          latitude: parseFloat(formData.coordinates.latitude),
          longitude: parseFloat(formData.coordinates.longitude)
        }
      };
      
      if (isEdit) {
        await updateLocation(location._id, locationData);
      } else {
        await createLocation(locationData);
      }
      
      onClose();
    } catch (error) {
      console.error('Error saving location:', error);
    }
  };

  const handleGetCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData(prev => ({
            ...prev,
            coordinates: {
              latitude: position.coords.latitude,
              longitude: position.coords.longitude
            }
          }));
        },
        (error) => {
          console.error('Error getting location:', error);
          alert('Unable to get your current location');
        }
      );
    }
  };

  return (
    <div className="location-form-modal">
      <div className="modal-content">
        <div className="modal-header">
          <h2>{isEdit ? 'Edit Location' : 'Add New Location'}</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="location-form">
          <div className="form-section">
            <h3>Basic Information</h3>
            
            <div className="form-group">
              <label>Location Name *</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Enter location name"
              />
              {errors.name && <span className="error">{errors.name}</span>}
            </div>
            
            <div className="form-group">
              <label>Type</label>
              <select name="type" value={formData.type} onChange={handleChange}>
                <option value="restaurant">Restaurant</option>
                <option value="hotel">Hotel</option>
                <option value="museum">Museum</option>
                <option value="park">Park</option>
                <option value="mall">Mall</option>
                <option value="office">Office</option>
                <option value="residential">Residential</option>
                <option value="other">Other</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Description</label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Describe this location..."
                rows="3"
              />
            </div>
          </div>
          
          <div className="form-section">
            <h3>Address</h3>
            
            <div className="form-group">
              <label>Street</label>
              <input
                type="text"
                name="address.street"
                value={formData.address.street}
                onChange={handleChange}
                placeholder="Street address"
              />
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label>City *</label>
                <input
                  type="text"
                  name="address.city"
                  value={formData.address.city}
                  onChange={handleChange}
                  placeholder="City"
                />
                {errors.city && <span className="error">{errors.city}</span>}
              </div>
              
              <div className="form-group">
                <label>State</label>
                <input
                  type="text"
                  name="address.state"
                  value={formData.address.state}
                  onChange={handleChange}
                  placeholder="State"
                />
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label>Postal Code</label>
                <input
                  type="text"
                  name="address.postalCode"
                  value={formData.address.postalCode}
                  onChange={handleChange}
                  placeholder="Postal code"
                />
              </div>
              
              <div className="form-group">
                <label>Country</label>
                <input
                  type="text"
                  name="address.country"
                  value={formData.address.country}
                  onChange={handleChange}
                />
              </div>
            </div>
          </div>
          
          <div className="form-section">
            <h3>Coordinates</h3>
            <div className="form-row">
              <div className="form-group">
                <label>Latitude *</label>
                <input
                  type="text"
                  name="coordinates.latitude"
                  value={formData.coordinates.latitude}
                  onChange={handleChange}
                  placeholder="e.g., 40.7128"
                />
                {errors.latitude && <span className="error">{errors.latitude}</span>}
              </div>
              
              <div className="form-group">
                <label>Longitude *</label>
                <input
                  type="text"
                  name="coordinates.longitude"
                  value={formData.coordinates.longitude}
                  onChange={handleChange}
                  placeholder="e.g., -74.0060"
                />
                {errors.longitude && <span className="error">{errors.longitude}</span>}
              </div>
            </div>
            
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleGetCurrentLocation}
            >
              <i className="fas fa-location-crosshairs"></i> Use Current Location
            </button>
          </div>
          
          <div className="form-section">
            <h3>Amenities</h3>
            <div className="amenities-input">
              <input
                type="text"
                value={currentAmenity}
                onChange={(e) => setCurrentAmenity(e.target.value)}
                placeholder="Add an amenity"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addAmenity())}
              />
              <button type="button" onClick={addAmenity}>Add</button>
            </div>
            
            <div className="amenities-list">
              {formData.amenities.map((amenity, index) => (
                <span key={index} className="amenity-tag">
                  {amenity}
                  <button type="button" onClick={() => removeAmenity(amenity)}>
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
          
          <div className="form-section">
            <h3>Contact Information</h3>
            
            <div className="form-group">
              <label>Phone</label>
              <input
                type="tel"
                name="contact.phone"
                value={formData.contact.phone}
                onChange={handleChange}
                placeholder="Phone number"
              />
            </div>
            
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                name="contact.email"
                value={formData.contact.email}
                onChange={handleChange}
                placeholder="Email address"
              />
            </div>
            
            <div className="form-group">
              <label>Website</label>
              <input
                type="url"
                name="contact.website"
                value={formData.contact.website}
                onChange={handleChange}
                placeholder="Website URL"
              />
            </div>
          </div>
          
          <div className="form-actions">
            <button type="button" className="btn btn-outline" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              {isEdit ? 'Update Location' : 'Create Location'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LocationForm;