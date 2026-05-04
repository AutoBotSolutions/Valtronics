# Troubleshooting Guide

**Comprehensive troubleshooting guide for the Valtronics system**

---

## Overview

This guide provides solutions to common issues that may arise during installation, configuration, and operation of the Valtronics system. Issues are categorized by component and severity level.

---

## Quick Diagnosis Checklist

### System Health Check
```bash
# Check if all services are running
curl http://localhost:8000/api/v1/health/

# Expected response:
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "api": "healthy"
  }
}
```

### Common Issues Checklist
- [ ] Backend server is running on port 8000
- [ ] Frontend application is running on port 3000
- [ ] Database is accessible and responsive
- [ ] All environment variables are set correctly
- [ ] Network connectivity between components
- [ ] Sufficient system resources (CPU, RAM, disk)

---

## Backend Issues

### 1. Backend Fails to Start

#### Symptoms
- Backend server crashes immediately
- Error messages about missing dependencies
- Port already in use errors

#### Solutions

**Missing Dependencies**
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check for missing packages
pip list | grep -E "(fastapi|uvicorn|sqlalchemy)"
```

**Port Conflicts**
```bash
# Check what's using port 8000
netstat -tulpn | grep :8000
lsof -i :8000

# Kill the process using the port
sudo kill -9 <PID>

# Or use a different port
python main_sqlite.py --port 8001
```

**Database Connection Issues**
```bash
# Check database file permissions
ls -la valtronics.db

# Test database connection
python -c "from app.db.session_sqlite import engine; print(engine.execute('SELECT 1').scalar())"

# Reinitialize database
python init_database.py
```

### 2. API Returns 500 Errors

#### Symptoms
- API endpoints return internal server errors
- Logs show database or application errors
- Frontend shows "Something went wrong"

#### Solutions

**Check Application Logs**
```bash
# Run backend with verbose logging
python main_sqlite.py --log-level DEBUG

# Check specific error in logs
tail -f logs/valtronics.log | grep ERROR
```

**Database Issues**
```bash
# Check database integrity
sqlite3 valtronics.db "PRAGMA integrity_check;"

# Recreate database if corrupted
rm valtronics.db
python init_database.py
python create_sample_data.py
```

**Environment Variables**
```bash
# Check environment variables
env | grep -E "(DATABASE_URL|SECRET_KEY|API_V1_STR)"

# Reset to defaults
cp .env.example .env
# Edit .env with correct values
```

### 3. Slow API Performance

#### Symptoms
- API responses take several seconds
- Database queries are slow
- High CPU usage

#### Solutions

**Database Optimization**
```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Add missing indexes
CREATE INDEX CONCURRENTLY idx_telemetry_device_time 
ON telemetry_data(device_id, timestamp DESC);
```

**Application Optimization**
```python
# Add database connection pooling
from sqlalchemy import create_engine
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30
)

# Enable query caching
from sqlalchemy.orm import sessionmaker
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
```

---

## Frontend Issues

### 1. Frontend Fails to Load

#### Symptoms
- Blank white screen
- "Cannot GET /" error
- Build compilation errors

#### Solutions

**Node.js Issues**
```bash
# Check Node.js version
node --version  # Should be 16+
npm --version   # Should be 7+

# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Build Errors**
```bash
# Check for syntax errors
npm run build

# Fix common issues
npm audit fix
npm install --legacy-peer-deps
```

**Environment Variables**
```bash
# Check frontend environment
cat .env

# Verify API URL is correct
echo $REACT_APP_API_URL
```

### 2. API Connection Errors

#### Symptoms
- "Network Error" messages
- CORS errors in browser console
- 404 errors for API calls

#### Solutions

**CORS Issues**
```python
# Check backend CORS configuration
# in app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**API URL Configuration**
```bash
# Check frontend API URL
grep REACT_APP_API_URL .env

# Test API directly
curl http://localhost:8000/api/v1/health/
```

**Proxy Configuration**
```javascript
// vite.config.js
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
});
```

### 3. Real-time Updates Not Working

#### Symptoms
- WebSocket connection failures
- Data not updating in real-time
- Connection timeout errors

#### Solutions

**WebSocket Connection**
```javascript
// Check WebSocket URL
const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
console.log('Connecting to:', wsUrl);

