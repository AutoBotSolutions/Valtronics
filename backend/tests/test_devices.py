import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.device import Device, TelemetryData
from app.services.device_service import DeviceService, TelemetryService

class TestDeviceAPI:
    """Test device API endpoints"""
    
    def test_create_device(self, client: TestClient, sample_device_data):
        """Test creating a new device"""
        response = client.post("/api/v1/devices/", json=sample_device_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == sample_device_data["name"]
        assert data["device_id"] == sample_device_data["device_id"]
        assert data["device_type"] == sample_device_data["device_type"]
        assert "id" in data
        assert "created_at" in data
    
    def test_get_devices(self, client: TestClient, db_session: Session, sample_device_data):
        """Test getting all devices"""
        # Create a device first
        device = DeviceService.create_device(db_session, sample_device_data)
        
        response = client.get("/api/v1/devices/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(d["device_id"] == sample_device_data["device_id"] for d in data)
    
    def test_get_device_by_id(self, client: TestClient, db_session: Session, sample_device_data):
        """Test getting a specific device"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        response = client.get(f"/api/v1/devices/{device.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == device.id
        assert data["device_id"] == sample_device_data["device_id"]
    
    def test_get_device_not_found(self, client: TestClient):
        """Test getting a non-existent device"""
        response = client.get("/api/v1/devices/99999")
        assert response.status_code == 404
    
    def test_update_device(self, client: TestClient, db_session: Session, sample_device_data):
        """Test updating a device"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        update_data = {"name": "Updated Device Name", "location": "Updated Location"}
        response = client.put(f"/api/v1/devices/{device.id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Updated Device Name"
        assert data["location"] == "Updated Location"
        assert data["device_id"] == sample_device_data["device_id"]
    
    def test_delete_device(self, client: TestClient, db_session: Session, sample_device_data):
        """Test deleting a device"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        response = client.delete(f"/api/v1/devices/{device.id}")
        assert response.status_code == 204
        
        # Verify device is soft deleted
        response = client.get(f"/api/v1/devices/{device.id}")
        assert response.status_code == 404
    
    def test_get_device_stats(self, client: TestClient, db_session: Session, sample_device_data):
        """Test getting device statistics"""
        # Create multiple devices
        DeviceService.create_device(db_session, sample_device_data)
        DeviceService.create_device(db_session, {**sample_device_data, "device_id": "TEST_002", "status": "offline"})
        
        response = client.get("/api/v1/devices/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_devices" in data
        assert "online_devices" in data
        assert "offline_devices" in data
        assert "error_devices" in data
        assert data["total_devices"] >= 2
    
    def test_get_devices_by_status(self, client: TestClient, db_session: Session, sample_device_data):
        """Test getting devices filtered by status"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        response = client.get("/api/v1/devices/status/online")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert all(d["status"] == "online" for d in data)

class TestTelemetryAPI:
    """Test telemetry API endpoints"""
    
    def test_create_telemetry(self, client: TestClient, db_session: Session, sample_device_data, sample_telemetry_data):
        """Test creating telemetry data"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        telemetry_data = {**sample_telemetry_data, "device_id": device.id}
        response = client.post(f"/api/v1/devices/{device.id}/telemetry", json=telemetry_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["device_id"] == device.id
        assert data["metric_name"] == sample_telemetry_data["metric_name"]
        assert data["metric_value"] == sample_telemetry_data["metric_value"]
    
    def test_get_device_telemetry(self, client: TestClient, db_session: Session, sample_device_data, sample_telemetry_data):
        """Test getting device telemetry"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create some telemetry data
        for i in range(5):
            telemetry = TelemetryService.create_telemetry(db_session, {
                **sample_telemetry_data,
                "device_id": device.id,
                "metric_value": 20.0 + i
            })
        
        response = client.get(f"/api/v1/devices/{device.id}/telemetry")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 5
        assert all(d["device_id"] == device.id for d in data)
    
    def test_create_batch_telemetry(self, client: TestClient, db_session: Session, sample_device_data, sample_telemetry_data):
        """Test creating batch telemetry data"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        batch_data = [
            {**sample_telemetry_data, "metric_value": 20.0 + i}
            for i in range(3)
        ]
        
        response = client.post(f"/api/v1/devices/{device.id}/telemetry/batch", json=batch_data)
        assert response.status_code == 201
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

class TestDeviceCommandsAPI:
    """Test device command API endpoints"""
    
    def test_create_device_command(self, client: TestClient, db_session: Session, sample_device_data):
        """Test creating a device command"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        command_data = {
            "command": "restart",
            "parameters": {"force": True}
        }
        
        response = client.post(f"/api/v1/devices/{device.id}/commands", json=command_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["device_id"] == device.id
        assert data["command"] == command_data["command"]
        assert data["status"] == "pending"
    
    def test_get_device_commands(self, client: TestClient, db_session: Session, sample_device_data):
        """Test getting device commands"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create a command
        from app.services.device_service import DeviceCommandService
        command = DeviceCommandService.create_command(db_session, {
            "device_id": device.id,
            "command": "restart",
            "parameters": {}
        })
        
        response = client.get(f"/api/v1/devices/{device.id}/commands")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all(d["device_id"] == device.id for d in data)
    
    def test_update_command_status(self, client: TestClient, db_session: Session, sample_device_data):
        """Test updating command status"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create a command
        from app.services.device_service import DeviceCommandService
        command = DeviceCommandService.create_command(db_session, {
            "device_id": device.id,
            "command": "restart",
            "parameters": {}
        })
        
        response = client.patch(f"/api/v1/commands/{command.id}/status", json={"status": "executed"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "executed"
        assert data["executed_at"] is not None

class TestDeviceService:
    """Test device service layer"""
    
    def test_create_device_service(self, db_session: Session, sample_device_data):
        """Test device creation through service"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        assert device.name == sample_device_data["name"]
        assert device.device_id == sample_device_data["device_id"]
        assert device.status == "offline"  # Default status
        assert device.is_active is True
    
    def test_get_device_by_device_id(self, db_session: Session, sample_device_data):
        """Test getting device by device_id"""
        created_device = DeviceService.create_device(db_session, sample_device_data)
        
        retrieved_device = DeviceService.get_device_by_device_id(db_session, sample_device_data["device_id"])
        
        assert retrieved_device is not None
        assert retrieved_device.id == created_device.id
        assert retrieved_device.device_id == sample_device_data["device_id"]
    
    def test_update_device_status(self, db_session: Session, sample_device_data):
        """Test updating device status"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        updated_device = DeviceService.update_device_status(db_session, device.id, "online")
        
        assert updated_device.status == "online"
        assert updated_device.last_seen is not None
    
    def test_delete_device_service(self, db_session: Session, sample_device_data):
        """Test device deletion through service"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        success = DeviceService.delete_device(db_session, device.id)
        assert success is True
        
        # Verify device is soft deleted
        deleted_device = DeviceService.get_device(db_session, device.id)
        assert deleted_device is None
    
    def test_get_device_stats_service(self, db_session: Session, sample_device_data):
        """Test getting device statistics through service"""
        # Create devices with different statuses
        DeviceService.create_device(db_session, sample_device_data)
        DeviceService.create_device(db_session, {**sample_device_data, "device_id": "TEST_002", "status": "offline"})
        DeviceService.create_device(db_session, {**sample_device_data, "device_id": "TEST_003", "status": "error"})
        
        stats = DeviceService.get_device_stats(db_session)
        
        assert stats["total_devices"] == 3
        assert stats["online_devices"] == 1
        assert stats["offline_devices"] == 1
        assert stats["error_devices"] == 1

class TestTelemetryService:
    """Test telemetry service layer"""
    
    def test_create_telemetry_service(self, db_session: Session, sample_device_data, sample_telemetry_data):
        """Test telemetry creation through service"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        telemetry = TelemetryService.create_telemetry(db_session, {
            **sample_telemetry_data,
            "device_id": device.id
        })
        
        assert telemetry.device_id == device.id
        assert telemetry.metric_name == sample_telemetry_data["metric_name"]
        assert telemetry.metric_value == sample_telemetry_data["metric_value"]
    
    def test_get_device_telemetry_service(self, db_session: Session, sample_device_data, sample_telemetry_data):
        """Test getting device telemetry through service"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create multiple telemetry points
        for i in range(10):
            TelemetryService.create_telemetry(db_session, {
                **sample_telemetry_data,
                "device_id": device.id,
                "metric_value": 20.0 + i
            })
        
        telemetry_list = TelemetryService.get_device_telemetry(db_session, device.id, limit=5)
        
        assert len(telemetry_list) == 5
        assert all(t.device_id == device.id for t in telemetry_list)
        # Should be ordered by timestamp descending
        assert telemetry_list[0].metric_value > telemetry_list[1].metric_value
    
    def test_get_latest_telemetry_service(self, db_session: Session, sample_device_data, sample_telemetry_data):
        """Test getting latest telemetry through service"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create telemetry for multiple metrics
        metrics = ["temperature", "humidity", "pressure"]
        for metric in metrics:
            TelemetryService.create_telemetry(db_session, {
                **sample_telemetry_data,
                "device_id": device.id,
                "metric_name": metric,
                "metric_value": 20.0 + len(metrics)
            })
        
        latest_telemetry = TelemetryService.get_latest_telemetry(db_session, device.id)
        
        assert len(latest_telemetry) == len(metrics)
        assert set(t.metric_name for t in latest_telemetry) == set(metrics)
