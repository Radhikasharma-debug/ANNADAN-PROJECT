const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
const DEFAULT_TIMEOUT_MS = Number(process.env.REACT_APP_API_TIMEOUT_MS || 15000);

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const parseResponseBody = async (response) => {
  const text = await response.text();
  if (!text) {
    return {};
  }

  try {
    return JSON.parse(text);
  } catch (error) {
    return { message: text };
  }
};

const request = async (method, endpoint, payload) => {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      ...(payload !== undefined ? { body: JSON.stringify(payload) } : {}),
    });

    const data = await parseResponseBody(response);

    if (!response.ok) {
      const err = new Error(data.error || data.message || `Error: ${response.statusText}`);
      err.response = { data, status: response.status };
      throw err;
    }

    return data;
  } catch (error) {
    if (error.name === 'AbortError') {
      const timeoutError = new Error('Request timed out. Please try again.');
      timeoutError.response = { data: { error: 'timeout' }, status: 408 };
      throw timeoutError;
    }

    throw error;
  } finally {
    clearTimeout(timeout);
  }
};

const apiClient = {
  get: (endpoint) => request('GET', endpoint),
  post: (endpoint, data) => request('POST', endpoint, data),
  put: (endpoint, data) => request('PUT', endpoint, data),
  delete: (endpoint) => request('DELETE', endpoint),
};

export default apiClient;
