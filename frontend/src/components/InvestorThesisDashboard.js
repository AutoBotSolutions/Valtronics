import React, { useState, useEffect } from 'react';
import '../styles/sci-fi-dashboard.css';

const InvestorThesisDashboard = () => {
  const [metrics, setMetrics] = useState({
    totalDevices: 1247,
    activeDevices: 1189,
    alerts: 23,
    systemLoad: 67,
    dataProcessed: '2.4TB',
    uptime: '99.97%',
    revenue: '$847K',
    growth: '+34%',
    marketValue: '$47B'
  });

  const [devices, setDevices] = useState([
    { id: 'DEV-001', name: 'Temperature Sensor Alpha', status: 'online', location: 'Zone A', lastSeen: '2s ago', efficiency: 94 },
    { id: 'DEV-002', name: 'Pressure Monitor Beta', status: 'online', location: 'Zone B', lastSeen: '5s ago', efficiency: 89 },
    { id: 'DEV-003', name: 'Flow Controller Gamma', status: 'warning', location: 'Zone C', lastSeen: '1m ago', efficiency: 76 },
    { id: 'DEV-004', name: 'Voltage Sensor Delta', status: 'offline', location: 'Zone D', lastSeen: '15m ago', efficiency: 0 },
    { id: 'DEV-005', name: 'Humidity Monitor Epsilon', status: 'online', location: 'Zone E', lastSeen: '3s ago', efficiency: 91 }
  ]);

  const [systemTime, setSystemTime] = useState(new Date());

  // Simulate real-time data updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        activeDevices: prev.activeDevices + Math.floor(Math.random() * 3) - 1,
        systemLoad: Math.max(0, Math.min(100, prev.systemLoad + Math.floor(Math.random() * 5) - 2)),
        dataProcessed: (parseFloat(prev.dataProcessed) + Math.random() * 0.1).toFixed(1) + 'TB',
        revenue: '$' + (parseFloat(prev.revenue.replace('$', '').replace('K', '')) + Math.random() * 2).toFixed(0) + 'K'
      }));
    }, 3000);

    const timeInterval = setInterval(() => {
      setSystemTime(new Date());
    }, 1000);

    return () => {
      clearInterval(interval);
      clearInterval(timeInterval);
    };
  }, []);

  const getStatusClass = (status) => {
    switch (status) {
      case 'online': return 'status-online';
      case 'offline': return 'status-offline';
      case 'warning': return 'status-warning';
      default: return 'status-offline';
    }
  };

  const getEfficiencyColor = (efficiency) => {
    if (efficiency >= 90) return 'var(--gold-color)';
    if (efficiency >= 70) return 'var(--accent-color)';
    if (efficiency > 0) return 'var(--cyber-warning)';
    return 'var(--cyber-danger)';
  };

  return (
    <div className="dashboard-container">
      <div className="matrix-rain"></div>
      <div className="grid-overlay"></div>
      
      {/* Header with Investor Thesis Styling */}
      <header className="dashboard-header">
        <div className="hologram-effect"></div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 className="dashboard-title">Valtronics Command Center</h1>
            <p style={{ 
              fontFamily: 'Space Mono, monospace', 
              color: 'var(--text-secondary)', 
              margin: '0.5rem 0 0 0',
              fontSize: '0.9rem'
            }}>
              AI-Powered Intelligent Electronics Ecosystem
            </p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ 
              fontFamily: 'Orbitron, monospace', 
              fontSize: '1.2rem', 
              color: 'var(--gold-color)',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              textShadow: 'var(--profit-glow)'
            }}>
              {systemTime.toLocaleTimeString()}
            </div>
            <div style={{ 
              fontFamily: 'Space Mono, monospace', 
              color: 'var(--text-secondary)', 
              fontSize: '0.8rem',
              marginTop: '0.25rem'
            }}>
              {systemTime.toLocaleDateString()}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="cyber-nav">
        <ul className="nav-list">
          <li><a href="#overview" className="nav-item active">Overview</a></li>
          <li><a href="#devices" className="nav-item">Devices</a></li>
          <li><a href="#analytics" className="nav-item">Analytics</a></li>
          <li><a href="#financials" className="nav-item">Financials</a></li>
          <li><a href="#alerts" className="nav-item">Alerts</a></li>
        </ul>
      </nav>

      {/* Premium Metrics Grid */}
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
            <h3 className="card-title">System Revenue</h3>
            <div className="card-icon">💰</div>
          </div>
          <div className="metric-value live-data" style={{ color: 'var(--gold-color)' }}>
            {metrics.revenue}
          </div>
          <div className="metric-label">Monthly Recurring</div>
          <div className="metric-change positive">
            <span>↑</span> {metrics.growth} growth
          </div>
        </div>

        <div className="cyber-card">
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">Market Value</h3>
            <div className="card-icon">🏆</div>
          </div>
          <div className="metric-value live-data" style={{ color: 'var(--gold-color)' }}>
            {metrics.marketValue}
          </div>
          <div className="metric-label">Total Addressable</div>
          <div className="metric-change positive">
            <span>↑</span> 47% CAGR
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
            <div className="progress-fill" style={{ width: `${metrics.systemLoad}%` }}></div>
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
      </div>

      {/* Enhanced Device Table */}
      <div className="chart-container">
        <div className="hologram-effect"></div>
        <div className="card-header">
          <h3 className="card-title">Device Performance Matrix</h3>
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
              <th>Efficiency</th>
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
                <td>
                  <span style={{ 
                    color: getEfficiencyColor(device.efficiency),
                    fontWeight: 'bold',
                    textShadow: device.efficiency >= 90 ? 'var(--profit-glow)' : 'none'
                  }}>
                    {device.efficiency}%
                  </span>
                </td>
                <td>{device.lastSeen}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Financial Overview Section */}
      <div className="dashboard-grid">
        <div className="cyber-card" style={{ gridColumn: 'span 2' }}>
          <div className="hologram-effect"></div>
          <div className="card-header">
            <h3 className="card-title">Financial Performance</h3>
            <div className="card-icon">📈</div>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                MRR
              </div>
              <div style={{ fontSize: '1.5rem', color: 'var(--gold-color)', fontWeight: 'bold' }}>
                $847K
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--accent-color)' }}>
                +34% YoY
              </div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                ARR
              </div>
              <div style={{ fontSize: '1.5rem', color: 'var(--gold-color)', fontWeight: 'bold' }}>
                $10.2M
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--accent-color)' }}>
                +41% YoY
              </div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                Gross Margin
              </div>
              <div style={{ fontSize: '1.5rem', color: 'var(--gold-color)', fontWeight: 'bold' }}>
                87%
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--accent-color)' }}>
                +5% YoY
              </div>
            </div>
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

      {/* Premium Control Panel */}
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
            <span>Export Reports</span>
          </button>
          <button className="cyber-button">
            <span>Investor Portal</span>
          </button>
        </div>
      </div>

      {/* Footer Status */}
      <footer className="dashboard-header" style={{ marginTop: '2rem' }}>
        <div className="hologram-effect"></div>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          flexWrap: 'wrap', 
          gap: '1rem' 
        }}>
          <div className="status-indicator status-online">
            <span className="status-dot"></span>
            System Status: OPERATIONAL
          </div>
          <div className="status-indicator status-online">
            <span className="status-dot"></span>
            Network: SECURE
          </div>
          <div className="status-indicator status-online">
            <span className="status-dot"></span>
            AI Core: ACTIVE
          </div>
          <div style={{ 
            fontFamily: 'Orbitron, monospace', 
            color: 'var(--gold-color)',
            textShadow: 'var(--profit-glow)',
            fontSize: '0.8rem'
          }}>
            VALTRONICS v2.0 - INVESTOR READY
          </div>
        </div>
      </footer>
    </div>
  );
};

export default InvestorThesisDashboard;
