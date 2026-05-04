import React, { useState, useEffect } from 'react';
import InvestorThesisDashboard from '../components/InvestorThesisDashboard';
import '../styles/sci-fi-dashboard.css';

const InvestorThesisPage = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [systemTime, setSystemTime] = useState(new Date());

  useEffect(() => {
    // Simulate loading with investor thesis styling
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
            color: 'var(--gold-color)', 
            marginTop: '2rem',
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            textShadow: 'var(--profit-glow)',
            animation: 'glitchText 2s infinite'
          }}>
            Initializing Valtronics Investor Dashboard...
          </h1>
          <p style={{ 
            fontFamily: 'Space Mono, monospace', 
            color: 'var(--text-secondary)', 
            marginTop: '1rem',
            opacity: 0.8
          }}>
            Connecting to quantum core and financial systems...
          </p>
          <div style={{ 
            marginTop: '2rem',
            fontFamily: 'Space Mono, monospace',
            color: 'var(--accent-color)',
            fontSize: '0.9rem'
          }}>
            <div>Loading market data...</div>
            <div>Initializing AI analytics...</div>
            <div>Preparing investor metrics...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="matrix-rain"></div>
      <div className="grid-overlay"></div>
      
      {/* Premium Header with Investor Thesis Styling */}
      <header className="dashboard-header">
        <div className="hologram-effect"></div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 className="dashboard-title">Valtronics Investor Command Center</h1>
            <p style={{ 
              fontFamily: 'Space Mono, monospace', 
              color: 'var(--text-secondary)', 
              fontSize: '0.9rem',
              margin: '0.5rem 0 0 0'
            }}>
              AI-Powered Intelligent Electronics Ecosystem - Real-Time Investor Analytics
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

      {/* Main Dashboard */}
      <InvestorThesisDashboard />

      {/* Investor Footer */}
      <footer className="dashboard-header" style={{ marginTop: '2rem' }}>
        <div className="hologram-effect"></div>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          flexWrap: 'wrap', 
          gap: '1rem' 
        }}>
          <div style={{ 
            fontFamily: 'Space Mono, monospace', 
            fontSize: '0.8rem',
            color: 'var(--text-secondary)'
          }}>
            <span style={{ color: 'var(--accent-color)' }}>●</span> Market Cap: $47B
          </div>
          <div style={{ 
            fontFamily: 'Space Mono, monospace', 
            fontSize: '0.8rem',
            color: 'var(--text-secondary)'
          }}>
            <span style={{ color: 'var(--gold-color)' }}>●</span> ARR: $10.2M
          </div>
          <div style={{ 
            fontFamily: 'Space Mono, monospace', 
            fontSize: '0.8rem',
            color: 'var(--text-secondary)'
          }}>
            <span style={{ color: 'var(--accent-color)' }}>●</span> Growth: 47% CAGR
          </div>
          <div style={{ 
            fontFamily: 'Orbitron, monospace', 
            color: 'var(--gold-color)',
            textShadow: 'var(--profit-glow)',
            fontSize: '0.8rem',
            fontWeight: 'bold'
          }}>
            INVESTOR READY • SCALABLE • PROFITABLE
          </div>
        </div>
      </footer>
    </div>
  );
};

export default InvestorThesisPage;
