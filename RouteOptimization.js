import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Form, Spinner, Alert, ListGroup, Badge } from 'react-bootstrap';
import axios from 'axios';

/**
 * Route Optimization Component
 * Optimizes delivery routes for efficient food distribution
 */
const RouteOptimization = () => {
  const [ngoId, setNgoId] = useState('');
  const [pickupLocations, setPickupLocations] = useState([{ address: '', quantity: '' }]);
  const [deliveryLocations, setDeliveryLocations] = useState([{ address: '', quantity: '' }]);
  const [numVehicles, setNumVehicles] = useState(1);
  const [vehicleCapacity, setVehicleCapacity] = useState(100);
  const [optimizedRoute, setOptimizedRoute] = useState(null);
  const [multiVehicleRoutes, setMultiVehicleRoutes] = useState(null);
  const [consolidationSuggestions, setConsolidationSuggestions] = useState(null);
  const [routeStats, setRouteStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('single');
  const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  const handleAddPickup = () => {
    setPickupLocations([...pickupLocations, { address: '', quantity: '' }]);
  };

  const handleAddDelivery = () => {
    setDeliveryLocations([...deliveryLocations, { address: '', quantity: '' }]);
  };

  const handlePickupChange = (index, field, value) => {
    const updated = [...pickupLocations];
    updated[index][field] = value;
    setPickupLocations(updated);
  };

  const handleDeliveryChange = (index, field, value) => {
    const updated = [...deliveryLocations];
    updated[index][field] = value;
    setDeliveryLocations(updated);
  };

  const handleRemovePickup = (index) => {
    setPickupLocations(pickupLocations.filter((_, i) => i !== index));
  };

  const handleRemoveDelivery = (index) => {
    setDeliveryLocations(deliveryLocations.filter((_, i) => i !== index));
  };

  const handleOptimizeRoute = async (e) => {
    e.preventDefault();

    if (!ngoId) {
      setError('Please enter NGO ID');
      return;
    }

    if (activeTab === 'single' && (!pickupLocations.length || !deliveryLocations.length)) {
      setError('Please add at least one pickup and delivery location');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const payload = {
        ngo_id: ngoId,
        [activeTab === 'single' ? 'pickup_locations' : 'locations']: 
          activeTab === 'single' ? pickupLocations : [...pickupLocations, ...deliveryLocations],
        ...(activeTab === 'multi' && { num_vehicles: numVehicles }),
        vehicle_capacity: vehicleCapacity
      };

      const endpoint = activeTab === 'single' 
        ? '/api/ai/routes/optimize'
        : '/api/ai/routes/optimize-multi';

      const response = await axios.post(`${baseURL}${endpoint}`, payload, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.data.success) {
        if (activeTab === 'single') {
          setOptimizedRoute(response.data);
        } else {
          setMultiVehicleRoutes(response.data);
        }
        fetchConsolidationSuggestions();
        fetchRouteStats();
      } else {
        setError(response.data.error || 'Error optimizing route');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Error optimizing route');
    } finally {
      setLoading(false);
    }
  };

  const fetchConsolidationSuggestions = async () => {
    if (!ngoId) return;

    try {
      const response = await axios.get(
        `${baseURL}/api/ai/routes/consolidation/${ngoId}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      if (response.data.success) {
        setConsolidationSuggestions(response.data);
      }
    } catch (err) {
      console.error('Error fetching consolidation suggestions:', err);
    }
  };

  const fetchRouteStats = async () => {
    if (!ngoId) return;

    try {
      const response = await axios.get(
        `${baseURL}/api/ai/routes/stats/${ngoId}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      if (response.data.success) {
        setRouteStats(response.data);
      }
    } catch (err) {
      console.error('Error fetching route stats:', err);
    }
  };

  // Using route.total_distance_km directly instead of calculating

  return (
    <Container className="route-optimization-container">
      <Row className="mb-4">
        <Col lg={8}>
          <Card className="route-input-card">
            <Card.Header className="bg-primary text-white">
              <h5>🗺️ Route Optimization</h5>
            </Card.Header>
            <Card.Body>
              <Form onSubmit={handleOptimizeRoute}>
                <Row className="mb-3">
                  <Col md={6}>
                    <Form.Group>
                      <Form.Label>NGO ID</Form.Label>
                      <Form.Control
                        type="text"
                        placeholder="Enter NGO ID"
                        value={ngoId}
                        onChange={(e) => setNgoId(e.target.value)}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group>
                      <Form.Label>Vehicle Capacity (Units)</Form.Label>
                      <Form.Control
                        type="number"
                        value={vehicleCapacity}
                        onChange={(e) => setVehicleCapacity(parseInt(e.target.value))}
                        min="1"
                      />
                    </Form.Group>
                  </Col>
                </Row>

                {/* Tab Selection */}
                <div className="btn-group w-100 mb-3" role="group">
                  <input
                    type="radio"
                    className="btn-check"
                    name="routeType"
                    id="singleVehicle"
                    value="single"
                    checked={activeTab === 'single'}
                    onChange={(e) => setActiveTab(e.target.value)}
                  />
                  <label className="btn btn-outline-secondary" htmlFor="singleVehicle">
                    🚗 Single Vehicle
                  </label>

                  <input
                    type="radio"
                    className="btn-check"
                    name="routeType"
                    id="multiVehicle"
                    value="multi"
                    checked={activeTab === 'multi'}
                    onChange={(e) => setActiveTab(e.target.value)}
                  />
                  <label className="btn btn-outline-secondary" htmlFor="multiVehicle">
                    🚗🚗 Multiple Vehicles
                  </label>
                </div>

                {activeTab === 'multi' && (
                  <Form.Group className="mb-3">
                    <Form.Label>Number of Vehicles</Form.Label>
                    <Form.Range
                      min="1"
                      max="10"
                      value={numVehicles}
                      onChange={(e) => setNumVehicles(parseInt(e.target.value))}
                    />
                    <small className="text-muted">Selected: {numVehicles} vehicles</small>
                  </Form.Group>
                )}

                {/* Pickup Locations */}
                <div className="location-section mb-3">
                  <h6>📍 Pickup Locations</h6>
                  {pickupLocations.map((location, index) => (
                    <div key={index} className="location-item mb-2">
                      <Row>
                        <Col md={8}>
                          <Form.Control
                            type="text"
                            placeholder="Pickup address"
                            value={location.address}
                            onChange={(e) => handlePickupChange(index, 'address', e.target.value)}
                            size="sm"
                          />
                        </Col>
                        <Col md={3}>
                          <Form.Control
                            type="number"
                            placeholder="Qty"
                            value={location.quantity}
                            onChange={(e) => handlePickupChange(index, 'quantity', e.target.value)}
                            size="sm"
                            min="0"
                          />
                        </Col>
                        <Col md={1}>
                          {pickupLocations.length > 1 && (
                            <Button
                              variant="danger"
                              size="sm"
                              onClick={() => handleRemovePickup(index)}
                            >
                              ✕
                            </Button>
                          )}
                        </Col>
                      </Row>
                    </div>
                  ))}
                  <Button
                    variant="outline-primary"
                    size="sm"
                    onClick={handleAddPickup}
                    className="w-100"
                  >
                    + Add Pickup Location
                  </Button>
                </div>

                {/* Delivery Locations */}
                <div className="location-section mb-3">
                  <h6>🏠 Delivery Locations</h6>
                  {deliveryLocations.map((location, index) => (
                    <div key={index} className="location-item mb-2">
                      <Row>
                        <Col md={8}>
                          <Form.Control
                            type="text"
                            placeholder="Delivery address"
                            value={location.address}
                            onChange={(e) => handleDeliveryChange(index, 'address', e.target.value)}
                            size="sm"
                          />
                        </Col>
                        <Col md={3}>
                          <Form.Control
                            type="number"
                            placeholder="Qty"
                            value={location.quantity}
                            onChange={(e) => handleDeliveryChange(index, 'quantity', e.target.value)}
                            size="sm"
                            min="0"
                          />
                        </Col>
                        <Col md={1}>
                          {deliveryLocations.length > 1 && (
                            <Button
                              variant="danger"
                              size="sm"
                              onClick={() => handleRemoveDelivery(index)}
                            >
                              ✕
                            </Button>
                          )}
                        </Col>
                      </Row>
                    </div>
                  ))}
                  <Button
                    variant="outline-primary"
                    size="sm"
                    onClick={handleAddDelivery}
                    className="w-100"
                  >
                    + Add Delivery Location
                  </Button>
                </div>

                {error && <Alert variant="danger">{error}</Alert>}

                <Button
                  variant="primary"
                  type="submit"
                  className="w-100"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Spinner size="sm" className="me-2" />
                      Optimizing Route...
                    </>
                  ) : (
                    '🔍 Optimize Route'
                  )}
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={4}>
          {routeStats && (
            <Card className="stats-card">
              <Card.Header className="bg-info text-white">
                <h6>📊 Statistics</h6>
              </Card.Header>
              <Card.Body>
                <div className="stat-item">
                  <span>Completed Deliveries</span>
                  <strong>{routeStats.completed_deliveries}</strong>
                </div>
                <div className="stat-item">
                  <span>Average Distance</span>
                  <strong>{routeStats.average_distance_km?.toFixed(2)} km</strong>
                </div>
                <div className="stat-item">
                  <span>Average Time</span>
                  <strong>{routeStats.average_time_minutes?.toFixed(0)} min</strong>
                </div>
                <div className="stat-item">
                  <span>Avg Stops/Route</span>
                  <strong>{routeStats.average_stops_per_route?.toFixed(1)}</strong>
                </div>
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>

      {/* Single Vehicle Results */}
      {optimizedRoute && activeTab === 'single' && (
        <Row className="mb-4">
          <Col lg={12}>
            <Card className="route-results-card">
              <Card.Header className="bg-success text-white">
                <h5>✓ Optimized Route</h5>
              </Card.Header>
              <Card.Body>
                <Row className="mb-4">
                  <Col md={3}>
                    <div className="metric">
                      <h6>📍 Total Distance</h6>
                      <h3 className="text-primary">{optimizedRoute.total_distance_km} km</h3>
                    </div>
                  </Col>
                  <Col md={3}>
                    <div className="metric">
                      <h6>⏱️ Total Time</h6>
                      <h3 className="text-info">{optimizedRoute.total_time_minutes} min</h3>
                    </div>
                  </Col>
                  <Col md={3}>
                    <div className="metric">
                      <h6>📦 Capacity Used</h6>
                      <h3 className="text-warning">{optimizedRoute.vehicle_capacity_used}%</h3>
                    </div>
                  </Col>
                  <Col md={3}>
                    <div className="metric">
                      <h6>🌍 CO₂ Saved</h6>
                      <h3 className="text-success">{optimizedRoute.co2_saved_kg} kg</h3>
                    </div>
                  </Col>
                </Row>

                <h6 className="mb-3">Route Sequence:</h6>
                <div className="route-steps">
                  {optimizedRoute.optimized_route?.map((stop, index) => (
                    <div key={index} className="route-step">
                      <div className="step-number">{stop.sequence}</div>
                      <div className="step-info">
                        <strong>{stop.location_name}</strong>
                        <small className="text-muted">
                          Distance: {stop.distance_from_previous_km} km | Time: {stop.estimated_time_minutes} min
                        </small>
                      </div>
                      <Badge bg="secondary">{stop.type}</Badge>
                    </div>
                  ))}
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Multi-Vehicle Results */}
      {multiVehicleRoutes && activeTab === 'multi' && (
        <Row className="mb-4">
          <Col lg={12}>
            <Card className="multi-vehicle-card">
              <Card.Header className="bg-success text-white">
                <h5>✓ Multi-Vehicle Routes</h5>
              </Card.Header>
              <Card.Body>
                <Row className="mb-4">
                  <Col md={4}>
                    <div className="metric">
                      <h6>Total Distance</h6>
                      <h3>{multiVehicleRoutes.total_distance_km} km</h3>
                    </div>
                  </Col>
                  <Col md={4}>
                    <div className="metric">
                      <h6>Total Time</h6>
                      <h3>{multiVehicleRoutes.total_time_minutes} min</h3>
                    </div>
                  </Col>
                  <Col md={4}>
                    <div className="metric">
                      <h6>Average Efficiency</h6>
                      <h3>{multiVehicleRoutes.average_efficiency}</h3>
                    </div>
                  </Col>
                </Row>

                {multiVehicleRoutes.routes?.map((route, index) => (
                  <div key={index} className="vehicle-route mb-3">
                    <h6>
                      <Badge bg="primary">{route.vehicle_id}</Badge>
                      <span className="ms-2">{route.distance_km} km | {route.time_minutes} min | {route.stops} stops</span>
                    </h6>
                    <small className="text-muted">
                      Capacity Used: {route.capacity_used}%
                    </small>
                  </div>
                ))}
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Consolidation Suggestions */}
      {consolidationSuggestions && consolidationSuggestions.consolidation_opportunities?.length > 0 && (
        <Row>
          <Col lg={12}>
            <Card className="consolidation-card">
              <Card.Header className="bg-warning text-dark">
                <h5>💡 Consolidation Opportunities</h5>
              </Card.Header>
              <Card.Body>
                <p className="text-muted">
                  Total Savings: <strong>{consolidationSuggestions.total_distance_savings_km} km</strong> | 
                  <strong className="ms-2">{consolidationSuggestions.total_co2_savings_kg} kg CO₂</strong>
                </p>

                <ListGroup>
                  {consolidationSuggestions.consolidation_opportunities?.map((opp, index) => (
                    <ListGroup.Item key={index}>
                      <div className="d-flex justify-content-between align-items-start">
                        <div>
                          <h6>{opp.location}</h6>
                          <small className="text-muted">
                            Consolidate {opp.consolidation_count} deliveries
                          </small>
                        </div>
                        <div className="text-end">
                          <div className="saving">
                            <span className="badge bg-success">{opp.trips_saved} trips saved</span>
                          </div>
                          <small className="text-muted">
                            {opp.distance_saved_km} km | {opp.co2_saved_kg?.toFixed(2)} kg CO₂
                          </small>
                        </div>
                      </div>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}
    </Container>
  );
};

export default RouteOptimization;
