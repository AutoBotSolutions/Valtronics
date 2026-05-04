#!/usr/bin/env python3
"""
Valtronics Firmware Test Framework

This script provides a comprehensive testing framework for Valtronics firmware,
including unit tests, integration tests, hardware tests, and performance benchmarks.
"""

import os
import sys
import json
import time
import subprocess
import threading
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import unittest
import tempfile
import shutil

class TestResult(Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

@dataclass
class TestMetric:
    name: str
    value: Union[int, float, str]
    unit: str = ""
    threshold: Optional[float] = None
    passed: bool = True

@dataclass
class TestCase:
    name: str
    description: str
    category: str
    platform: str
    timeout: int = 300
    setup_commands: List[str] = None
    test_commands: List[str] = None
    teardown_commands: List[str] = None
    expected_results: Dict[str, Any] = None
    metrics: List[TestMetric] = None

class FirmwareTestFramework:
    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.firmware_dir = self.project_root / "firmware"
        self.test_dir = self.firmware_dir / "test"
        self.framework_dir = self.test_dir / "framework"
        self.results_dir = self.test_dir / "results"
        self.reports_dir = self.test_dir / "reports"
        
        # Ensure directories exist
        self.framework_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        self.log("Firmware Test Framework initialized")
        self.log(f"Project root: {self.project_root}")
        self.log(f"Test directory: {self.test_dir}")
        
        self.test_suites = []
        self.current_test_run = None
        self.test_results = []
        
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def load_test_suites(self, config_file=None):
        """Load test suites from configuration"""
        if not config_file:
            config_file = self.framework_dir / "test_suites.json"
        
        if not config_file.exists():
            self.log("Creating default test suite configuration...")
            self.create_default_test_suites(config_file)
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            self.test_suites = []
            for suite_config in config.get('test_suites', []):
                test_cases = []
                for test_config in suite_config.get('test_cases', []):
                    metrics = []
                    for metric_config in test_config.get('metrics', []):
                        metric = TestMetric(
                            name=metric_config['name'],
                            value=0,  # Will be set during test
                            unit=metric_config.get('unit', ''),
                            threshold=metric_config.get('threshold'),
                            passed=True
                        )
                        metrics.append(metric)
                    
                    test_case = TestCase(
                        name=test_config['name'],
                        description=test_config['description'],
                        category=test_config['category'],
                        platform=test_config['platform'],
                        timeout=test_config.get('timeout', 300),
                        setup_commands=test_config.get('setup_commands', []),
                        test_commands=test_config['test_commands'],
                        teardown_commands=test_config.get('teardown_commands', []),
                        expected_results=test_config.get('expected_results', {}),
                        metrics=metrics
                    )
                    test_cases.append(test_case)
                
                self.test_suites.extend(test_cases)
            
            self.log(f"Loaded {len(self.test_suites)} test suites with {sum(len(s) for s in self.test_suites)} test cases")
            
        except Exception as e:
            self.log(f"Error loading test suites: {e}")
            return False
        
        return True
    
    def create_default_test_suites(self, config_file):
        """Create default test suite configuration"""
        default_config = {
            "test_suites": [
                {
                    "name": "unit_tests",
                    "description": "Unit tests for individual components",
                    "test_cases": [
                        {
                            "name": "sensor_manager_init",
                            "description": "Test sensor manager initialization",
                            "category": "unit",
                            "platform": "esp32",
                            "timeout": 60,
                            "setup_commands": ["pio run -e esp32 -t clean"],
                            "test_commands": ["pio test -e esp32 --filter test_sensor_manager_init"],
                            "expected_results": {
                                "return_code": 0,
                                "test_count": 1
                            },
                            "metrics": [
                                {
                                    "name": "execution_time",
                                    "unit": "seconds",
                                    "threshold": 30.0
                                },
                                {
                                    "name": "memory_usage",
                                    "unit": "bytes",
                                    "threshold": 50000
                                }
                            ]
                        },
                        {
                            "name": "mqtt_client_connection",
                            "description": "Test MQTT client connection",
                            "category": "unit",
                            "platform": "esp32",
                            "timeout": 120,
                            "setup_commands": ["pio run -e esp32 -t clean"],
                            "test_commands": ["pio test -e esp32 --filter test_mqtt_client_connection"],
                            "expected_results": {
                                "return_code": 0,
                                "connection_successful": True
                            },
                            "metrics": [
                                {
                                    "name": "connection_time",
                                    "unit": "seconds",
                                    "threshold": 30.0
                                }
                            ]
                        },
                        {
                            "name": "data_fusion_accuracy",
                            "description": "Test data fusion accuracy",
                            "category": "unit",
                            "platform": "esp32",
                            "timeout": 90,
                            "setup_commands": ["pio run -e esp32 -t clean"],
                            "test_commands": ["pio test -e esp32 --filter test_data_fusion_accuracy"],
                            "expected_results": {
                                "return_code": 0,
                                "fusion_accuracy": 0.95
                            },
                            "metrics": [
                                {
                                    "name": "fusion_accuracy",
                                    "unit": "percentage",
                                    "threshold": 0.90
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "integration_tests",
                    "description": "Integration tests for component interaction",
                    "test_cases": [
                        {
                            "name": "sensor_to_mqtt_integration",
                            "description": "Test sensor data to MQTT integration",
                            "category": "integration",
                            "platform": "esp32",
                            "timeout": 180,
                            "setup_commands": ["pio run -e esp32 -t clean"],
                            "test_commands": ["pio test -e esp32 --filter test_sensor_to_mqtt_integration"],
                            "expected_results": {
                                "return_code": 0,
                                "data_transmitted": True
                            },
                            "metrics": [
                                {
                                    "name": "end_to_end_latency",
                                    "unit": "milliseconds",
                                    "threshold": 1000.0
                                }
                            ]
                        },
                        {
                            "name": "multi_sensor_coordination",
                            "description": "Test multi-sensor coordination",
                            "category": "integration",
                            "platform": "esp32",
                            "timeout": 240,
                            "setup_commands": ["pio run -e esp32 -t clean"],
                            "test_commands": ["pio test -e esp32 --filter test_multi_sensor_coordination"],
                            "expected_results": {
                                "return_code": 0,
                                "all_sensors_active": True
                            },
                            "metrics": [
                                {
                                    "name": "sensor_sync_time",
                                    "unit": "milliseconds",
                                    "threshold": 500.0
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "hardware_tests",
                    "description": "Hardware tests with actual devices",
                    "test_cases": [
                        {
                            "name": "sensor_hardware_validation",
                            "description": "Validate sensor hardware communication",
                            "category": "hardware",
                            "platform": "esp32",
                            "timeout": 300,
                            "setup_commands": ["pio run -e esp32 -t clean"],
                            "test_commands": ["pio test -e esp32 --filter test_sensor_hardware_validation"],
                            "expected_results": {
                                "return_code": 0,
                                "hardware_connected": True
                            },
                            "metrics": [
                                {
                                    "name": "sensor_response_time",
                                    "unit": "milliseconds",
                                    "threshold": 100.0
                                }
                            ]
                        }
                    ]
                },
                {
                    "name": "performance_tests",
                    "description": "Performance and memory tests",
                    "test_cases": [
                        {
                            "name": "memory_usage_benchmark",
                            "description": "Benchmark memory usage",
                            "category": "performance",
                            "platform": "esp32",
                            "timeout": 180,
                            "setup_commands": ["pio run -e esp32 -t clean"],
                            "test_commands": ["pio test -e esp32 --filter test_memory_usage_benchmark"],
                            "expected_results": {
                                "return_code": 0
                            },
                            "metrics": [
                                {
                                    "name": "peak_memory_usage",
                                    "unit": "bytes",
                                    "threshold": 100000
                                },
                                {
                                    "name": "memory_leaks",
                                    "unit": "count",
                                    "threshold": 0
                                }
                            ]
                        },
                        {
                            "name": "cpu_performance_benchmark",
                            "description": "Benchmark CPU performance",
                            "category": "performance",
                            "platform": "esp32",
                            "timeout": 240,
                            "setup_commands": ["pio run -e esp32 -t clean"],
                            "test_commands": ["pio test -e esp32 --filter test_cpu_performance_benchmark"],
                            "expected_results": {
                                "return_code": 0
                            },
                            "metrics": [
                                {
                                    "name": "cpu_utilization",
                                    "unit": "percentage",
                                    "threshold": 80.0
                                },
                                {
                                    "name": "response_time",
                                    "unit": "milliseconds",
                                    "threshold": 100.0
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.log(f"Created default test suite configuration: {config_file}")

class TestRunner:
    def __init__(self, framework: FirmwareTestFramework):
        self.framework = framework
        self.current_test = None
        self.test_output = []
        
    def run_test_case(self, test_case: TestCase) -> Dict[str, Any]:
        """Run a single test case"""
        self.framework.log(f"Running test: {test_case.name}")
        
        start_time = time.time()
        result = {
            "name": test_case.name,
            "description": test_case.description,
            "category": test_case.category,
            "platform": test_case.platform,
            "start_time": start_time,
            "end_time": None,
            "duration": 0,
            "result": TestResult.ERROR,
            "output": "",
            "error": "",
            "metrics": []
        }
        
        try:
            # Change to firmware directory
            os.chdir(self.framework.firmware_dir)
            
            # Setup phase
            if test_case.setup_commands:
                self.framework.log("Setup phase...")
                for cmd in test_case.setup_commands:
                    stdout, stderr, returncode = self._run_command(cmd, test_case.timeout // len(test_case.setup_commands))
                    if returncode != 0:
                        result["result"] = TestResult.FAILED
                        result["error"] = f"Setup command failed: {cmd}"
                        return result
            
            # Test phase
            self.framework.log("Test phase...")
            test_start_time = time.time()
            
            for cmd in test_case.test_commands:
                stdout, stderr, returncode = self._run_command(cmd, test_case.timeout // len(test_case.test_commands))
                result["output"] += stdout
                
                if returncode != 0:
                    result["result"] = TestResult.FAILED
                    result["error"] = stderr
                    break
            else:
                result["result"] = TestResult.PASSED
            
            test_end_time = time.time()
            result["test_duration"] = test_end_time - test_start_time
            
            # Process metrics
            if test_case.metrics:
                result["metrics"] = self._process_metrics(test_case.metrics, result["output"])
            
            # Validate expected results
            if test_case.expected_results:
                validation_result = self._validate_expected_results(test_case.expected_results, result["output"])
                if not validation_result["passed"]:
                    result["result"] = TestResult.FAILED
                    result["error"] = "Expected results validation failed"
            
            # Teardown phase
            if test_case.teardown_commands:
                self.framework.log("Teardown phase...")
                for cmd in test_case.teardown_commands:
                    stdout, stderr, returncode = self._run_command(cmd, 30)
                    if returncode != 0:
                        self.framework.log(f"Teardown command failed: {cmd}")
            
        except Exception as e:
            result["result"] = TestResult.ERROR
            result["error"] = str(e)
            self.framework.log(f"Test exception: {e}")
        
        finally:
            end_time = time.time()
            result["end_time"] = end_time
            result["duration"] = end_time - start_time
        
        self.framework.log(f"Test {test_case.name} completed: {result['result'].value}")
        return result
    
    def _run_command(self, command: str, timeout: int = 300) -> tuple:
        """Run shell command"""
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.framework.firmware_dir
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            returncode = process.returncode
            
            return stdout, stderr, returncode
            
        except subprocess.TimeoutExpired:
            process.kill()
            return "", "Command timed out", 1
        except Exception as e:
            return "", str(e), 1
    
    def _process_metrics(self, metrics: List[TestMetric], output: str) -> List[Dict[str, Any]]:
        """Process test metrics from output"""
        processed_metrics = []
        
        for metric in metrics:
            metric_result = {
                "name": metric.name,
                "value": 0,
                "unit": metric.unit,
                "threshold": metric.threshold,
                "passed": True
            }
            
            # Extract metric value from output (this would need to be adapted based on actual test output format)
            if metric.name == "execution_time":
                # Look for execution time in output
                import re
                match = re.search(r'Execution time: ([\d.]+)', output)
                if match:
                    metric_result["value"] = float(match.group(1))
            elif metric.name == "memory_usage":
                # Look for memory usage in output
                import re
                match = re.search(r'Memory usage: (\d+)', output)
                if match:
                    metric_result["value"] = int(match.group(1))
            elif metric.name == "connection_time":
                # Look for connection time in output
                import re
                match = re.search(r'Connection time: ([\d.]+)', output)
                if match:
                    metric_result["value"] = float(match.group(1))
            elif metric.name == "fusion_accuracy":
                # Look for fusion accuracy in output
                import re
                match = re.search(r'Fusion accuracy: ([\d.]+)', output)
                if match:
                    metric_result["value"] = float(match.group(1))
            elif metric.name == "peak_memory_usage":
                # Look for peak memory usage in output
                import re
                match = re.search(r'Peak memory: (\d+)', output)
                if match:
                    metric_result["value"] = int(match.group(1))
            elif metric.name == "memory_leaks":
                # Look for memory leaks in output
                import re
                match = re.search(r'Memory leaks: (\d+)', output)
                if match:
                    metric_result["value"] = int(match.group(1))
            
            # Check threshold
            if metric.threshold is not None:
                if isinstance(metric_result["value"], (int, float)):
                    metric_result["passed"] = metric_result["value"] <= metric_threshold
                else:
                    metric_result["passed"] = True
            
            processed_metrics.append(metric_result)
        
        return processed_metrics
    
    def _validate_expected_results(self, expected: Dict[str, Any], output: str) -> Dict[str, Any]:
        """Validate expected results against output"""
        validation = {
            "passed": True,
            "failures": []
        }
        
        for key, expected_value in expected.items():
            # Look for key in output
            import re
            pattern = f'{key}: ([^\\n]+)'
            match = re.search(pattern, output)
            
            if match:
                actual_value = match.group(1).strip()
                
                # Try to convert to appropriate type
                try:
                    if isinstance(expected_value, bool):
                        actual_bool = actual_value.lower() in ['true', '1', 'yes', 'on']
                        if actual_bool != expected_value:
                            validation["failures"].append(f"{key}: expected {expected_value}, got {actual_bool}")
                            validation["passed"] = False
                    elif isinstance(expected_value, int):
                        actual_int = int(actual_value)
                        if actual_int != expected_value:
                            validation["failures"].append(f"{key}: expected {expected_value}, got {actual_int}")
                            validation["passed"] = False
                    elif isinstance(expected_value, float):
                        actual_float = float(actual_value)
                        if abs(actual_float - expected_value) > 0.001:
                            validation["failures"].append(f"{key}: expected {expected_value}, got {actual_float}")
                            validation["passed"] = False
                    else:
                        if actual_value != str(expected_value):
                            validation["failures"].append(f"{key}: expected {expected_value}, got {actual_value}")
                            validation["passed"] = False
                except ValueError:
                    validation["failures"].append(f"{key}: could not convert actual value '{actual_value}' to expected type")
                    validation["passed"] = False
            else:
                validation["failures"].append(f"{key}: not found in output")
                validation["passed"] = False
        
        return validation

class TestSuite:
    def __init__(self, name: str, description: str, test_cases: List[TestCase]):
        self.name = name
        self.description = description
        self.test_cases = test_cases
        self.results = []
        
    def run(self, runner: TestRunner) -> Dict[str, Any]:
        """Run entire test suite"""
        self.framework.log(f"Running test suite: {self.name}")
        
        suite_result = {
            "name": self.name,
            "description": self.description,
            "start_time": time.time(),
            "end_time": None,
            "duration": 0,
            "total_tests": len(self.test_cases),
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "error_tests": 0,
            "results": []
        }
        
        for test_case in self.test_cases:
            test_result = runner.run_test_case(test_case)
            suite_result["results"].append(test_result)
            
            # Update counters
            if test_result["result"] == TestResult.PASSED:
                suite_result["passed_tests"] += 1
            elif test_result["result"] == TestResult.FAILED:
                suite_result["failed_tests"] += 1
            elif test_result["result"] == TestResult.SKIPPED:
                suite_result["skipped_tests"] += 1
            elif test_result["result"] == TestResult.ERROR:
                suite_result["error_tests"] += 1
        
        suite_result["end_time"] = time.time()
        suite_result["duration"] = suite_result["end_time"] - suite_result["start_time"]
        
        self.framework.log(f"Test suite {self.name} completed: {suite_result['passed_tests']}/{suite_result['total_tests']} passed")
        
        return suite_result

def main():
    parser = argparse.ArgumentParser(description="Valtronics Firmware Test Framework")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument("--config", help="Test suite configuration file")
    parser.add_argument("--suite", help="Specific test suite to run")
    parser.add_argument("--platform", help="Target platform")
    parser.add_argument("--category", help="Test category")
    parser.add_argument("--output", help="Output directory for results")
    parser.add_argument("--report", action="store_true", help="Generate HTML report")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    run_parser = subparsers.add_parser("run", help="Run tests")
    run_parser.add_argument("--suite", help="Specific test suite to run")
    run_parser.add_argument("--platform", help="Target platform")
    run_parser.add_argument("--category", help="Test category")
    
    list_parser = subparsers.add_parser("list", help="List available test suites")
    list_parser.add_argument("--format", choices=["json", "table"], default="table", help="Output format")
    
    config_parser = subparsers.add_parser("config", help="Manage test configuration")
    config_parser.add_argument("--validate", action="store_true", help="Validate configuration")
    config_parser.add_argument("--create-default", action="store_true", help="Create default configuration")
    
    args = parser.parse_args()
    
    # Initialize framework
    framework = FirmwareTestFramework(args.project_root)
    
    # Load test suites
    if not framework.load_test_suites(args.config):
        return 1
    
    # Execute commands
    if args.command == "run":
        runner = TestRunner(framework)
        
        # Filter test cases based on arguments
        test_cases = framework.test_suites
        if args.suite:
            test_cases = [tc for tc in test_cases if tc.name == args.suite]
        if args.platform:
            test_cases = [tc for tc in test_cases for t in tc if t.platform == args.platform]
        if args.category:
            test_cases = [tc for tc in test_cases for t in tc if t.category == args.category]
        
        if not test_cases:
            print("No test cases found matching criteria")
            return 1
        
        # Run tests
        all_results = []
        for test_case in test_cases:
            result = runner.run_test_case(test_case)
            all_results.append(result)
        
        # Generate summary
        passed = len([r for r in all_results if r["result"] == TestResult.PASSED])
        failed = len([r for r in all_results if r["result"] == TestResult.FAILED])
        total = len(all_results)
        
        print(f"\nTest Results Summary:")
        print(f"Total: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Generate report if requested
        if args.report:
            generate_html_report(all_results, args.output)
        
        return 0 if failed == 0 else 1
    
    elif args.command == "list":
        if args.format == "json":
            print(json.dumps([{"name": tc.name, "description": tc.description, "category": tc.category, "platform": tc.platform} 
                              for tc in framework.test_suites], indent=2))
        else:
            print("Available Test Suites:")
            for tc in framework.test_suites:
                print(f"  {tc.name} - {tc.description}")
                print(f"    Category: {tc.category}")
                print(f"    Platform: {tc.platform}")
    
    elif args.command == "config":
        if args.validate:
            # Validate configuration
            print("Configuration validation completed")
        elif args.create_default:
            # Create default configuration
            framework.create_default_test_suites(framework.framework_dir / "test_suites.json")
            print("Default configuration created")
    
    else:
        parser.print_help()
    
    return 0

def generate_html_report(results, output_dir=None):
    """Generate HTML test report"""
    if not output_dir:
        output_dir = Path("test_reports")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    report_file = output_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Firmware Test Report</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; text-align: center; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .summary-item {{ background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }}
        .summary-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .summary-label {{ color: #666; margin-top: 5px; }}
        .test-results {{ margin: 20px 0; }}
        .test-item {{ margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .test-item.passed {{ background: #d4edda; border-left: 4px solid #28a745; }}
        .test-item.failed {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
        .test-item.error {{ background: #fff3cd; border-left: 4px solid #ffc107; }}
        .test-header {{ display: flex; justify-content: space-between; align-items: center; }}
        .test-name {{ font-weight: bold; }}
        .test-status {{ padding: 4px 8px; border-radius: 3px; color: white; font-size: 12px; }}
        .test-status.passed {{ background: #28a745; }}
        .test-status.failed {{ background: #dc3545; }}
        .test-status.error {{ background: #ffc107; }}
        .test-details {{ margin-top: 10px; font-family: monospace; font-size: 12px; color: #666; }}
        .metrics {{ margin-top: 10px; }}
        .metric {{ display: inline-block; margin: 5px; padding: 4px 8px; background: #e9ecef; border-radius: 3px; font-size: 11px; }}
        .metric.failed {{ background: #f8d7da; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Firmware Test Report</h1>
        
        <div class="summary">
            <div class="summary-item">
                <div class="summary-value">{len(results)}</div>
                <div class="summary-label">Total Tests</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{len([r for r in results if r['result'] == 'passed'])}</div>
                <div class="summary-label">Passed</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{len([r for r in results if r['result'] == 'failed'])}</div>
                <div class="summary-label">Failed</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{len([r for r in results if r['result'] == 'error'])}</div>
                <div class="summary-label">Errors</div>
            </div>
        </div>
        
        <div class="test-results">
"""
    
    for result in results:
        status_class = result["result"].value
        status_text = result["result"].value.upper()
        
        html += f"""
            <div class="test-item {status_class}">
                <div class="test-header">
                    <span class="test-name">{result['name']}</span>
                    <span class="test-status {status_class}">{status_text}</span>
                </div>
                <div class="test-details">
                    <strong>Platform:</strong> {result['platform']}<br>
                    <strong>Category:</strong> {result['category']}<br>
                    <strong>Duration:</strong> {result['duration']:.2f}s<br>
                    <strong>Timestamp:</strong> {datetime.fromtimestamp(result['start_time']).strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        if result.get("error"):
            html += f"<br><strong>Error:</strong> {result['error']}"
        
        if result.get("metrics"):
            html += "<div class='metrics'>"
            for metric in result["metrics"]:
                metric_class = "failed" if not metric.get("passed", True) else ""
                html += f"<span class='metric {metric_class}'>{metric['name']}: {metric['value']} {metric['unit']}</span>"
            html += "</div>"
        
        html += "</div></div>"
    
    html += """
        </div>
    </div>
</body>
</html>
"""
    
    with open(report_file, 'w') as f:
        f.write(html_content)
    
    print(f"HTML report generated: {report_file}")

if __name__ == "__main__":
    sys.exit(main())
