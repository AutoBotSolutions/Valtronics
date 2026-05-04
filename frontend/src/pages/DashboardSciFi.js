import React, { useState, useEffect } from 'react';
import '../styles/sci-fi-dashboard.css';

const DashboardSciFi = () => {
  const [devices, setDevices] = useState([]);
  const [telemetry, setTelemetry] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [systemStats, setSystemStats] = useState({
    totalDevices: 0,
    onlineDevices: 0,
    offlineDevices: 0,
    warningDevices: 0,
    systemLoad: 0,
    networkTraffic: 0,
    storageUsed: 0
  });
  const [isLoading, setIsLoading] = useState(true);

  // Simulate real-time data
  useEffect(() => {
    // Simulate initial data load
    const timer = setTimeout(() => {
      setDevices([
        { id: 'DEV-001', name: 'Temperature Sensor Alpha', type: 'sensor', status: 'online', location: 'Zone A', lastSeen: '2s ago', battery: 87 },
        { id: 'DEV-002', name: 'Pressure Monitor Beta', type: 'sensor', status: 'online', location: 'Zone B', lastSeen: '5s ago', battery: 92 },
        { id: 'DEV-003', name: 'Flow Controller Gamma', type: 'actuator', status: 'warning', location: 'Zone C', lastSeen: '1m ago', battery: 45 },
        { id: 'DEV-004', name: 'Voltage Sensor Delta', type: 'sensor', status: 'offline', location: 'Zone D', lastSeen: '15m ago', battery: 12 },
        { id: 'DEV-005', name: 'Humidity Monitor Epsilon', type: 'sensor', status: 'online', location: 'Zone E', lastSeen: '3s ago', battery: 78 },
        { id: 'DEV-006', name: 'Motor Controller Zeta', type: 'actuator', status: 'online', location: 'Zone F', lastSeen: '1s ago', battery: 95 },
        { id: 'DEV-007', name: 'Light Sensor Eta', type: 'sensor', status: 'online', location: 'Zone G', lastSeen: '4s ago', battery: 83 },
        { id: 'DEV-008', name: 'Temperature Sensor Theta', type: 'sensor', status: 'warning', location: 'Zone H', lastSeen: '30s ago', battery: 38 }
      ]);

      setTelemetry([
        { deviceId: 'DEV-001', temperature: 23.5, humidity: 45.2, pressure: 1013.25, timestamp: new Date() },
        { deviceId: 'DEV-002', temperature: 24.1, humidity: 43.8, pressure: 1012.87, timestamp: new Date() },
        { deviceId: 'DEV-005', temperature: 22.8, humidity: 46.1, pressure: 1013.45, timestamp: new Date() }
      ]);

      setAlerts([
        { id: 1, deviceId: 'DEV-003', type: 'warning', message: 'Low battery warning', severity: 'medium', timestamp: new Date() },
        { id: 2, deviceId: 'DEV-004', type: 'error', message: 'Device offline', severity: 'high', timestamp: new Date() },
        { id: 3, deviceId: 'DEV-008', type: 'warning', message: 'Sensor calibration needed', severity: 'low', timestamp: new Date() }
      ]);

      setIsLoading(false);
    }, 1500);

    // Simulate real-time updates
    const interval = setInterval(() => {
      setSystemStats(prev => ({
        ...prev,
        systemLoad: Math.max(0, Math.min(100, prev.systemLoad + Math.random() * 10 - 5)),
        networkTraffic: Math.max(0, Math.min(100, prev.networkTraffic + Math.random() * 8 - 4)),
        storageUsed: Math.min(100, prev.storageUsed + Math.random() * 2)
      }));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const totalDevices = devices.length;
    const onlineDevices = devices.filter(d => d.status === 'online').length;
    const offlineDevices = devices.filter(d => d.status === 'offline').length;
    const warningDevices = devices.filter(d => d.status === 'warning').length;

    setSystemStats(prev => ({
      ...prev,
      totalDevices,
      onlineDevices,
      offlineDevices,
      warningDevices
    }));
  }, [devices]);

  const getStatusClass = (status) => {
    switch (status) {
      case 'online': return 'status-online';
      case 'offline': return 'status-offline';
      case 'warning': return 'status-warning';
      default: return 'status-offline';
    }
  };

  const getAlertSeverityClass = (severity) => {
    switch (severity) {
      case 'high': return 'status-offline';
      case 'medium': return 'status-warning';
      case 'low': return 'status-online';
      default: return 'status-offline';
    }
  };

  const getBatteryColor = (battery) => {
    if (battery > 60) return '#00ff41';
    if (battery > 30) return '#ff6b35';
    return '#ff0040';
  };

  if (isLoading) {
    return (
      <div className="dashboard-container">
        <div className="matrix-rain"></div>
        <div className="grid-overlay"></div>
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: '100vh' 
        }}>
          <div className="loading-spinner"></div>
          <h1 style={{ 
            fontFamily: 'Orbitron, monospace', 
            fontSize: '2rem', 
            color: '#00ffff', 
            marginTop: '2rem',
            textTransform: 'uppercase',
            letterSpacing: '0.1em'
          }}>
            Loading Valtronics Interface...
          </h1>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="matrix-rain"></div>
      <div className="grid-overlay"></div>
      
      {/* Header */}
      <header className="dashboard-header">
        <div className="hologram-effect"></div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 className="dashboard-title">Valtronics Control Center</h1>
            <p style={{ fontFamily: 'Space Mono, monospace', color: '#b8b8c8', margin: '0.5rem 0 0 0' }}>
              Real-time IoT Management & Analytics
            </p>
          </div>
          <div className="status-indicator status-online">
            <span className="status-dot"></span>
            System Online
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="cyber-nav">
        <ul className="nav-list">
          <li><a href="#overview" className="nav-item active">Overview</a></li>
          <li><a href="#devices" className="nav-item">Devices</a></li>
          <li><a href="#telemetry" className="nav-item">Telemetry</a></li>
          <li><a href="#alerts" className="nav-item">Alerts</a></li>
          <li><a href="#analytics" className="nav-item">Analytics</a></li>
        </ul>
      </nav>

      {/* System Overview */}
      <div className="dashboard-grid">
        <div className="cyber-card">
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">Total Devices</h3>
            <div className="card-icon">📡</div>
          </div>
          <div className="metric-value live-data">{systemStats.totalDevices}</div>
          <div className="metric-label">Connected Systems</div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: '100%' }}></div>
          </div>
        </div>

        <div className="cyber-card">
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">Online Devices</h3>
            <div className="card-icon">⚡</div>
          </div>
          <div className="metric-value live-data">{systemStats.onlineDevices}</div>
          <div className="metric-label">Active Systems</div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ 
                width: `${systemStats.totalDevices > 0 ? (systemStats.onlineDevices / systemStats.totalDevices) * 100 : 0}%` 
              }}
            ></div>
          </div>
        </div>

        <div className="cyber-card">
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">System Alerts</h3>
            <div className="card-icon">⚠️</div>
          </div>
          <div className="metric-value live-data">{alerts.length}</div>
          <div className="metric-label">Active Warnings</div>
          <div className="metric-change negative">
            <span>↑</span> {systemStats.warningDevices} devices need attention
          </div>
        </div>

        <div className="cyber-card">
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">System Load</h3>
            <div className="card-icon">💻</div>
          </div>
          <div className="metric-value live-data">{Math.round(systemStats.systemLoad)}%</div>
          <div className="metric-label">CPU Usage</div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${systemStats.systemLoad}%` }}></div>
          </div>
        </div>

        <div className="cyber-card">
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">Network Traffic</h3>
            <div className="card-icon">🌐</div>
          </div>
          <div className="metric-value live-data">{Math.round(systemStats.networkTraffic)}%</div>
          <div className="metric-label">Bandwidth Usage</div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${systemStats.networkTraffic}%` }}></div>
          </div>
        </div>

        <div className="cyber-card">
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">Storage Used</h3>
            <div className="card-icon">💾</div>
          </div>
          <div className="metric-value live-data">{Math.round(systemStats.storageUsed)}%</div>
          <div className="metric-label">Database Capacity</div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${systemStats.storageUsed}%` }}></div>
          </div>
        </div>
      </div>

      {/* Device Status Matrix */}
      <div className="chart-container">
        <div className="hologram-effect"></div>
        <div className="card-header">
          <h3 className="card-title">Device Status Matrix</h3>
          <button className="cyber-button">
            <span>Refresh</span>
          </button>
        </div>
        
        <table className="data-table">
          <thead>
            <tr>
              <th>Device ID</th>
              <th>Name</th>
              <th>Type</th>
              <th>Status</th>
              <th>Location</th>
              <th>Battery</th>
              <th>Last Seen</th>
            </tr>
          </thead>
          <tbody>
            {devices.map((device, index) => (
              <tr key={device.id} className={index % 2 === 0 ? 'glitch-effect' : ''}>
                <td>{device.id}</td>
                <td>{device.name}</td>
                <td>{device.type}</td>
                <td>
                  <span className={`status-indicator ${getStatusClass(device.status)}`}>
                    <span className="status-dot"></span>
                    {device.status.toUpperCase()}
                  </span>
                </td>
                <td>{device.location}</td>
                <td>
                  <span style={{ color: getBatteryColor(device.battery) }}>
                    {device.battery}%
                  </span>
                </td>
                <td>{device.lastSeen}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Alerts Panel */}
      <div className="dashboard-grid">
        <div className="cyber-card" style={{ gridColumn: 'span 2' }}>
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">Active Alerts</h3>
            <div className="card-icon">🚨</div>
          </div>
          
          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {alerts.map(alert => (
              <div key={alert.id} style={{ 
                padding: '1rem', 
                margin: '0.5rem 0', 
                background: 'rgba(0, 255, 255, 0.05)', 
                border: '1px solid rgba(0, 255, 255, 0.2)', 
                borderRadius: '8px' 
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span className={`status-indicator ${getAlertSeverityClass(alert.severity)}`}>
                    <span className="status-dot"></span>
                    {alert.deviceId}
                  </span>
                  <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>
                    {alert.timestamp.toLocaleTimeString()}
                  </span>
                </div>
                <div style={{ marginTop: '0.5rem', color: '#b8b8c8' }}>
                  {alert.message}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="cyber-card">
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">System Health</h3>
            <div className="card-icon">🏥</div>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="status-indicator status-online">
              <span className="status-dot"></span>
              Quantum Core: Operational
            </div>
            <div className="status-indicator status-online">
              <span className="status-dot"></span>
              Neural Network: Active
            </div>
            <div className="status-indicator status-warning">
              <span className="status-dot"></span>
              Data Sync: Delayed
            </div>
            <div className="status-indicator status-online">
              <span className="status-dot"></span>
              Security: Secured
            </div>
          </div>
        </div>
      </div>

      {/* Control Panel */}
      <div className="chart-container">
        <div className="hologram-effect"></div>
        <div className="card-header">
          <h3 className="card-title">System Controls</h3>
        </div>
        
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <button className="cyber-button">
            <span>Run Diagnostics</span>
          </button>
          <button className="cyber-button">
            <span>System Backup</span>
          </button>
          <button className="cyber-button">
            <span>Security Scan</span>
          </button>
          <button className="cyber-button">
            <span>Performance Optimize</span>
          </button>
          <button className="cyber-button">
            <span>Export Logs</span>
          </button>
          <button className="cyber-button">
            <span>Reboot System</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default DashboardSciFi;
