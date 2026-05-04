import React, { useState, useEffect } from 'react';
import SciFiDashboard from '../components/SciFiDashboard';
import '../styles/sci-fi-dashboard.css';

const SciFiDashboardPage = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [systemTime, setSystemTime] = useState(new Date());

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 2000);

    // Update system time
    const timeInterval = setInterval(() => {
      setSystemTime(new Date());
    }, 1000);

    return () => {
      clearTimeout(timer);
      clearInterval(timeInterval);
    };
  }, []);

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
            letterSpacing: '0.1em',
            animation: 'glitchText 2s infinite'
          }}>
            Initializing Valtronics System...
          </h1>
          <p style={{ 
            fontFamily: 'Space Mono, monospace', 
            color: '#b8b8c8', 
            marginTop: '1rem',
            opacity: 0.8
          }}>
            Connecting to quantum core...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="matrix-rain"></div>
      <div className="grid-overlay"></div>
      
      {/* System Header with Time */}
      <header className="dashboard-header">
        <div className="hologram-effect"></div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 className="dashboard-title" style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>
              Valtronics Command Center
            </h1>
            <p style={{ 
              fontFamily: 'Space Mono, monospace', 
              color: '#b8b8c8', 
              fontSize: '0.9rem',
              margin: 0
            }}>
              Advanced IoT Management System v2.0
            </p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ 
              fontFamily: 'Orbitron, monospace', 
              fontSize: '1.2rem', 
              color: '#00ffff',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              {systemTime.toLocaleTimeString()}
            </div>
            <div style={{ 
              fontFamily: 'Space Mono, monospace', 
              color: '#b8b8c8', 
              fontSize: '0.8rem',
              marginTop: '0.25rem'
            }}>
              {systemTime.toLocaleDateString()}
            </div>
          </div>
        </div>
      </header>

      {/* Main Dashboard */}
      <SciFiDashboard />

      {/* System Footer */}
      <footer className="dashboard-header" style={{ marginTop: '2rem' }}>
        <div className="hologram-effect"></div>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          flexWrap: 'wrap', 
          gap: '1rem' 
        }}>
          <div style={{ fontFamily: 'Space Mono, monospace', fontSize: '0.8rem' }}>
            <span style={{ color: '#00ff41' }}>●</span> System Status: OPERATIONAL
          </div>
          <div style={{ fontFamily: 'Space Mono, monospace', fontSize: '0.8rem' }}>
            <span style={{ color: '#00ffff' }}>●</span> Network: SECURE
          </div>
          <div style={{ fontFamily: 'Space Mono, monospace', fontSize: '0.8rem' }}>
            <span style={{ color: '#ff00ff' }}>●</span> AI Core: ACTIVE
          </div>
          <div style={{ fontFamily: 'Space Mono, monospace', fontSize: '0.8rem' }}>
            <span style={{ color: '#ff6b35' }}>●</span> Warnings: 3
          </div>
        </div>
      </footer>
    </div>
  );
};

export default SciFiDashboardPage;
