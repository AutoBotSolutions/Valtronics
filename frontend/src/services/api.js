import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Device API endpoints
export const deviceAPI = {
  // Get all devices
  getDevices: (skip = 0, limit = 100) =>
    apiClient.get(`/devices?skip=${skip}&limit=${limit}`),

  // Get device by ID
  getDevice: (deviceId) =>
    apiClient.get(`/devices/${deviceId}`),

  // Create device
  createDevice: (deviceData) =>
    apiClient.post('/devices', deviceData),

  // Update device
  updateDevice: (deviceId, deviceData) =>
    apiClient.put(`/devices/${deviceId}`, deviceData),

  // Delete device
  deleteDevice: (deviceId) =>
    apiClient.delete(`/devices/${deviceId}`),

  // Update device status
  updateDeviceStatus: (deviceId, status) =>
    apiClient.patch(`/devices/${deviceId}/status`, { status }),

  // Get device telemetry
  getDeviceTelemetry: (deviceId, limit = 100, hours = 24) =>
    apiClient.get(`/devices/${deviceId}/telemetry?limit=${limit}&hours=${hours}`),

  // Create telemetry data
  createTelemetry: (deviceId, telemetryData) =>
    apiClient.post(`/devices/${deviceId}/telemetry`, telemetryData),

  // Create batch telemetry data
  createBatchTelemetry: (deviceId, telemetryData) =>
    apiClient.post(`/devices/${deviceId}/telemetry/batch`, telemetryData),

  // Get device commands
  getDeviceCommands: (deviceId) =>
    apiClient.get(`/devices/${deviceId}/commands`),

  // Create device command
  createDeviceCommand: (deviceId, commandData) =>
    apiClient.post(`/devices/${deviceId}/commands`, commandData),

  // Update command status
  updateCommandStatus: (commandId, status) =>
    apiClient.patch(`/commands/${commandId}/status`, { status }),

  // Get device statistics
  getDeviceStats: () =>
    apiClient.get('/devices/stats'),

  // Get devices by status
  getDevicesByStatus: (status) =>
    apiClient.get(`/devices/status/${status}`),
};

// AI API endpoints
export const aiAPI = {
  // Get device insights
  getInsights: (deviceId, query, timeRangeHours = 24) =>
    apiClient.post('/ai/insights', {
      device_id: deviceId,
      query,
      time_range_hours: timeRangeHours,
    }),

  // Detect anomalies
  detectAnomalies: (deviceId, metrics = ['temperature', 'vibration', 'power_consumption']) =>
    apiClient.post('/ai/anomaly-detection', {
      device_id: deviceId,
      metrics,
    }),

  // Get predictive maintenance
  getPredictiveMaintenance: (deviceId, predictionDays = 7) =>
    apiClient.post('/ai/predictive-maintenance', {
      device_id: deviceId,
      prediction_days: predictionDays,
    }),

  // Get device health score
  getHealthScore: (deviceId) =>
    apiClient.get(`/ai/device/${deviceId}/health-score`),
};

// Health API endpoints
export const healthAPI = {
  // Check system health
  checkHealth: () =>
    apiClient.get('/health/'),

  // Simple ping
  ping: () =>
    apiClient.get('/health/ping'),
};

// WebSocket connection for real-time updates
export class WebSocketService {
  constructor() {
    this.ws = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 5000;
  }

  connect(url = 'ws://localhost:8000/ws') {
    try {
      this.ws = new WebSocket(url);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.emit('connected');
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.emit(data.type || 'message', data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.emit('disconnected');
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', error);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      this.attemptReconnect();
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      setTimeout(() => this.connect(), this.reconnectInterval);
    } else {
      console.error('Max reconnection attempts reached');
      this.emit('maxReconnectAttemptsReached');
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => callback(data));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Export singleton WebSocket service
export const wsService = new WebSocketService();

// Utility functions
export const apiUtils = {
  // Format API error messages
  formatError: (error) => {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    } else if (error.message) {
      return error.message;
    } else {
      return 'An unexpected error occurred';
    }
  },

  // Handle API errors consistently
  handleError: (error, showToast = true) => {
    const message = apiUtils.formatError(error);
    console.error('API Error:', error);
    
    if (showToast) {
      // You can integrate toast notifications here
      console.error('Toast message:', message);
    }
    
    return message;
  },

  // Create query parameters from object
  createQueryParams: (params) => {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value);
      }
    });
    return searchParams.toString();
  },
};
