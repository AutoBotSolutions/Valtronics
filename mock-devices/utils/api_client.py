"""
API Client Utilities for Mock Devices

This module provides HTTP API client functionality for mock devices.
"""

import asyncio
import json
import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime
import aiohttp
import time


class APIClient:
    """HTTP API client for Valtronics system"""
    
    def __init__(self, base_url: str = "http://localhost:8000", 
                 timeout: int = 30, retry_attempts: int = 3):
        self.base_url = base_url
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.logger = logging.getLogger("api_client")
        
        # Statistics
        self.requests_sent = 0
        self.requests_failed = 0
        self.last_activity = None
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Valtronics-Mock-Device/1.0'
        })
    
    def register_device(self, device_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Register device with Valtronics API"""
        return self._make_request('POST', '/api/v1/devices/', device_data)
    
    def update_device_status(self, device_id: int, status_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update device status"""
        return self._make_request('PATCH', f'/api/v1/devices/{device_id}/status', status_data)
    
    def send_telemetry(self, device_id: int, telemetry_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send telemetry data"""
        return self._make_request('POST', f'/api/v1/telemetry/', telemetry_data)
    
    def create_alert(self, alert_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create alert"""
        return self._make_request('POST', '/api/v1/alerts/', alert_data)
    
    def get_device(self, device_id: int) -> Optional[Dict[str, Any]]:
        """Get device information"""
        return self._make_request('GET', f'/api/v1/devices/{device_id}')
    
    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.retry_attempts):
            try:
                if method == 'GET':
                    response = self.session.get(url, timeout=self.timeout)
                elif method == 'POST':
                    response = self.session.post(url, json=data, timeout=self.timeout)
                elif method == 'PUT':
                    response = self.session.put(url, json=data, timeout=self.timeout)
                elif method == 'PATCH':
                    response = self.session.patch(url, json=data, timeout=self.timeout)
                elif method == 'DELETE':
                    response = self.session.delete(url, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                self.requests_sent += 1
                self.last_activity = datetime.utcnow()
                
                if response.status_code in [200, 201, 204]:
                    if response.status_code == 204:
                        return {"success": True}
                    return response.json()
                else:
                    self.logger.warning(f"HTTP {response.status_code}: {response.text}")
                    return None
                    
            except requests.exceptions.Timeout:
                self.logger.warning(f"Request timeout (attempt {attempt + 1}/{self.retry_attempts})")
                if attempt < self.retry_attempts - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue
            except requests.exceptions.ConnectionError:
                self.logger.warning(f"Connection error (attempt {attempt + 1}/{self.retry_attempts})")
                if attempt < self.retry_attempts - 1:
                    time.sleep(2 ** attempt)
                continue
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                break
        
        self.requests_failed += 1
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get API client statistics"""
        return {
            "requests_sent": self.requests_sent,
            "requests_failed": self.requests_failed,
            "success_rate": (self.requests_sent - self.requests_failed) / max(1, self.requests_sent),
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }


class AsyncAPIClient:
    """Asynchronous HTTP API client for mock devices"""
    
    def __init__(self, base_url: str = "http://localhost:8000", 
                 timeout: int = 30, retry_attempts: int = 3):
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.retry_attempts = retry_attempts
        self.logger = logging.getLogger("async_api_client")
        
        # Statistics
        self.requests_sent = 0
        self.requests_failed = 0
        self.last_activity = None
    
    async def register_device(self, device_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Register device with Valtronics API"""
        return await self._make_request('POST', '/api/v1/devices/', device_data)
    
    async def update_device_status(self, device_id: int, status_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update device status"""
        return await self._make_request('PATCH', f'/api/v1/devices/{device_id}/status', status_data)
    
    async def send_telemetry(self, device_id: int, telemetry_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send telemetry data"""
        return await self._make_request('POST', f'/api/v1/telemetry/', telemetry_data)
    
    async def create_alert(self, alert_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create alert"""
        return await self._make_request('POST', '/api/v1/alerts/', alert_data)
    
    async def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make asynchronous HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.retry_attempts):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    headers = {'Content-Type': 'application/json'}
                    
                    if method == 'GET':
                        async with session.get(url, headers=headers) as response:
                            return await self._process_response(response)
                    elif method == 'POST':
                        async with session.post(url, json=data, headers=headers) as response:
                            return await self._process_response(response)
                    elif method == 'PUT':
                        async with session.put(url, json=data, headers=headers) as response:
                            return await self._process_response(response)
                    elif method == 'PATCH':
                        async with session.patch(url, json=data, headers=headers) as response:
                            return await self._process_response(response)
                    elif method == 'DELETE':
                        async with session.delete(url, headers=headers) as response:
                            return await self._process_response(response)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")
                        
            except asyncio.TimeoutError:
                self.logger.warning(f"Request timeout (attempt {attempt + 1}/{self.retry_attempts})")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(2 ** attempt)
                continue
            except aiohttp.ClientError:
                self.logger.warning(f"Connection error (attempt {attempt + 1}/{self.retry_attempts})")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(2 ** attempt)
                continue
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                break
        
        self.requests_failed += 1
        return None
    
    async def _process_response(self, response) -> Optional[Dict[str, Any]]:
        """Process HTTP response"""
        self.requests_sent += 1
        self.last_activity = datetime.utcnow()
        
        if response.status in [200, 201, 204]:
            if response.status == 204:
                return {"success": True}
            return await response.json()
        else:
            self.logger.warning(f"HTTP {response.status}: {await response.text()}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get API client statistics"""
        return {
            "requests_sent": self.requests_sent,
            "requests_failed": self.requests_failed,
            "success_rate": (self.requests_sent - self.requests_failed) / max(1, self.requests_sent),
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }
