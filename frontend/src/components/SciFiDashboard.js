import React, { useState, useEffect } from 'react';
import './sci-fi-dashboard.css';

const SciFiDashboard = () => {
  const [metrics, setMetrics] = useState({
    totalDevices: 1247,
    activeDevices: 1189,
    alerts: 23,
    systemLoad: 67,
    dataProcessed: '2.4TB',
    uptime: '99.97%'
  });

  const [devices, setDevices] = useState([
    { id: 'DEV-001', name: 'Temperature Sensor Alpha', status: 'online', location: 'Zone A', lastSeen: '2s ago' },
    { id: 'DEV-002', name: 'Pressure Monitor Beta', status: 'online', location: 'Zone B', lastSeen: '5s ago' },
    { id: 'DEV-003', name: 'Flow Controller Gamma', status: 'warning', location: 'Zone C', lastSeen: '1m ago' },
    { id: 'DEV-004', name: 'Voltage Sensor Delta', status: 'offline', location: 'Zone D', lastSeen: '15m ago' },
    { id: 'DEV-005', name: 'Humidity Monitor Epsilon', status: 'online', location: 'Zone E', lastSeen: '3s ago' }
  ]);

  const [activeNav, setActiveNav] = useState('overview');

  // Simulate real-time data updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        activeDevices: prev.activeDevices + Math.floor(Math.random() * 3) - 1,
        systemLoad: Math.max(0, Math.min(100, prev.systemLoad + Math.floor(Math.random() * 5) - 2)),
        dataProcessed: (parseFloat(prev.dataProcessed) + Math.random() * 0.1).toFixed(1) + 'TB'
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const getStatusClass = (status) => {
    switch (status) {
      case 'online': return 'status-online';
      case 'offline': return 'status-offline';
      case 'warning': return 'status-warning';
      default: return 'status-offline';
    }
  };

  const getChangeClass = (value) => {
    return value >= 0 ? 'positive' : 'negative';
  };

  return (
    <div className="dashboard-container">
      <div className="matrix-rain"></div>
      <div className="grid-overlay"></div>
      
      {/* Header */}
      <header className="dashboard-header">
        <div className="hologram-effect"></div>
        <h1 className="dashboard-title">Valtronics Command Center</h1>
        <div className="status-indicator status-online">
          <span className="status-dot"></span>
          System Operational
        </div>
      </header>

      {/* Navigation */}
      <nav className="cyber-nav">
        <ul className="nav-list">
          <li>
            <a 
              href="#overview" 
              className={`nav-item ${activeNav === 'overview' ? 'active' : ''}`}
              onClick={() => setActiveNav('overview')}
            >
              Overview
            </a>
          </li>
          <li>
            <a 
              href="#devices" 
              className={`nav-item ${activeNav === 'devices' ? 'active' : ''}`}
              onClick={() => setActiveNav('devices')}
            >
              Devices
            </a>
          </li>
          <li>
            <a 
              href="#analytics" 
              className={`nav-item ${activeNav === 'analytics' ? 'active' : ''}`}
              onClick={() => setActiveNav('analytics')}
            >
              Analytics
            </a>
          </li>
          <li>
            <a 
              href="#alerts" 
              className={`nav-item ${activeNav === 'alerts' ? 'active' : ''}`}
              onClick={() => setActiveNav('alerts')}
            >
              Alerts
            </a>
          </li>
        </ul>
      </nav>

      {/* Metrics Grid */}
      <div className="dashboard-grid">
        <div className="cyber-card">
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">Total Devices</h3>
            <div className="card-icon">📡</div>
          </div>
          <div className="metric-value live-data">{metrics.totalDevices.toLocaleString()}</div>
          <div className="metric-label">Connected Systems</div>
          <div className="metric-change positive">
            <span>↑</span> +12 this hour
          </div>
        </div>

        <div className="cyber-card">
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">Active Devices</h3>
            <div className="card-icon">⚡</div>
          </div>
          <div className="metric-value live-data">{metrics.activeDevices.toLocaleString()}</div>
          <div className="metric-label">Online Systems</div>
          <div className="metric-change positive">
            <span>↑</span> 95.3% uptime
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${(metrics.activeDevices / metrics.totalDevices) * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="cyber-card">
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">System Alerts</h3>
            <div className="card-icon">⚠️</div>
          </div>
          <div className="metric-value live-data">{metrics.alerts}</div>
          <div className="metric-label">Active Warnings</div>
          <div className="metric-change negative">
            <span>↑</span> +3 new alerts
          </div>
        </div>

        <div className="cyber-card">
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">System Load</h3>
            <div className="card-icon">💻</div>
          </div>
          <div className="metric-value live-data">{metrics.systemLoad}%</div>
          <div className="metric-label">CPU Usage</div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${metrics.systemLoad}%` }}
            ></div>
          </div>
        </div>

        <div className="cyber-card">
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">Data Processed</h3>
            <div className="card-icon">📊</div>
          </div>
          <div className="metric-value live-data">{metrics.dataProcessed}</div>
          <div className="metric-label">Today's Volume</div>
          <div className="metric-change positive">
            <span>↑</span> 18% increase
          </div>
        </div>

        <div className="cyber-card">
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">System Uptime</h3>
            <div className="card-icon">🔧</div>
          </div>
          <div className="metric-value live-data">{metrics.uptime}</div>
          <div className="metric-label">Last 30 Days</div>
          <div className="metric-change positive">
            <span>↑</span> Excellent
          </div>
        </div>
      </div>

      {/* Devices Table */}
      <div className="chart-container">
        <div className="hologram-effect"></div>
        <div className="card-header">
          <h3 className="card-title">Device Status Matrix</h3>
          <button className="cyber-button">
            <span>Refresh Data</span>
          </button>
        </div>
        
        <table className="data-table">
          <thead>
            <tr>
              <th>Device ID</th>
              <th>Name</th>
              <th>Status</th>
              <th>Location</th>
              <th>Last Seen</th>
            </tr>
          </thead>
          <tbody>
            {devices.map((device, index) => (
              <tr key={device.id} className={index % 2 === 0 ? 'glitch-effect' : ''}>
                <td>{device.id}</td>
                <td>{device.name}</td>
                <td>
                  <span className={`status-indicator ${getStatusClass(device.status)}`}>
                    <span className="status-dot"></span>
                    {device.status.toUpperCase()}
                  </span>
                </td>
                <td>{device.location}</td>
                <td>{device.lastSeen}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Analytics Section */}
      <div className="dashboard-grid">
        <div className="cyber-card">
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">Network Traffic</h3>
            <div className="card-icon">🌐</div>
          </div>
          <div className="metric-value">847 MB/s</div>
          <div className="metric-label">Current Bandwidth</div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: '71%' }}></div>
          </div>
        </div>

        <div className="cyber-card">
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">Response Time</h3>
            <div className="card-icon">⚡</div>
          </div>
          <div className="metric-value">12ms</div>
          <div className="metric-label">Average Latency</div>
          <div className="metric-change positive">
            <span>↓</span> Optimized
          </div>
        </div>

        <div className="cyber-card">
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">Storage Used</h3>
            <div className="card-icon">💾</div>
          </div>
          <div className="metric-value">3.2TB</div>
          <div className="metric-label">of 10TB Total</div>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: '32%' }}></div>
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
        </div>
      </div>

      {/* Footer Status */}
      <div className="dashboard-header" style={{ marginTop: '2rem' }}>
        <div className="hologram-effect"></div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div className="status-indicator status-online">
            <span className="status-dot"></span>
            Quantum Core Online
          </div>
          <div className="status-indicator status-online">
            <span className="status-dot"></span>
            Neural Network Active
          </div>
          <div className="status-indicator status-online">
            <span className="status-dot"></span>
            Data Sync Operational
          </div>
          <div className="status-indicator status-warning">
            <span className="status-dot"></span>
            3 Devices Need Attention
          </div>
        </div>
      </div>
    </div>
  );
};

export default SciFiDashboard;