// Test connection
const ws = new WebSocket(wsUrl);
ws.onopen = () => console.log('WebSocket connected');
ws.onerror = (error) => console.error('WebSocket error:', error);
```

**Backend WebSocket Handler**
```python
# Check WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection accepted")
```

**Network Issues**
```bash
# Check if WebSocket port is open
telnet localhost 8000

# Test WebSocket connection
wscat -c ws://localhost:8000/ws
```

---

## Database Issues

### 1. Database Connection Errors

#### Symptoms
- "Database connection failed" errors
- SQLite "database is locked" errors
- PostgreSQL "connection refused" errors

#### Solutions

**SQLite Issues**
```bash
# Check database file permissions
ls -la valtronics.db

# Fix permissions if needed
chmod 664 valtronics.db

# Check for locks
fuser valtronics.db

# Remove lock files
rm valtronics.db-journal valtronics.db-wal
```

**PostgreSQL Issues**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start PostgreSQL service
sudo systemctl start postgresql

# Test connection
psql -h localhost -U valtronics_user -d valtronics

# Check connection limits
SELECT * FROM pg_settings WHERE name LIKE 'max_connections%';
```

### 2. Slow Database Performance

#### Symptoms
- Queries taking several seconds
- High CPU usage on database server
- Timeouts in API responses

#### Solutions

**Query Optimization**
```sql
-- Analyze slow queries
EXPLAIN ANALYZE SELECT * FROM devices WHERE status = 'online';

-- Add missing indexes
CREATE INDEX CONCURRENTLY idx_devices_status ON devices(status);

-- Update statistics
ANALYZE devices;
```

**Connection Pooling**
```python
# Configure connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
);
```

**Data Cleanup**
```bash
# Clean old telemetry data
python scripts/cleanup_old_data.py --days 30

# Archive old data
python scripts/archive_data.py --table telemetry_data --before "2024-01-01"
```

---

## Device and Telemetry Issues

### 1. Devices Not Receiving Data

#### Symptoms
- Device status shows "offline"
- No recent telemetry data
- Last seen timestamp is old

#### Solutions

**Device Connectivity**
```bash
# Check if device is sending data
tail -f logs/device_connections.log | grep "DEVICE-001"

# Test device connection
telnet <device-ip> 1883  # For MQTT devices
```

**Data Processing**
```python
# Check telemetry processing
from app.services.telemetry_service import process_telemetry
# Test with sample data
sample_data = {
    "device_id": "DEVICE-001",
    "metric_name": "temperature",
    "metric_value": 23.5,
    "unit": "°C"
}
process_telemetry(sample_data)
```

**Alert Rules**
```bash
# Check alert rules
curl http://localhost:8000/api/v1/alerts/rules/

# Test alert generation
curl -X POST http://localhost:8000/api/v1/telemetry/ \
  -H "Content-Type: application/json" \
  -d '{"device_id": 1, "metric_name": "temperature", "metric_value": 35.0}'
```

### 2. Incorrect Alert Generation

#### Symptoms
- Alerts not triggering when expected
- False positive alerts
- Alert rules not working

#### Solutions

**Alert Rule Configuration**
```bash
# Check alert rule configuration
curl http://localhost:8000/api/v1/alerts/rules/1

# Test alert rule manually
curl -X POST http://localhost:8000/api/v1/alerts/test-rule/1 \
  -H "Content-Type: application/json" \
  -d '{"metric_value": 35.0}'
```

**Threshold Values**
```sql
-- Check current thresholds
SELECT name, threshold_value, condition, metric_name 
FROM alert_rules 
WHERE is_active = true;

-- Update incorrect thresholds
UPDATE alert_rules 
SET threshold_value = 30.0 
WHERE name = 'High Temperature Alert';
```

---

## Security Issues

### 1. Authentication Failures

#### Symptoms
- Login failures with correct credentials
- Token expiration errors
- Permission denied errors

#### Solutions

