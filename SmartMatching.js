import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Form, Spinner, Alert, ListGroup } from 'react-bootstrap';
import axios from 'axios';

/**
 * Smart Donor-NGO Matching Component
 * Intelligently matches donors with suitable NGOs based on multiple factors
 */
const SmartMatching = () => {
  const [matchType, setMatchType] = useState('donor-to-ngo'); // donor-to-ngo or ngo-to-donor
  const [entityId, setEntityId] = useState('');
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [stats, setStats] = useState(null);
  const [topK, setTopK] = useState(5);
  const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  // Get matching stats on component load
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${baseURL}/api/ai/matching/stats`);
        if (response.data.success) {
          setStats(response.data);
        }
      } catch (err) {
        console.error('Error fetching stats:', err);
      }
    };
    fetchStats();
  }, [baseURL]);

  const handleFindMatches = async (e) => {
    e.preventDefault();
    
    if (!entityId) {
      setError('Please enter an ID');
      return;
    }

    setLoading(true);
    setError('');
    setMatches([]);

    try {
      const endpoint = matchType === 'donor-to-ngo' 
        ? `/api/ai/matching/find-ngos/${entityId}?top_k=${topK}`
        : `/api/ai/matching/find-donations/${entityId}`;

      const response = await axios.get(`${baseURL}${endpoint}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.data.success) {
        setMatches(response.data.matches || []);
      } else {
        setError(response.data.error || 'No matches found');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Error finding matches');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#4CAF50'; // Green
    if (score >= 60) return '#FFC107'; // Yellow
    if (score >= 40) return '#FF9800'; // Orange
    return '#F44336'; // Red
  };

  return (
    <Container className="smart-matching-container">
      <Row className="mb-4">
        <Col lg={8}>
          <Card className="matching-card">
            <Card.Header className="bg-primary text-white">
              <h5>🔗 Smart Donor-NGO Matching</h5>
            </Card.Header>
            <Card.Body>
              <Form onSubmit={handleFindMatches}>
                <Form.Group className="mb-3">
                  <Form.Label>Match Type</Form.Label>
                  <div className="btn-group w-100" role="group">
                    <input
                      type="radio"
                      className="btn-check"
                      name="matchType"
                      id="donorToNgo"
                      value="donor-to-ngo"
                      checked={matchType === 'donor-to-ngo'}
                      onChange={(e) => setMatchType(e.target.value)}
                    />
                    <label className="btn btn-outline-primary" htmlFor="donorToNgo">
                      👤 Donor → NGO
                    </label>

                    <input
                      type="radio"
                      className="btn-check"
                      name="matchType"
                      id="ngoToDonor"
                      value="ngo-to-donor"
                      checked={matchType === 'ngo-to-donor'}
                      onChange={(e) => setMatchType(e.target.value)}
                    />
                    <label className="btn btn-outline-primary" htmlFor="ngoToDonor">
                      🏢 NGO → Donations
                    </label>
                  </div>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>
                    {matchType === 'donor-to-ngo' ? 'Donation ID' : 'NGO ID'}
                  </Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Enter ID"
                    value={entityId}
                    onChange={(e) => setEntityId(e.target.value)}
                  />
                </Form.Group>

                {matchType === 'donor-to-ngo' && (
                  <Form.Group className="mb-3">
                    <Form.Label>Number of Matches (Top K)</Form.Label>
                    <Form.Range
                      min="1"
                      max="10"
                      value={topK}
                      onChange={(e) => setTopK(parseInt(e.target.value))}
                    />
                    <small className="text-muted">Selected: {topK}</small>
                  </Form.Group>
                )}

                <Button 
                  variant="primary" 
                  type="submit" 
                  className="w-100"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Spinner size="sm" className="me-2" />
                      Finding Matches...
                    </>
                  ) : (
                    '🔍 Find Matches'
                  )}
                </Button>
              </Form>

              {error && <Alert variant="danger" className="mt-3">{error}</Alert>}
            </Card.Body>
          </Card>
        </Col>

        <Col lg={4}>
          <Card className="stats-card">
            <Card.Header className="bg-info text-white">
              <h6>📊 System Stats</h6>
            </Card.Header>
            <Card.Body>
              {stats ? (
                <>
                  <div className="stat-item">
                    <span>Total Donations</span>
                    <strong>{stats.total_donations}</strong>
                  </div>
                  <div className="stat-item">
                    <span>Successfully Matched</span>
                    <strong className="text-success">{stats.matched_donations}</strong>
                  </div>
                  <div className="stat-item">
                    <span>Success Rate</span>
                    <strong className="text-primary">{stats.success_rate?.toFixed(1)}%</strong>
                  </div>
                  <div className="stat-item">
                    <span>Avg Match Time</span>
                    <strong>{stats.avg_match_time_hours?.toFixed(1)} hrs</strong>
                  </div>
                </>
              ) : (
                <Spinner size="sm" />
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {matches.length > 0 && (
        <Row>
          <Col lg={12}>
            <Card className="matches-card">
              <Card.Header className="bg-success text-white">
                <h5>
                  {matchType === 'donor-to-ngo' ? '🏢 Matching NGOs' : '📦 Matching Donations'}
                </h5>
              </Card.Header>
              <Card.Body>
                <div className="matches-list">
                  {matches.map((match, index) => (
                    <div key={index} className="match-item">
                      <div className="match-header">
                        <h6>
                          {matchType === 'donor-to-ngo' ? match.ngo_name : match.donor_name}
                        </h6>
                        <div className="match-score">
                          <div className="score-bar">
                            <div 
                              className="score-fill" 
                              style={{
                                width: `${match.score}%`,
                                backgroundColor: getScoreColor(match.score)
                              }}
                            />
                          </div>
                          <span className="score-text">{match.score}%</span>
                        </div>
                      </div>

                      <ListGroup variant="flush" className="match-details">
                        {matchType === 'donor-to-ngo' ? (
                          <>
                            <ListGroup.Item className="d-flex justify-content-between">
                              <span>📍 Distance</span>
                              <strong>{match.distance_km?.toFixed(2)} km</strong>
                            </ListGroup.Item>
                            <ListGroup.Item className="d-flex justify-content-between">
                              <span>⭐ Rating</span>
                              <strong>{match.rating}/5</strong>
                            </ListGroup.Item>
                            <ListGroup.Item className="d-flex justify-content-between">
                              <span>🎯 Specialty</span>
                              <strong>{match.specialty}</strong>
                            </ListGroup.Item>
                            <ListGroup.Item className="d-flex justify-content-between">
                              <span>📦 Capacity</span>
                              <strong>{match.capacity} units</strong>
                            </ListGroup.Item>
                          </>
                        ) : (
                          <>
                            <ListGroup.Item className="d-flex justify-content-between">
                              <span>🍱 Food Type</span>
                              <strong>{match.food_type}</strong>
                            </ListGroup.Item>
                            <ListGroup.Item className="d-flex justify-content-between">
                              <span>📊 Quantity</span>
                              <strong>{match.quantity}</strong>
                            </ListGroup.Item>
                            <ListGroup.Item className="d-flex justify-content-between">
                              <span>📍 Distance</span>
                              <strong>{match.distance_km?.toFixed(2)} km</strong>
                            </ListGroup.Item>
                            <ListGroup.Item className="d-flex justify-content-between">
                              <span>🚨 Urgency</span>
                              <strong>{match.urgency}</strong>
                            </ListGroup.Item>
                          </>
                        )}
                      </ListGroup>

                      <Button variant="primary" size="sm" className="mt-3 w-100">
                        View Details
                      </Button>
                    </div>
                  ))}
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}
    </Container>
  );
};

export default SmartMatching;
