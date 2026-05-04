import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Activity, 
  Settings, 
  Send, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  TrendingUp,
  BarChart3,
  Clock,
  MapPin,
  Cpu,
  Zap,
  Thermometer,
  Droplets
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { deviceAPI, aiAPI, wsService } from '../services/api';
import toast from 'react-hot-toast';

const DeviceDetail = () => {
  const { id } = useParams();
  const [device, setDevice] = useState(null);
  const [telemetry, setTelemetry] = useState([]);
  const [healthScore, setHealthScore] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [commandInput, setCommandInput] = useState('');
  const [sendingCommand, setSendingCommand] = useState(false);

  useEffect(() => {
    fetchDeviceData();
    connectWebSocket();
    
    return () => {
      wsService.disconnect();
    };
  }, [id]);

  const fetchDeviceData = async () => {
    try {
      setLoading(true);
      const [deviceResponse, telemetryResponse, healthResponse, anomalyResponse] = await Promise.all([
        deviceAPI.getDevice(id),
        deviceAPI.getDeviceTelemetry(id, 100, 24),
        aiAPI.getHealthScore(id),
        aiAPI.detectAnomalies(id)
      ]);

      setDevice(deviceResponse.data);
      setTelemetry(telemetryResponse.data);
      setHealthScore(healthResponse.data);
      setAnomalies(anomalyResponse.data.anomalies_detected || []);
    } catch (error) {
      toast.error('Failed to load device data');
      console.error('Device data fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const connectWebSocket = () => {
    wsService.on('telemetry_update', (data) => {
      if (data.device_id == id) {
        setTelemetry(prev => [data.data, ...prev.slice(0, 99)]);
      }
    });

    wsService.on('device_update', (data) => {
      if (data.device_id == id) {
        setDevice(prev => ({ ...prev, ...data.updates }));
      }
    });
  };

  const sendCommand = async () => {
    if (!commandInput.trim()) return;

    try {
      setSendingCommand(true);
      await deviceAPI.createDeviceCommand(id, {
        command: commandInput,
        parameters: {}
      });
      toast.success('Command sent successfully');
      setCommandInput('');
    } catch (error) {
      toast.error('Failed to send command');
      console.error('Command send error:', error);
    } finally {
      setSendingCommand(false);
    }
  };

  const getMetricIcon = (metricName) => {
    switch (metricName.toLowerCase()) {
      case 'temperature':
        return <Thermometer className="w-4 h-4" />;
      case 'humidity':
        return <Droplets className="w-4 h-4" />;
      case 'power':
      case 'voltage':
      case 'current':
        return <Zap className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'online':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'offline':
        return <XCircle className="w-6 h-6 text-red-500" />;
      case 'error':
        return <AlertTriangle className="w-6 h-6 text-yellow-500" />;
      default:
        return <Activity className="w-6 h-6 text-gray-500" />;
    }
  };

  const formatTelemetryData = (metricName) => {
    const metricData = telemetry
      .filter(t => t.metric_name === metricName)
      .slice(0, 20)
      .reverse()
      .map(t => ({
        time: new Date(t.timestamp).toLocaleTimeString(),
        value: t.metric_value
      }));

    return metricData;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!device) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Cpu className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Device not found</h3>
          <p className="mt-1 text-sm text-gray-500">
            The device you're looking for doesn't exist.
          </p>
          <div className="mt-6">
            <Link
              to="/dashboard"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const uniqueMetrics = [...new Set(telemetry.map(t => t.metric_name))];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link
                to="/dashboard"
                className="inline-flex items-center text-gray-600 hover:text-gray-900 mr-4"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back
              </Link>
              <div className="flex items-center">
                {getStatusIcon(device.status)}
                <div className="ml-3">
                  <h1 className="text-2xl font-bold text-gray-900">{device.name}</h1>
                  <p className="text-sm text-gray-600">{device.device_id}</p>
                </div>
              </div>
            </div>
            <Link
              to={`/devices/${id}/settings`}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Device Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Cpu className="w-8 h-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Device Type</p>
                <p className="text-lg font-semibold text-gray-900">{device.device_type}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <MapPin className="w-8 h-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Location</p>
                <p className="text-lg font-semibold text-gray-900">{device.location || 'Not set'}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Clock className="w-8 h-8 text-purple-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Last Seen</p>
                <p className="text-lg font-semibold text-gray-900">
                  {device.last_seen ? 
                    new Date(device.last_seen).toLocaleString() : 
                    'Never'
                  }
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Health Score and Anomalies */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Health Score</h3>
            {healthScore ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-600">Overall Health</span>
                  <span className={`text-lg font-bold ${
                    healthScore.health_score > 0.7 ? 'text-green-600' :
                    healthScore.health_score > 0.4 ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {Math.round(healthScore.health_score * 100)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      healthScore.health_score > 0.7 ? 'bg-green-500' :
                      healthScore.health_score > 0.4 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${healthScore.health_score * 100}%` }}
                  ></div>
                </div>
                <div className="text-sm text-gray-600">
                  Status: <span className="font-medium">{healthScore.status}</span>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">Health score not available</p>
            )}
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Anomalies</h3>
            {anomalies.length > 0 ? (
              <div className="space-y-2">
                {anomalies.slice(0, 3).map((anomaly, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-yellow-50 rounded">
                    <div className="flex items-center">
                      <AlertTriangle className="w-4 h-4 text-yellow-600 mr-2" />
                      <span className="text-sm text-gray-700">{anomaly.metric}</span>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded ${
                      anomaly.severity === 'high' ? 'bg-red-100 text-red-800' :
                      anomaly.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {anomaly.severity}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No anomalies detected</p>
            )}
          </div>
        </div>

        {/* Telemetry Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {uniqueMetrics.map(metric => (
            <div key={metric} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 capitalize">{metric}</h3>
                <div className="flex items-center text-gray-600">
                  {getMetricIcon(metric)}
                  <span className="ml-1 text-sm">
                    {telemetry.find(t => t.metric_name === metric)?.unit || ''}
                  </span>
                </div>
              </div>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={formatTelemetryData(metric)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ))}
        </div>

        {/* Command Interface */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Device Commands</h3>
          <div className="flex space-x-4">
            <input
              type="text"
              value={commandInput}
              onChange={(e) => setCommandInput(e.target.value)}
              placeholder="Enter command..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            <button
              onClick={sendCommand}
              disabled={sendingCommand || !commandInput.trim()}
              className="inline-flex items-center px-6 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {sendingCommand ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <Send className="w-4 h-4 mr-2" />
              )}
              Send Command
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DeviceDetail;