**JWT Token Issues**
```bash
# Check JWT secret
grep SECRET_KEY .env

# Reset user password
python scripts/reset_user_password.py --username admin --password newpassword

# Check token expiration
grep ACCESS_TOKEN_EXPIRE_MINUTES .env
```

**User Permissions**
```bash
# Check user roles
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/auth/me

# Update user role
python scripts/update_user_role.py --username user --role admin
```

### 2. CORS Errors

#### Symptoms
- CORS errors in browser console
- "Access-Control-Allow-Origin" errors
- Cross-origin request blocked

#### Solutions

**Backend CORS Configuration**
```python
# Update CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**Frontend API Configuration**
```javascript
// Ensure API URLs are correct
const API_BASE_URL = process.env.REACT_APP_API_URL;
console.log('API URL:', API_BASE_URL);
```

---

## Performance Issues

### 1. High Memory Usage

#### Symptoms
- System running out of memory
- Application crashes
- Slow response times

#### Solutions

**Memory Leaks**
```python
# Check for memory leaks
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
```

**Database Memory**
```sql
-- Check database memory usage
SELECT datname, numbackends, xact_commit, xact_rollback, 
       blks_read, blks_hit, tup_returned, tup_fetched
FROM pg_stat_database WHERE datname = 'valtronics';
```

**Application Optimization**
```python
# Use generators for large datasets
def get_telemetry_stream(device_id, limit=1000):
    offset = 0
    while True:
        data = db.query(TelemetryData).filter(
            TelemetryData.device_id == device_id
        ).offset(offset).limit(limit).all()
        if not data:
            break
        yield data
        offset += limit
```

### 2. High CPU Usage

#### Symptoms
- CPU usage consistently above 80%
- Slow application response
- System overheating

#### Solutions

**Process Monitoring**
```bash
# Check CPU usage by process
top -p $(pgrep -f "python main_sqlite.py")
htop

# Check database queries
SELECT pid, query, state 
FROM pg_stat_activity 
WHERE state = 'active';
```

**Query Optimization**
```sql
-- Identify slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Optimize with indexes
EXPLAIN ANALYZE SELECT * FROM telemetry_data 
WHERE device_id = 1 AND timestamp > NOW() - INTERVAL '1 hour';
```

---

## Network Issues

### 1. Connection Timeouts

#### Symptoms
- "Connection timeout" errors
- "Network unreachable" errors
- Intermittent connectivity

#### Solutions

**Network Diagnostics**
```bash
# Test connectivity
ping localhost
telnet localhost 8000
nc -zv localhost 8000

# Check firewall status
sudo ufw status
sudo iptables -L
```

**Timeout Configuration**
```python
# Adjust timeout settings
import httpx

client = httpx.Client(timeout=30.0)  # 30 second timeout
```

### 2. Port Conflicts

#### Symptoms
- "Address already in use" errors
- Services failing to start
- Port binding errors

#### Solutions

**Port Identification**
```bash
# Find what's using the port
netstat -tulpn | grep :8000
lsof -i :8000
ss -tulpn | grep :8000
```

**Port Resolution**
```bash
# Kill the process
sudo kill -9 <PID>

# Or use a different port
export PORT=8001
python main_sqlite.py --port 8001
```

---

## Environment-Specific Issues

### Development Environment

#### Common Issues
- SQLite database corruption
- Hot reload not working
- Environment variables not loading

#### Solutions
```bash
# Reset development database
rm valtronics.db
python init_database.py
python create_sample_data.py

# Check environment variables
python -c "import os; print(os.getenv('DATABASE_URL'))"

# Restart development servers
pkill -f "python main_sqlite.py"
pkill -f "npm start"
```

### Production Environment

#### Common Issues
- PostgreSQL connection issues
- SSL certificate errors
- Load balancer misconfiguration

#### Solutions
```bash
# Check PostgreSQL status
sudo systemctl status postgresql
sudo tail -f /var/log/postgresql/postgresql-14-main.log

# Check SSL certificates
openssl x509 -in /path/to/cert.pem -text -noout

