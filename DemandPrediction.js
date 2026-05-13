import React, { useState, useEffect, useCallback } from 'react';
import { Container, Row, Col, Card, Form, Spinner, Alert } from 'react-bootstrap';
import axios from 'axios';

/**
 * Demand Prediction Component
 * Predicts food demand patterns and urgency levels
 */
const DemandPrediction = () => {
  const [daysAhead, setDaysAhead] = useState(7);
  const [predictions, setPredictions] = useState([]);
  const [urgency, setUrgency] = useState([]);
  const [criticalPeriods, setCriticalPeriods] = useState([]);
  const [accuracy, setAccuracy] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  const fetchPredictions = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${baseURL}/api/ai/demand/predict?days_ahead=${daysAhead}&include_by_type=true`
      );
      
      if (response.data.success) {
        setPredictions(response.data.predictions || []);
      }
    } catch (err) {
      setError('Error fetching predictions');
    } finally {
      setLoading(false);
    }
  }, [daysAhead, baseURL]);

  const fetchUrgency = useCallback(async () => {
    try {
      const response = await axios.get(
        `${baseURL}/api/ai/demand/urgency?days_ahead=${daysAhead}`
      );
      
      if (response.data.success) {
        setUrgency(response.data.urgency_predictions || []);
      }
    } catch (err) {
      console.error('Error fetching urgency:', err);
    }
  }, [daysAhead, baseURL]);

  const fetchCriticalPeriods = useCallback(async () => {
    try {
      const response = await axios.get(
        `${baseURL}/api/ai/demand/critical-periods`
      );
      
      if (response.data.success) {
        setCriticalPeriods(response.data.critical_periods || []);
      }
    } catch (err) {
      console.error('Error fetching critical periods:', err);
    }
  }, [baseURL]);

  const fetchAccuracy = useCallback(async () => {
    try {
      const response = await axios.get(
        `${baseURL}/api/ai/demand/accuracy`
      );
      
      if (response.data.success) {
        setAccuracy(response.data);
      }
    } catch (err) {
      console.error('Error fetching accuracy:', err);
    }
  }, [baseURL]);

  useEffect(() => {
    const initializePredictions = async () => {
      await Promise.all([
        fetchPredictions(),
        fetchUrgency(),
        fetchCriticalPeriods(),
        fetchAccuracy()
      ]);
    };
    initializePredictions();
  }, [fetchPredictions, fetchUrgency, fetchCriticalPeriods, fetchAccuracy]);

  const getUrgencyBadge = (urgency) => {
    const colors = {
      'critical': 'danger',
      'high': 'warning',
      'medium': 'info',
      'low': 'success'
    };
    return colors[urgency] || 'secondary';
  };

  const getRecommendationColor = (recommendation) => {
    if (recommendation.includes('Urgent')) return 'danger';
    if (recommendation.includes('High')) return 'warning';
    if (recommendation.includes('Medium')) return 'info';
    if (recommendation.includes('Low')) return 'success';
    return 'secondary';
  };

  return (
    <Container className="demand-prediction-container">
      <Row className="mb-4">
        <Col lg={12}>
          <Card className="prediction-control-card">
            <Card.Header className="bg-primary text-white">
              <h5>📈 Demand Forecasting</h5>
            </Card.Header>
            <Card.Body>
              <Form.Group className="mb-3">
                <Form.Label>Forecast Period (Days Ahead)</Form.Label>
                <Form.Range
                  min="1"
                  max="30"
                  value={daysAhead}
                  onChange={(e) => setDaysAhead(parseInt(e.target.value))}
                />
                <small className="text-muted">
                  Showing forecast for {daysAhead} days
                </small>
              </Form.Group>

              {error && <Alert variant="danger">{error}</Alert>}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col lg={4} md={6} className="mb-3">
          <Card className="metric-card">
            <Card.Body className="text-center">
              <h6>Model Accuracy (MAPE)</h6>
              <h3 className="text-primary">
                {accuracy?.mape ? `${(100 - accuracy.mape).toFixed(1)}%` : 'N/A'}
              </h3>
              <small className="text-muted">Mean Absolute % Error</small>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4} md={6} className="mb-3">
          <Card className="metric-card">
            <Card.Body className="text-center">
              <h6>Prediction Error (RMSE)</h6>
              <h3 className="text-info">
                {accuracy?.rmse ? `${accuracy.rmse.toFixed(1)}` : 'N/A'}
              </h3>
              <small className="text-muted">Root Mean Squared Error</small>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4} md={6} className="mb-3">
          <Card className="metric-card">
            <Card.Body className="text-center">
              <h6>Model Status</h6>
              <h3 className="text-success">✓ Active</h3>
              <small className="text-muted">{accuracy?.recommendation}</small>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col lg={12}>
          <Card className="predictions-card">
            <Card.Header className="bg-success text-white">
              <h5>📅 Demand Forecast</h5>
            </Card.Header>
            <Card.Body>
              {loading ? (
                <div className="text-center">
                  <Spinner />
                </div>
              ) : (
                <div className="forecast-table">
                  <div className="table-responsive">
                    <table className="table">
                      <thead>
                        <tr>
                          <th>Date</th>
                          <th>Day</th>
                          <th>Predicted Demand</th>
                          <th>Confidence</th>
                          <th>Recommendation</th>
                        </tr>
                      </thead>
                      <tbody>
                        {predictions.map((pred, index) => (
                          <tr key={index}>
                            <td><strong>{pred.date}</strong></td>
                            <td>{pred.day_name}</td>
                            <td>
                              <span className="badge bg-primary">
                                {pred.predicted_demand} units
                              </span>
                            </td>
                            <td>
                              <div className="confidence-bar">
                                <div 
                                  className="confidence-fill"
                                  style={{ width: `${pred.confidence * 100}%` }}
                                />
                              </div>
                              {(pred.confidence * 100).toFixed(0)}%
                            </td>
                            <td>
                              <span className={`badge bg-${getRecommendationColor(pred.recommendation)}`}>
                                {pred.recommendation.split(':')[0]}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mb-4">
        <Col lg={6}>
          <Card className="urgency-card">
            <Card.Header className="bg-warning text-dark">
              <h5>🚨 Urgency Levels</h5>
            </Card.Header>
            <Card.Body>
              <div className="urgency-list">
                {urgency.map((item, index) => (
                  <div key={index} className="urgency-item">
                    <div className="urgency-header">
                      <span className="date">{item.date}</span>
                      <span className={`badge bg-${getUrgencyBadge(item.urgency_level)}`}>
                        {item.urgency_level.toUpperCase()}
                      </span>
                    </div>
                    <div className="urgency-details">
                      <small>Expected Demand: {item.expected_demand.toFixed(0)} units</small>
                      <span className="priority-badge">Priority: {item.priority}</span>
                    </div>
                  </div>
                ))}
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={6}>
          <Card className="critical-periods-card">
            <Card.Header className="bg-danger text-white">
              <h5>⚠️ Critical Periods</h5>
            </Card.Header>
            <Card.Body>
              {criticalPeriods.length > 0 ? (
                <div className="critical-list">
                  {criticalPeriods.map((period, index) => (
                    <div key={index} className="critical-item">
                      <div className="critical-date">
                        <strong>{period.date}</strong>
                        <span className={`severity-badge ${period.severity}`}>
                          {period.severity.toUpperCase()}
                        </span>
                      </div>
                      <div className="critical-demand">
                        <span className="label">Expected Demand:</span>
                        <span className="value">{period.demand.toFixed(0)} units</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <Alert variant="success">
                  ✓ No critical periods detected in the forecast period
                </Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        <Col lg={12}>
          <Card className="insights-card">
            <Card.Header className="bg-info text-white">
              <h5>💡 Key Insights</h5>
            </Card.Header>
            <Card.Body>
              <ul className="insights-list">
                <li>📊 Demand forecast uses historical data and seasonal patterns</li>
                <li>⏰ Predictions include day-of-week and temporal factors</li>
                <li>🎯 Confidence scores reflect data availability and model certainty</li>
                <li>🚨 Urgency levels help prioritize resources for peak demand periods</li>
                <li>💚 Plan ahead with critical period alerts to minimize food waste</li>
              </ul>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default DemandPrediction;
