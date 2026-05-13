import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Card, Form, Button, Spinner, ListGroup } from 'react-bootstrap';
import axios from 'axios';

/**
 * AI Chatbot Widget Component
 * Provides instant answers to FAQs and user inquiries
 */
const ChatbotWidget = () => {
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [faqCategories, setFaqCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [categoryDetails, setCategoryDetails] = useState(null);
  const [stats, setStats] = useState(null);
  const [view, setView] = useState('chat'); // 'chat' or 'faq'
  const messagesEndRef = useRef(null);
  const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  const getUserId = () => {
    const directUserId = localStorage.getItem('userId');
    if (directUserId) return directUserId;

    try {
      const storedUser = JSON.parse(localStorage.getItem('user') || 'null');
      return storedUser?.id || storedUser?._id || 'guest';
    } catch (error) {
      return 'guest';
    }
  };

  // Initialize chatbot on component mount
  useEffect(() => {
    const startConversation = async () => {
      try {
        const response = await axios.post(`${baseURL}/api/ai/chatbot/start`, {
          user_id: getUserId()
        });

        if (response.data.conversation_id) {
          setConversationId(response.data.conversation_id);
          setMessages([{
            id: 1,
            text: response.data.message,
            sender: 'bot',
            timestamp: new Date()
          }]);
        }
      } catch (err) {
        console.error('Error starting conversation:', err);
      }
    };

    const fetchFAQCategories = async () => {
      try {
        const response = await axios.get(`${baseURL}/api/ai/chatbot/faq`);
        if (response.data.success) {
          setFaqCategories(Object.entries(response.data.categories || {}));
        }
      } catch (err) {
        console.error('Error fetching FAQ categories:', err);
      }
    };

    const fetchChatbotStats = async () => {
      try {
        const response = await axios.get(`${baseURL}/api/ai/chatbot/stats`);
        if (response.data.success) {
          setStats(response.data);
        }
      } catch (err) {
        console.error('Error fetching stats:', err);
      }
    };

    const initialize = async () => {
      await startConversation();
      await fetchFAQCategories();
      await fetchChatbotStats();
    };
    initialize();
  }, [baseURL]);

  // Scroll to bottom on new messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchCategoryDetails = async (category) => {
    try {
      const response = await axios.get(`${baseURL}/api/ai/chatbot/faq/${category}`);
      if (response.data.success) {
        setCategoryDetails(response.data);
      }
    } catch (err) {
      console.error('Error fetching category details:', err);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!userInput.trim()) return;

    // Add user message to display
    const userMessage = {
      id: messages.length + 1,
      text: userInput,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages([...messages, userMessage]);
    setUserInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${baseURL}/api/ai/chatbot/message`, {
        message: userInput,
        conversation_id: conversationId,
        user_id: getUserId()
      });

      if (response.data.success) {
        const botMessage = {
          id: messages.length + 2,
          text: response.data.response,
          sender: 'bot',
          type: response.data.type,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, botMessage]);
      }
    } catch (err) {
      const errorMessage = {
        id: messages.length + 2,
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleCategorySelect = (categoryKey) => {
    setSelectedCategory(categoryKey);
    fetchCategoryDetails(categoryKey);
  };

  const handleSuggestedQuestion = (question) => {
    setUserInput(question);
  };

  return (
    <Container className="chatbot-container">
      <Row className="h-100">
        <Col lg={8}>
          <Card className="chatbot-card">
            <Card.Header className="bg-primary text-white d-flex justify-content-between align-items-center">
              <h5>💬 AI Chatbot Assistant</h5>
              <small>{conversationId}</small>
            </Card.Header>
            <Card.Body className="chat-messages-container">
              <div className="messages">
                {messages.map((message) => (
                  <div key={message.id} className={`message message-${message.sender}`}>
                    <div className="message-avatar">
                      {message.sender === 'bot' ? '🤖' : '👤'}
                    </div>
                    <div className="message-content">
                      <p>{message.text}</p>
                      <small className="message-time">
                        {message.timestamp.toLocaleTimeString()}
                      </small>
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="message message-bot">
                    <div className="message-avatar">🤖</div>
                    <div className="message-content">
                      <Spinner size="sm" />
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </Card.Body>
            <Card.Footer>
              <Form onSubmit={handleSendMessage}>
                <div className="input-group">
                  <Form.Control
                    type="text"
                    placeholder="Ask me anything..."
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    disabled={loading}
                  />
                  <Button 
                    variant="primary" 
                    type="submit"
                    disabled={loading || !userInput.trim()}
                  >
                    {loading ? <Spinner size="sm" /> : '📤'}
                  </Button>
                </div>
              </Form>
            </Card.Footer>
          </Card>
        </Col>

        <Col lg={4}>
          <Row className="mb-3">
            <Col>
              <div className="btn-group w-100" role="group">
                <input
                  type="radio"
                  className="btn-check"
                  name="view"
                  id="chatView"
                  value="chat"
                  checked={view === 'chat'}
                  onChange={(e) => setView(e.target.value)}
                />
                <label className="btn btn-outline-primary" htmlFor="chatView">
                  💬 Chat
                </label>

                <input
                  type="radio"
                  className="btn-check"
                  name="view"
                  id="faqView"
                  value="faq"
                  checked={view === 'faq'}
                  onChange={(e) => setView(e.target.value)}
                />
                <label className="btn btn-outline-primary" htmlFor="faqView">
                  ❓ FAQ
                </label>
              </div>
            </Col>
          </Row>

          {view === 'chat' && (
            <>
              <Card className="quick-questions-card mb-3">
                <Card.Header className="bg-info text-white">
                  <h6>💡 Quick Questions</h6>
                </Card.Header>
                <Card.Body>
                  <div className="questions-list">
                    <Button 
                      variant="light" 
                      size="sm" 
                      className="w-100 mb-2 text-start"
                      onClick={() => handleSuggestedQuestion('How do I donate food?')}
                    >
                      How do I donate food?
                    </Button>
                    <Button 
                      variant="light" 
                      size="sm" 
                      className="w-100 mb-2 text-start"
                      onClick={() => handleSuggestedQuestion('How to register as an NGO?')}
                    >
                      How to register as NGO?
                    </Button>
                    <Button 
                      variant="light" 
                      size="sm" 
                      className="w-100 mb-2 text-start"
                      onClick={() => handleSuggestedQuestion('What are the food safety guidelines?')}
                    >
                      Food safety guidelines?
                    </Button>
                    <Button 
                      variant="light" 
                      size="sm" 
                      className="w-100 text-start"
                      onClick={() => handleSuggestedQuestion('Is donation free?')}
                    >
                      Is donation free?
                    </Button>
                  </div>
                </Card.Body>
              </Card>

              <Card>
                <Card.Header className="bg-secondary text-white">
                  <h6>📊 Stats</h6>
                </Card.Header>
                <Card.Body>
                  {stats ? (
                    <>
                      <div className="stat">
                        <span>Active Conversations</span>
                        <strong>{stats.total_conversations}</strong>
                      </div>
                      <div className="stat">
                        <span>FAQ Categories</span>
                        <strong>{stats.faq_categories}</strong>
                      </div>
                      <div className="stat">
                        <span>Knowledge Base Items</span>
                        <strong>{stats.faq_items}</strong>
                      </div>
                    </>
                  ) : (
                    <Spinner size="sm" />
                  )}
                </Card.Body>
              </Card>
            </>
          )}

          {view === 'faq' && (
            <>
              {!selectedCategory ? (
                <Card className="faq-categories-card">
                  <Card.Header className="bg-warning text-dark">
                    <h6>📚 FAQ Categories</h6>
                  </Card.Header>
                  <Card.Body>
                    <ListGroup variant="flush">
                      {faqCategories.map(([categoryKey, categoryData]) => (
                        <ListGroup.Item 
                          key={categoryKey}
                          action
                          onClick={() => handleCategorySelect(categoryKey)}
                          className="cursor-pointer"
                        >
                          <div className="d-flex justify-content-between align-items-start">
                            <strong>{categoryData.title}</strong>
                          </div>
                          <small className="text-muted">
                            {categoryData.preview}
                          </small>
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  </Card.Body>
                </Card>
              ) : (
                <Card className="faq-detail-card">
                  <Card.Header className="bg-warning text-dark">
                    <Button 
                      variant="link" 
                      onClick={() => setSelectedCategory(null)}
                      className="p-0"
                    >
                      ← Back
                    </Button>
                    <h6>{categoryDetails?.title}</h6>
                  </Card.Header>
                  <Card.Body>
                    <div className="faq-content">
                      {categoryDetails?.content}
                    </div>
                    <div className="mt-3">
                      <small className="text-muted">
                        Related keywords: {categoryDetails?.triggers?.join(', ')}
                      </small>
                    </div>
                  </Card.Body>
                </Card>
              )}
            </>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default ChatbotWidget;