# Test load balancer
curl -H "Host: yourdomain.com" http://localhost/api/v1/health/
```

---

## Recovery Procedures

### Database Recovery

#### SQLite Recovery
```bash
# Check database integrity
sqlite3 valtronics.db ".schema"
sqlite3 valtronics.db "PRAGMA integrity_check;"

# Recover from backup
cp /backups/valtronics_backup_latest.sql.gz .
gunzip valtronics_backup_latest.sql.gz
sqlite3 valtronics.db < valtronics_backup_latest.sql
```

#### PostgreSQL Recovery
```bash
# Restore from backup
pg_restore -U valtronics_user -d valtronics backup_file.dump

# Point-in-time recovery
pg_basebackup -h localhost -D /backup/base -U valtronics_user -v -P
```

### Application Recovery

#### Full System Reset
```bash
# Stop all services
pkill -f "python main_sqlite.py"
pkill -f "npm start"

# Clear caches
rm -rf node_modules/.cache
pip cache purge

# Reset database
rm valtronics.db
python init_database.py
python create_sample_data.py

# Restart services
python main_sqlite.py &
npm start
```

---

## Monitoring and Diagnostics

### Health Monitoring
```bash
# System health check script
#!/bin/bash
echo "=== Valtronics Health Check ==="

# Check backend
if curl -s http://localhost:8000/api/v1/health/ > /dev/null; then
    echo "✅ Backend: Healthy"
else
    echo "❌ Backend: Unhealthy"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend: Healthy"
else
    echo "❌ Frontend: Unhealthy"
fi

# Check database
if python -c "from app.db.session_sqlite import engine; engine.execute('SELECT 1')" 2>/dev/null; then
    echo "✅ Database: Healthy"
else
    echo "❌ Database: Unhealthy"
fi

echo "=== End Health Check ==="
```

### Log Analysis
```bash
# Analyze application logs
tail -f logs/valtronics.log | grep -E "(ERROR|WARNING)"

# Database query analysis
tail -f logs/postgresql.log | grep -E "(ERROR|FATAL)"

# System resource monitoring
watch -n 5 'ps aux | grep -E "(python|node)" | head -10'
```

---

## Prevention and Best Practices

### Regular Maintenance
```bash
# Weekly maintenance script
#!/bin/bash

# Clean old logs
find logs/ -name "*.log" -mtime +7 -delete

# Optimize database
sqlite3 valtronics.db "VACUUM;"
psql -U valtronics_user -d valtronics -c "VACUUM ANALYZE;"

# Update dependencies
pip install --upgrade -r requirements.txt
npm update

# Health check
./health_check.sh
```

### Monitoring Setup
```bash
# Install monitoring tools
pip install prometheus-client grafana-api

# Set up metrics collection
# (Add Prometheus metrics to application)

# Configure alerts
# (Set up Grafana alerts for system health)
```

---

## Support Resources

### Documentation
- [Installation Guide](../01-getting-started/installation.md)
- [API Documentation](../03-api/api-overview.md)
- [Database Documentation](../05-database/database-overview.md)

### Community Support
- [GitHub Issues] (coming soon)
- [Community Forum] (coming soon)
- [Discord Server] (coming soon)

### Professional Support
- **Email**: autobotsolution@gmail.com
- **Phone**: [Available upon request]
- **Support Portal**: [Coming soon]

### Emergency Contacts
- **Critical Issues**: autobotsolution@gmail.com
- **Security Issues**: security@valtronics.com
- **Sales Inquiries**: sales@valtronics.com

---

## Escalation Procedures

### Level 1: Self-Service
1. Check this troubleshooting guide
2. Review relevant documentation
3. Try common solutions
4. Check system logs

### Level 2: Community Support
1. Post issue on community forum
2. Search existing issues
3. Engage with community
4. Wait for community response

### Level 3: Professional Support
1. Contact support email
2. Provide detailed issue description
3. Include system logs and configuration
4. Follow support team instructions

### Level 4: Emergency Support
1. Use emergency contact method
2. Provide immediate impact assessment
3. Follow emergency procedures
4. Escalate to development team

---

**© 2024 Software Customs Auto Bot Solution. All Rights Reserved.**  
**Troubleshooting Guide v1.0**
