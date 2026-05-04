import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.services.analytics_service import AnalyticsService
from app.services.device_service import DeviceService, TelemetryService
from app.models.device import Device, TelemetryData

class TestAnalyticsService:
    """Test analytics service"""
    
    def test_get_device_analytics(self, db_session: Session, sample_device_data, sample_telemetry_data):
        """Test getting device analytics"""
        # Create device
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create telemetry data
        for i in range(20):
            TelemetryService.create_telemetry(db_session, {
                **sample_telemetry_data,
                "device_id": device.id,
                "metric_value": 20.0 + i % 10,
                "timestamp": datetime.utcnow() - timedelta(minutes=i)
            })
        
        analytics = AnalyticsService.get_device_analytics(db_session, device.id, hours=24)
        
        assert analytics is not None
        assert "device_info" in analytics
        assert "telemetry_summary" in analytics
        assert "performance_metrics" in analytics
        assert "anomalies" in analytics
        assert "trends" in analytics
        assert "data_quality" in analytics
        
        # Check device info
        assert analytics["device_info"]["id"] == device.id
        assert analytics["device_info"]["name"] == sample_device_data["name"]
        
        # Check telemetry summary
        telemetry_summary = analytics["telemetry_summary"]
        assert telemetry_summary["total_points"] == 20
        assert sample_telemetry_data["metric_name"] in telemetry_summary["metrics"]
        
        # Check performance metrics
        perf_metrics = analytics["performance_metrics"]
        assert "score" in perf_metrics
        assert "data_frequency" in perf_metrics
        assert 0 <= perf_metrics["score"] <= 1
    
    def test_get_system_analytics(self, db_session: Session, sample_device_data, sample_telemetry_data):
        """Test getting system analytics"""
        # Create multiple devices
        devices = []
        for i in range(3):
            device_data = {**sample_device_data, "device_id": f"TEST_{i:03d}", "name": f"Test Device {i}"}
            device = DeviceService.create_device(db_session, device_data)
            devices.append(device)
            
            # Create telemetry for each device
            for j in range(10):
                TelemetryService.create_telemetry(db_session, {
                    **sample_telemetry_data,
                    "device_id": device.id,
                    "metric_value": 20.0 + j + i,
                    "timestamp": datetime.utcnow() - timedelta(minutes=j)
                })
        
        analytics = AnalyticsService.get_system_analytics(db_session, hours=24)
        
        assert "system_stats" in analytics
        assert "device_performance" in analytics
        assert "telemetry_overview" in analytics
        assert "system_health" in analytics
        assert "utilization_trends" in analytics
        
        # Check system stats
        system_stats = analytics["system_stats"]
        assert system_stats["total_devices"] == 3
        
        # Check device performance
        device_perf = analytics["device_performance"]
        assert len(device_perf) == 3
        assert all("device_id" in perf for perf in device_perf)
    
    def test_get_time_series_data(self, db_session: Session, sample_device_data, sample_telemetry_data):
        """Test getting time series data"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create time-ordered telemetry data
        base_time = datetime.utcnow() - timedelta(hours=2)
        for i in range(10):
            TelemetryService.create_telemetry(db_session, {
                **sample_telemetry_data,
                "device_id": device.id,
                "metric_value": 20.0 + i,
                "timestamp": base_time + timedelta(minutes=i * 12)  # Every 12 minutes
            })
        
        time_series = AnalyticsService.get_time_series_data(db_session, device.id, sample_telemetry_data["metric_name"], hours=24)
        
        assert isinstance(time_series, list)
        assert len(time_series) == 10
        assert all("timestamp" in point for point in time_series)
        assert all("value" in point for point in time_series)
        assert all("unit" in point for point in time_series)
        
        # Check chronological order
        timestamps = [datetime.fromisoformat(point["timestamp"]) for point in time_series]
        assert timestamps == sorted(timestamps)
    
    def test_get_comparison_data(self, db_session: Session, sample_device_data, sample_telemetry_data):
        """Test comparing metrics across devices"""
        # Create multiple devices
        devices = []
        for i in range(3):
            device_data = {**sample_device_data, "device_id": f"TEST_{i:03d}", "name": f"Test Device {i}"}
            device = DeviceService.create_device(db_session, device_data)
            devices.append(device)
            
            # Create telemetry with different values
            for j in range(5):
                TelemetryService.create_telemetry(db_session, {
                    **sample_telemetry_data,
                    "device_id": device.id,
                    "metric_value": 20.0 + i * 5 + j,
                    "timestamp": datetime.utcnow() - timedelta(minutes=j)
                })
        
        device_ids = [d.id for d in devices]
        comparison = AnalyticsService.get_comparison_data(db_session, device_ids, sample_telemetry_data["metric_name"], hours=24)
        
        assert isinstance(comparison, dict)
        assert len(comparison) == 3
        assert all(isinstance(data, list) for data in comparison.values())
        
        # Check that each device has data
        for device in devices:
            assert device.name in comparison
            assert len(comparison[device.name]) > 0
    
    def test_summarize_telemetry(self, db_session: Session, sample_device_data, sample_telemetry_data):
        """Test telemetry summarization"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create telemetry with known values
        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        for value in values:
            TelemetryService.create_telemetry(db_session, {
                **sample_telemetry_data,
                "device_id": device.id,
                "metric_value": value
            })
        
        telemetry_list = TelemetryService.get_device_telemetry(db_session, device.id, hours=24)
        summary = AnalyticsService._summarize_telemetry(telemetry_list)
        
        assert summary["total_points"] == 5
        assert sample_telemetry_data["metric_name"] in summary["metrics"]
        
        metric_summary = summary["metrics"][sample_telemetry_data["metric_name"]]
        assert metric_summary["min"] == min(values)
        assert metric_summary["max"] == max(values)
        assert metric_summary["avg"] == sum(values) / len(values)
        assert metric_summary["count"] == len(values)
    
    def test_detect_anomalies(self, db_session: Session, sample_device_data, sample_telemetry_data):
        """Test anomaly detection"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create normal telemetry data
        normal_values = [20.0, 21.0, 19.5, 20.5, 20.2] * 4  # 20 normal values
        for value in normal_values:
            TelemetryService.create_telemetry(db_session, {
                **sample_telemetry_data,
                "device_id": device.id,
                "metric_value": value
            })
        
        # Add anomaly values
        anomaly_values = [50.0, 5.0]  # Clear outliers
        for value in anomaly_values:
            TelemetryService.create_telemetry(db_session, {
                **sample_telemetry_data,
                "device_id": device.id,
                "metric_value": value
            })
        
        telemetry_list = TelemetryService.get_device_telemetry(db_session, device.id, hours=24)
        anomalies = AnalyticsService._detect_anomalies(telemetry_list)
        
        assert len(anomalies) >= 2  # Should detect the outliers
        assert all("metric" in anomaly for anomaly in anomalies)
        assert all("value" in anomaly for anomaly in anomalies)
        assert all("severity" in anomaly for anomaly in anomalies)
        assert all(anomaly["metric"] == sample_telemetry_data["metric_name"] for anomaly in anomalies)
    
    def test_calculate_trends(self, db_session: Session, sample_device_data, sample_telemetry_data):
        """Test trend calculation"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create telemetry with clear increasing trend
        for i in range(10):
            TelemetryService.create_telemetry(db_session, {
                **sample_telemetry_data,
                "device_id": device.id,
                "metric_value": 20.0 + i * 2,  # Increasing values
                "timestamp": datetime.utcnow() - timedelta(minutes=(10 - i))
            })
        
        telemetry_list = TelemetryService.get_device_telemetry(db_session, device.id, hours=24)
        trends = AnalyticsService._calculate_trends(telemetry_list)
        
        assert sample_telemetry_data["metric_name"] in trends
        
        trend_info = trends[sample_telemetry_data["metric_name"]]
        assert "direction" in trend_info
        assert "slope" in trend_info
        assert "strength" in trend_info
        assert "recent_change" in trend_info
        
        # Should detect increasing trend
        assert trend_info["direction"] == "increasing"
        assert trend_info["slope"] > 0
    
    def test_assess_data_quality(self, db_session: Session, sample_device_data, sample_telemetry_data):
        """Test data quality assessment"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create telemetry with good coverage (every 15 minutes for 2 hours)
        for i in range(8):
            TelemetryService.create_telemetry(db_session, {
                **sample_telemetry_data,
                "device_id": device.id,
                "metric_value": 20.0 + i,
                "timestamp": datetime.utcnow() - timedelta(minutes=i * 15)
            })
        
        telemetry_list = TelemetryService.get_device_telemetry(db_session, device.id, hours=24)
        quality = AnalyticsService._assess_data_quality(telemetry_list, hours=2)
        
        assert "score" in quality
        assert "issues" in quality
        assert "data_points" in quality
        assert "expected_points" in quality
        assert "coverage" in quality
        
        assert 0 <= quality["score"] <= 1
        assert quality["data_points"] == 8
        assert quality["coverage"] > 0  # Should have some coverage
    
    def test_calculate_device_performance(self, db_session: Session, sample_device_data, sample_telemetry_data):
        """Test device performance calculation"""
        device = DeviceService.create_device(db_session, sample_device_data)
        
        # Create recent telemetry
        for i in range(20):
            TelemetryService.create_telemetry(db_session, {
                **sample_telemetry_data,
                "device_id": device.id,
                "metric_value": 20.0 + i,
                "timestamp": datetime.utcnow() - timedelta(minutes=i)
            })
        
        telemetry_list = TelemetryService.get_device_telemetry(db_session, device.id, hours=24)
        performance = AnalyticsService._calculate_performance_metrics(telemetry_list)
        
        assert "score" in performance
        assert "data_frequency" in performance
        assert "consistency_score" in performance
        assert "quality_score" in performance
        assert "factors" in performance
        
        assert 0 <= performance["score"] <= 1
        assert performance["data_frequency"] > 0
        assert len(performance["factors"]) > 0
