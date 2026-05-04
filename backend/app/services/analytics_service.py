from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from app.models.device import Device, TelemetryData
from app.models.alert import Alert
from app.services.device_service import DeviceService, TelemetryService

class AnalyticsService:
    
    @staticmethod
    def get_device_analytics(db: Session, device_id: int, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive analytics for a specific device"""
        device = DeviceService.get_device(db, device_id)
        if not device:
            return None
        
        # Get telemetry data
        telemetry = TelemetryService.get_device_telemetry(db, device_id, limit=1000, hours=hours)
        
        # Calculate metrics
        analytics = {
            "device_info": {
                "id": device.id,
                "name": device.name,
                "device_type": device.device_type,
                "status": device.status,
                "location": device.location
            },
            "telemetry_summary": AnalyticsService._summarize_telemetry(telemetry),
            "performance_metrics": AnalyticsService._calculate_performance_metrics(telemetry),
            "anomalies": AnalyticsService._detect_anomalies(telemetry),
            "trends": AnalyticsService._calculate_trends(telemetry),
            "data_quality": AnalyticsService._assess_data_quality(telemetry, hours)
        }
        
        return analytics
    
    @staticmethod
    def get_system_analytics(db: Session, hours: int = 24) -> Dict[str, Any]:
        """Get system-wide analytics"""
        # Get all devices
        devices = DeviceService.get_devices(db, limit=1000)
        
        # System statistics
        stats = DeviceService.get_device_stats(db)
        
        # Get recent telemetry for all devices
        recent_telemetry = []
        for device in devices:
            device_telemetry = TelemetryService.get_device_telemetry(db, device.id, limit=100, hours=hours)
            for data in device_telemetry:
                recent_telemetry.append({
                    "device_id": device.id,
                    "device_name": device.name,
                    "device_type": device.device_type,
                    **data.__dict__
                })
        
        # System-wide metrics
        analytics = {
            "system_stats": stats,
            "device_performance": AnalyticsService._analyze_device_performance(db, devices),
            "telemetry_overview": AnalyticsService._summarize_system_telemetry(recent_telemetry),
            "system_health": AnalyticsService._calculate_system_health(stats, recent_telemetry),
            "utilization_trends": AnalyticsService._calculate_utilization_trends(recent_telemetry),
            "alert_summary": AnalyticsService._get_alert_summary(db, hours)
        }
        
        return analytics
    
    @staticmethod
    def get_time_series_data(db: Session, device_id: int, metric: str, hours: int = 24) -> List[Dict]:
        """Get time series data for a specific metric"""
        telemetry = TelemetryService.get_device_telemetry(db, device_id, limit=500, hours=hours)
        
        # Filter by metric and sort by timestamp
        metric_data = [
            {
                "timestamp": t.timestamp.isoformat(),
                "value": t.metric_value,
                "unit": t.unit
            }
            for t in telemetry if t.metric_name == metric
        ]
        
        return sorted(metric_data, key=lambda x: x["timestamp"])
    
    @staticmethod
    def get_comparison_data(db: Session, device_ids: List[int], metric: str, hours: int = 24) -> Dict[str, List]:
        """Compare metrics across multiple devices"""
        comparison = {}
        
        for device_id in device_ids:
            device = DeviceService.get_device(db, device_id)
            if device:
                time_series = AnalyticsService.get_time_series_data(db, device_id, metric, hours)
                comparison[device.name] = time_series
        
        return comparison
    
    @staticmethod
    def _summarize_telemetry(telemetry: List[TelemetryData]) -> Dict[str, Any]:
        """Summarize telemetry data"""
        if not telemetry:
            return {"total_points": 0, "metrics": {}}
        
        # Group by metric name
        metrics = {}
        for data in telemetry:
            metric_name = data.metric_name
            if metric_name not in metrics:
                metrics[metric_name] = []
            metrics[metric_name].append(data.metric_value)
        
        # Calculate statistics for each metric
        summary = {"total_points": len(telemetry), "metrics": {}}
        for metric_name, values in metrics.items():
            if values:
                summary["metrics"][metric_name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "latest": values[-1] if values else None,
                    "unit": next((t.unit for t in telemetry if t.metric_name == metric_name), None)
                }
        
        return summary
    
    @staticmethod
    def _calculate_performance_metrics(telemetry: List[TelemetryData]) -> Dict[str, Any]:
        """Calculate performance metrics"""
        if not telemetry:
            return {"score": 0, "factors": []}
        
        # Data frequency (points per hour)
        if telemetry:
            time_span = (telemetry[-1].timestamp - telemetry[0].timestamp).total_seconds() / 3600
            data_frequency = len(telemetry) / max(time_span, 1)
        else:
            data_frequency = 0
        
        # Data consistency (how regular is the data)
        consistency_score = min(data_frequency / 10, 1.0)  # Expecting ~10 points per hour
        
        # Data quality (no missing values, reasonable ranges)
        quality_score = 0.9  # Simplified - would check for outliers, missing data, etc.
        
        # Overall performance score
        performance_score = (consistency_score + quality_score) / 2
        
        return {
            "score": performance_score,
            "data_frequency": data_frequency,
            "consistency_score": consistency_score,
            "quality_score": quality_score,
            "factors": [
                f"Data frequency: {data_frequency:.1f} points/hour",
                f"Consistency: {consistency_score:.2f}",
                f"Quality: {quality_score:.2f}"
            ]
        }
    
    @staticmethod
    def _detect_anomalies(telemetry: List[TelemetryData]) -> List[Dict[str, Any]]:
        """Detect anomalies in telemetry data"""
        anomalies = []
        
        # Group by metric
        metrics = {}
        for data in telemetry:
            if data.metric_name not in metrics:
                metrics[data.metric_name] = []
            metrics[data.metric_name].append(data)
        
        # Detect anomalies for each metric
        for metric_name, data_points in metrics.items():
            if len(data_points) < 10:  # Need enough data points
                continue
            
            values = [d.metric_value for d in data_points]
            mean = np.mean(values)
            std = np.std(values)
            
            # Find outliers (more than 2 standard deviations)
            for data_point in data_points:
                z_score = abs(data_point.metric_value - mean) / std if std > 0 else 0
                if z_score > 2:
                    anomalies.append({
                        "metric": metric_name,
                        "value": data_point.metric_value,
                        "expected_range": [mean - 2*std, mean + 2*std],
                        "timestamp": data_point.timestamp.isoformat(),
                        "severity": "high" if z_score > 3 else "medium",
                        "z_score": z_score
                    })
        
        return anomalies
    
    @staticmethod
    def _calculate_trends(telemetry: List[TelemetryData]) -> Dict[str, Any]:
        """Calculate trends in telemetry data"""
        trends = {}
        
        # Group by metric
        metrics = {}
        for data in telemetry:
            if data.metric_name not in metrics:
                metrics[data.metric_name] = []
            metrics[data.metric_name].append(data)
        
        # Calculate trend for each metric
        for metric_name, data_points in metrics.items():
            if len(data_points) < 5:
                continue
            
            # Sort by timestamp
            data_points.sort(key=lambda x: x.timestamp)
            values = [d.metric_value for d in data_points]
            
            # Simple linear regression to detect trend
            x = np.arange(len(values))
            if len(values) > 1:
                slope, intercept = np.polyfit(x, values, 1)
                
                # Determine trend direction
                if abs(slope) < 0.01:
                    trend_direction = "stable"
                elif slope > 0:
                    trend_direction = "increasing"
                else:
                    trend_direction = "decreasing"
                
                trends[metric_name] = {
                    "direction": trend_direction,
                    "slope": slope,
                    "strength": abs(slope) / (np.std(values) if np.std(values) > 0 else 1),
                    "recent_change": (values[-1] - values[0]) / values[0] * 100 if values[0] != 0 else 0
                }
        
        return trends
    
    @staticmethod
    def _assess_data_quality(telemetry: List[TelemetryData], hours: int) -> Dict[str, Any]:
        """Assess the quality of telemetry data"""
        if not telemetry:
            return {"score": 0, "issues": ["No data available"]}
        
        issues = []
        
        # Check data frequency
        expected_points = hours * 4  # Expecting ~4 points per hour
        actual_points = len(telemetry)
        
        if actual_points < expected_points * 0.5:
            issues.append(f"Low data frequency: {actual_points} points in {hours} hours")
        
        # Check for gaps in data
        if len(telemetry) > 1:
            time_gaps = []
            for i in range(1, len(telemetry)):
                gap = (telemetry[i].timestamp - telemetry[i-1].timestamp).total_seconds() / 3600
                if gap > 2:  # Gap of more than 2 hours
                    time_gaps.append(gap)
            
            if time_gaps:
                issues.append(f"Data gaps detected: {len(time_gaps)} gaps > 2 hours")
        
        # Calculate quality score
        quality_score = max(0, 1.0 - len(issues) * 0.2)
        
        return {
            "score": quality_score,
            "issues": issues,
            "data_points": actual_points,
            "expected_points": expected_points,
            "coverage": actual_points / expected_points if expected_points > 0 else 0
        }
    
    @staticmethod
    def _analyze_device_performance(db: Session, devices: List[Device]) -> List[Dict[str, Any]]:
        """Analyze performance across all devices"""
        performance = []
        
        for device in devices:
            # Get recent telemetry
            recent_telemetry = TelemetryService.get_device_telemetry(db, device.id, limit=50, hours=24)
            
            # Calculate performance metrics
            device_performance = {
                "device_id": device.id,
                "device_name": device.name,
                "device_type": device.device_type,
                "status": device.status,
                "data_points_24h": len(recent_telemetry),
                "last_seen": device.last_seen.isoformat() if device.last_seen else None,
                "uptime_percentage": AnalyticsService._calculate_uptime(device, recent_telemetry)
            }
            
            performance.append(device_performance)
        
        return performance
    
    @staticmethod
    def _summarize_system_telemetry(telemetry: List[Dict]) -> Dict[str, Any]:
        """Summarize telemetry across the system"""
        if not telemetry:
            return {"total_points": 0, "metrics": {}}
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(telemetry)
        
        summary = {
            "total_points": len(telemetry),
            "active_devices": len(df["device_id"].unique()),
            "device_types": df["device_type"].value_counts().to_dict(),
            "metrics": {}
        }
        
        # Summarize each metric
        for metric_name in df["metric_name"].unique():
            metric_data = df[df["metric_name"] == metric_name]["metric_value"]
            summary["metrics"][metric_name] = {
                "count": len(metric_data),
                "min": metric_data.min(),
                "max": metric_data.max(),
                "avg": metric_data.mean(),
                "std": metric_data.std()
            }
        
        return summary
    
    @staticmethod
    def _calculate_system_health(stats: Dict, telemetry: List[Dict]) -> Dict[str, Any]:
        """Calculate overall system health"""
        total_devices = stats.get("total_devices", 0)
        online_devices = stats.get("online_devices", 0)
        error_devices = stats.get("error_devices", 0)
        
        # Device health score
        device_health = online_devices / total_devices if total_devices > 0 else 0
        
        # Data health score (based on recent telemetry)
        expected_data_points = total_devices * 96  # 4 points per hour for 24 hours
        actual_data_points = len(telemetry)
        data_health = min(actual_data_points / expected_data_points, 1.0) if expected_data_points > 0 else 0
        
        # Overall health score
        overall_health = (device_health * 0.7 + data_health * 0.3)
        
        return {
            "overall_score": overall_health,
            "device_health": device_health,
            "data_health": data_health,
            "status": "healthy" if overall_health > 0.8 else "warning" if overall_health > 0.6 else "critical"
        }
    
    @staticmethod
    def _calculate_utilization_trends(telemetry: List[Dict]) -> Dict[str, Any]:
        """Calculate utilization trends"""
        if not telemetry:
            return {"trend": "stable", "utilization": 0}
        
        df = pd.DataFrame(telemetry)
        
        # Group by hour to see utilization over time
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
        hourly_counts = df.groupby("hour").size()
        
        # Calculate trend
        if len(hourly_counts) > 1:
            x = np.arange(len(hourly_counts))
            slope, _ = np.polyfit(x, hourly_counts.values, 1)
            
            if abs(slope) < 0.1:
                trend = "stable"
            elif slope > 0:
                trend = "increasing"
            else:
                trend = "decreasing"
        else:
            trend = "stable"
        
        # Current utilization (data points per hour)
        current_utilization = hourly_counts.mean() if len(hourly_counts) > 0 else 0
        
        return {
            "trend": trend,
            "current_utilization": current_utilization,
            "hourly_distribution": hourly_counts.to_dict()
        }
    
    @staticmethod
    def _get_alert_summary(db: Session, hours: int) -> Dict[str, Any]:
        """Get alert summary for the system"""
        # This would query alerts from the database
        # For now, return a placeholder
        return {
            "total_alerts": 0,
            "critical_alerts": 0,
            "warning_alerts": 0,
            "info_alerts": 0,
            "recent_alerts": []
        }
    
    @staticmethod
    def _calculate_uptime(device: Device, telemetry: List[TelemetryData]) -> float:
        """Calculate device uptime percentage"""
        if not telemetry:
            return 0.0
        
        # Simple uptime calculation based on recent data
        # In a real implementation, this would be more sophisticated
        recent_hours = 24
        expected_points = recent_hours * 4  # Expecting 4 points per hour
        actual_points = len(telemetry)
        
        return min(actual_points / expected_points, 1.0) if expected_points > 0 else 0.0
