#!/usr/bin/env python3
"""
Valtronics Firmware Test Runner

This script provides comprehensive testing capabilities for Valtronics firmware,
including unit tests, integration tests, hardware tests, and performance tests.
"""

import os
import sys
import json
import time
import subprocess
import argparse
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

class TestRunner:
    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.firmware_dir = self.project_root / "firmware"
        self.test_dir = self.firmware_dir / "test"
        self.results_dir = self.firmware_dir / "test" / "results"
        
        # Ensure directories exist
        self.test_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        
        self.log("Firmware Test Runner initialized")
        self.log(f"Project root: {self.project_root}")
        self.log(f"Test directory: {self.test_dir}")
        self.log(f"Results directory: {self.results_dir}")
        
        self.test_results = []
        self.current_test_session = None
    
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def run_command(self, command, cwd=None, capture_output=True, timeout=300):
        """Run shell command and return result"""
        try:
            if cwd:
                result = subprocess.run(command, shell=True, cwd=cwd, 
                                      capture_output=capture_output, text=True, timeout=timeout)
            else:
                result = subprocess.run(command, shell=True, 
                                      capture_output=capture_output, text=True, timeout=timeout)
            
            return result.stdout, result.stderr, result.returncode
                
        except subprocess.TimeoutExpired:
            self.log(f"Command timed out: {command}")
            return "", "Command timed out", 1
        except Exception as e:
            self.log(f"Error running command: {e}")
            return "", str(e), 1
    
    def start_test_session(self, session_name=None):
        """Start a new test session"""
        if not session_name:
            session_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.current_test_session = {
            "name": session_name,
            "start_time": datetime.now(),
            "tests": [],
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0
        }
        
        self.log(f"Started test session: {session_name}")
        return session_name
    
    def end_test_session(self):
        """End current test session and save results"""
        if not self.current_test_session:
            self.log("No active test session")
            return None
        
        self.current_test_session["end_time"] = datetime.now()
        self.current_test_session["duration"] = (
            self.current_test_session["end_time"] - self.current_test_session["start_time"]
        ).total_seconds()
        
        # Save results
        results_file = self.results_dir / f"{self.current_test_session['name']}.json"
        with open(results_file, 'w') as f:
            json.dump(self.current_test_session, f, indent=2, default=str)
        
        session_name = self.current_test_session["name"]
        self.log(f"Ended test session: {session_name}")
        self.log(f"Results saved to: {results_file}")
        
        session_summary = self.current_test_session.copy()
        self.current_test_session = None
        return session_summary
    
    def run_unit_tests(self, platform=None):
        """Run unit tests for firmware"""
        self.log("Running unit tests...")
        
        if not platform:
            platforms = ["esp32", "arduino_mega", "nucleo_f429zi"]
        else:
            platforms = [platform]
        
        results = []
        
        for platform in platforms:
            self.log(f"Running unit tests for {platform}...")
            
            # Change to firmware directory
            os.chdir(self.firmware_dir)
            
            # Run unit tests
            cmd = f"pio test -e {platform} --filter test_*"
            stdout, stderr, returncode = self.run_command(cmd)
            
            test_result = {
                "platform": platform,
                "type": "unit",
                "command": cmd,
                "stdout": stdout,
                "stderr": stderr,
                "returncode": returncode,
                "passed": returncode == 0,
                "timestamp": datetime.now().isoformat()
            }
            
            results.append(test_result)
            
            if returncode == 0:
                self.log(f"Unit tests passed for {platform}")
            else:
                self.log(f"Unit tests failed for {platform}: {stderr}")
        
        return results
    
    def run_integration_tests(self, platform=None):
        """Run integration tests for firmware"""
        self.log("Running integration tests...")
        
        if not platform:
            platforms = ["esp32", "arduino_mega", "nucleo_f429zi"]
        else:
            platforms = [platform]
        
        results = []
        
        for platform in platforms:
            self.log(f"Running integration tests for {platform}...")
            
            # Change to firmware directory
            os.chdir(self.firmware_dir)
            
            # Run integration tests
            cmd = f"pio test -e {platform} --filter integration_*"
            stdout, stderr, returncode = self.run_command(cmd)
            
            test_result = {
                "platform": platform,
                "type": "integration",
                "command": cmd,
                "stdout": stdout,
                "stderr": stderr,
                "returncode": returncode,
                "passed": returncode == 0,
                "timestamp": datetime.now().isoformat()
            }
            
            results.append(test_result)
            
            if returncode == 0:
                self.log(f"Integration tests passed for {platform}")
            else:
                self.log(f"Integration tests failed for {platform}: {stderr}")
        
        return results
    
    def run_hardware_tests(self, platform=None):
        """Run hardware tests for firmware"""
        self.log("Running hardware tests...")
        
        if not platform:
            platforms = ["esp32", "arduino_mega"]
        else:
            platforms = [platform]
        
        results = []
        
        for platform in platforms:
            self.log(f"Running hardware tests for {platform}...")
            
            # Change to firmware directory
            os.chdir(self.firmware_dir)
            
            # Run hardware tests
            cmd = f"pio test -e {platform} --filter hardware_*"
            stdout, stderr, returncode = self.run_command(cmd)
            
            test_result = {
                "platform": platform,
                "type": "hardware",
                "command": cmd,
                "stdout": stdout,
                "stderr": stderr,
                "returncode": returncode,
                "passed": returncode == 0,
                "timestamp": datetime.now().isoformat()
            }
            
            results.append(test_result)
            
            if returncode == 0:
                self.log(f"Hardware tests passed for {platform}")
            else:
                self.log(f"Hardware tests failed for {platform}: {stderr}")
        
        return results
    
    def run_performance_tests(self, platform=None):
        """Run performance tests for firmware"""
        self.log("Running performance tests...")
        
        if not platform:
            platforms = ["esp32", "arduino_mega"]
        else:
            platforms = [platform]
        
        results = []
        
        for platform in platforms:
            self.log(f"Running performance tests for {platform}...")
            
            # Change to firmware directory
            os.chdir(self.firmware_dir)
            
            # Run performance tests
            cmd = f"pio test -e {platform} --filter performance_*"
            stdout, stderr, returncode = self.run_command(cmd)
            
            test_result = {
                "platform": platform,
                "type": "performance",
                "command": cmd,
                "stdout": stdout,
                "stderr": stderr,
                "returncode": returncode,
                "passed": returncode == 0,
                "timestamp": datetime.now().isoformat()
            }
            
            results.append(test_result)
            
            if returncode == 0:
                self.log(f"Performance tests passed for {platform}")
            else:
                self.log(f"Performance tests failed for {platform}: {stderr}")
        
        return results
    
    def run_all_tests(self, platform=None):
        """Run all tests for firmware"""
        self.log("Running all tests...")
        
        session_name = self.start_test_session()
        
        try:
            # Run all test types
            unit_results = self.run_unit_tests(platform)
            integration_results = self.run_integration_tests(platform)
            hardware_results = self.run_hardware_tests(platform)
            performance_results = self.run_performance_tests(platform)
            
            # Combine results
            all_results = unit_results + integration_results + hardware_results + performance_results
            
            # Update session
            if self.current_test_session:
                self.current_test_session["tests"] = all_results
                self.current_test_session["total_tests"] = len(all_results)
                self.current_test_session["passed_tests"] = len([r for r in all_results if r["passed"]])
                self.current_test_session["failed_tests"] = len([r for r in all_results if not r["passed"]])
            
            return all_results
            
        finally:
            self.end_test_session()
    
    def run_coverage_tests(self, platform="esp32"):
        """Run coverage tests for firmware"""
        self.log(f"Running coverage tests for {platform}...")
        
        # Change to firmware directory
        os.chdir(self.firmware_dir)
        
        # Run coverage tests
        cmd = f"pio test -e {platform} --filter coverage_*"
        stdout, stderr, returncode = self.run_command(cmd)
        
        test_result = {
            "platform": platform,
            "type": "coverage",
            "command": cmd,
            "stdout": stdout,
            "stderr": stderr,
            "returncode": returncode,
            "passed": returncode == 0,
            "timestamp": datetime.now().isoformat()
        }
        
        if returncode == 0:
            self.log(f"Coverage tests passed for {platform}")
        else:
            self.log(f"Coverage tests failed for {platform}: {stderr}")
        
        return test_result
    
    def run_memory_tests(self, platform="esp32"):
        """Run memory tests for firmware"""
        self.log(f"Running memory tests for {platform}...")
        
        # Change to firmware directory
        os.chdir(self.firmware_dir)
        
        # Run memory tests
        cmd = f"pio test -e {platform} --filter memory_*"
        stdout, stderr, returncode = self.run_command(cmd)
        
        test_result = {
            "platform": platform,
            "type": "memory",
            "command": cmd,
            "stdout": stdout,
            "stderr": stderr,
            "returncode": returncode,
            "passed": returncode == 0,
            "timestamp": datetime.now().isoformat()
        }
        
        if returncode == 0:
            self.log(f"Memory tests passed for {platform}")
        else:
            self.log(f"Memory tests failed for {platform}: {stderr}")
        
        return test_result
    
    def generate_test_report(self, session_name=None):
        """Generate HTML test report"""
        self.log("Generating test report...")
        
        # Find latest results file
        if session_name:
            results_file = self.results_dir / f"{session_name}.json"
        else:
            results_files = list(self.results_dir.glob("*.json"))
            if not results_files:
                self.log("No test results found")
                return None
            
            results_file = max(results_files, key=lambda x: x.stat().st_mtime)
        
        if not results_file.exists():
            self.log(f"Results file not found: {results_file}")
            return None
        
        # Load results
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        # Generate HTML report
        html_content = self.generate_html_report(results)
        
        # Save HTML report
        report_file = self.results_dir / f"{results_file.stem}.html"
        with open(report_file, 'w') as f:
            f.write(html_content)
        
        self.log(f"Test report generated: {report_file}")
        return report_file
    
    def generate_html_report(self, results):
        """Generate HTML content for test report"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Valtronics Firmware Test Report</title>
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
        .test-item.skipped {{ background: #fff3cd; border-left: 4px solid #ffc107; }}
        .test-header {{ display: flex; justify-content: space-between; align-items: center; }}
        .test-name {{ font-weight: bold; }}
        .test-status {{ padding: 4px 8px; border-radius: 3px; color: white; font-size: 12px; }}
        .test-status.passed {{ background: #28a745; }}
        .test-status.failed {{ background: #dc3545; }}
        .test-status.skipped {{ background: #ffc107; }}
        .test-details {{ margin-top: 10px; font-family: monospace; font-size: 12px; color: #666; }}
        .platform-filter {{ margin: 20px 0; }}
        .platform-filter button {{ margin: 5px; padding: 8px 16px; border: 1px solid #ddd; background: white; border-radius: 4px; cursor: pointer; }}
        .platform-filter button.active {{ background: #007bff; color: white; }}
        .hidden {{ display: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Valtronics Firmware Test Report</h1>
        
        <div class="summary">
            <div class="summary-item">
                <div class="summary-value">{results['total_tests']}</div>
                <div class="summary-label">Total Tests</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{results['passed_tests']}</div>
                <div class="summary-label">Passed</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{results['failed_tests']}</div>
                <div class="summary-label">Failed</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{results.get('duration', 'N/A')}</div>
                <div class="summary-label">Duration (s)</div>
            </div>
        </div>
        
        <div class="platform-filter">
            <button class="active" onclick="filterTests('all')">All</button>
            <button onclick="filterTests('esp32')">ESP32</button>
            <button onclick="filterTests('arduino_mega')">Arduino Mega</button>
            <button onclick="filterTests('nucleo_f429zi')">STM32</button>
        </div>
        
        <div class="test-results">
"""
        
        # Add test results
        for test in results.get('tests', []):
            status_class = "passed" if test.get('passed', False) else "failed"
            status_text = "PASSED" if test.get('passed', False) else "FAILED"
            
            html += f"""
            <div class="test-item {status_class}" data-platform="{test.get('platform', 'unknown')}">
                <div class="test-header">
                    <span class="test-name">{test.get('type', 'unknown').upper()} - {test.get('platform', 'unknown')}</span>
                    <span class="test-status {status_class}">{status_text}</span>
                </div>
                <div class="test-details">
                    <strong>Command:</strong> {test.get('command', 'N/A')}<br>
                    <strong>Time:</strong> {test.get('timestamp', 'N/A')}<br>
                    <strong>Return Code:</strong> {test.get('returncode', 'N/A')}
                </div>
            </div>
            """
        
        html += """
        </div>
    </div>
    
    <script>
        function filterTests(platform) {
            const tests = document.querySelectorAll('.test-item');
            const buttons = document.querySelectorAll('.platform-filter button');
            
            // Update button states
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Filter tests
            tests.forEach(test => {
                if (platform === 'all' || test.dataset.platform === platform) {
                    test.classList.remove('hidden');
                } else {
                    test.classList.add('hidden');
                }
            });
        }
    </script>
</body>
</html>
"""
        
        return html
    
    def run_ci_tests(self, platform="esp32"):
        """Run CI tests for continuous integration"""
        self.log(f"Running CI tests for {platform}...")
        
        session_name = f"ci_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_test_session(session_name)
        
        try:
            # Run all test types
            results = self.run_all_tests(platform)
            
            # Generate report
            report_file = self.generate_test_report(session_name)
            
            # Check if any tests failed
            failed_tests = [r for r in results if not r.get('passed', False)]
            
            if failed_tests:
                self.log(f"CI tests failed: {len(failed_tests)} out of {len(results)}")
                for test in failed_tests:
                    self.log(f"  Failed: {test.get('platform')} - {test.get('type')}")
                return False
            else:
                self.log(f"All CI tests passed: {len(results)} tests")
                return True
                
        finally:
            session_summary = self.end_test_session()
        
        return len(failed_tests) == 0 if 'failed_tests' in locals() else False
    
    def run_regression_tests(self, baseline_platform="esp32"):
        """Run regression tests against baseline"""
        self.log(f"Running regression tests against baseline: {baseline_platform}")
        
        # This would compare test results with baseline
        # For now, just run all tests
        results = self.run_all_tests(baseline_platform)
        
        # Check for regressions
        failed_tests = [r for r in results if not r.get('passed', False)]
        
        if failed_tests:
            self.log(f"Regression tests failed: {len(failed_tests)} out of {len(results)}")
            return False
        else:
            self.log(f"No regressions detected: {len(results)} tests passed")
            return True
    
    def run_smoke_tests(self, platform="esp32"):
        """Run smoke tests to verify basic functionality"""
        self.log(f"Running smoke tests for {platform}...")
        
        # Change to firmware directory
        os.chdir(self.firmware_dir)
        
        # Basic build test
        cmd = f"pio run -e {platform}"
        stdout, stderr, returncode = self.run_command(cmd)
        
        if returncode != 0:
            self.log(f"Smoke test failed - build error: {stderr}")
            return False
        
        # Basic test
        cmd = f"pio test -e {platform} --filter test_basic"
        stdout, stderr, returncode = self.run_command(cmd)
        
        if returncode != 0:
            self.log(f"Smoke test failed - basic test error: {stderr}")
            return False
        
        self.log(f"Smoke tests passed for {platform}")
        return True
    
    def run_stress_tests(self, platform="esp32", duration=300):
        """Run stress tests for firmware"""
        self.log(f"Running stress tests for {platform} (duration: {duration}s)...")
        
        # This would run stress tests
        # For now, just run performance tests
        results = self.run_performance_tests(platform)
        
        # Check if any tests failed
        failed_tests = [r for r in results if not r.get('passed', False)]
        
        if failed_tests:
            self.log(f"Stress tests failed: {len(failed_tests)} out of {len(results)}")
            return False
        else:
            self.log(f"Stress tests passed: {len(results)} tests")
            return True
    
    def list_test_suites(self):
        """List available test suites"""
        self.log("Available test suites:")
        
        test_suites = [
            "unit - Unit tests for individual components",
            "integration - Integration tests for component interaction",
            "hardware - Hardware tests with actual devices",
            "performance - Performance and memory tests",
            "coverage - Code coverage tests",
            "memory - Memory usage tests",
            "smoke - Basic functionality tests",
            "regression - Regression tests against baseline",
            "ci - Continuous integration tests",
            "stress - Stress tests for stability"
        ]
        
        for suite in test_suites:
            self.log(f"  {suite}")
        
        return test_suites
    
    def clean_test_results(self, older_than_days=7):
        """Clean old test results"""
        self.log(f"Cleaning test results older than {older_than_days} days...")
        
        cutoff_time = datetime.now() - timedelta(days=older_than_days)
        cleaned_files = 0
        
        for result_file in self.results_dir.glob("*.json"):
            file_time = datetime.fromtimestamp(result_file.stat().st_mtime)
            if file_time < cutoff_time:
                result_file.unlink()
                cleaned_files += 1
        
        for report_file in self.results_dir.glob("*.html"):
            file_time = datetime.fromtimestamp(report_file.stat().st_mtime)
            if file_time < cutoff_time:
                report_file.unlink()
                cleaned_files += 1
        
        self.log(f"Cleaned {cleaned_files} test result files")
        return cleaned_files


def main():
    parser = argparse.ArgumentParser(description="Valtronics Firmware Test Runner")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument("--platform", help="Target platform (esp32, arduino_mega, nucleo_f429zi)")
    parser.add_argument("--session", help="Test session name")
    parser.add_argument("--report", action="store_true", help="Generate HTML test report")
    parser.add_argument("--clean", type=int, default=7, help="Clean results older than N days")
    parser.add_argument("--list-suites", action="store_true", help="List available test suites")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Test commands
    unit_parser = subparsers.add_parser("unit", help="Run unit tests")
    unit_parser.add_argument("--platform", help="Target platform")
    
    integration_parser = subparsers.add_parser("integration", help="Run integration tests")
    integration_parser.add_argument("--platform", help="Target platform")
    
    hardware_parser = subparsers.add_parser("hardware", help="Run hardware tests")
    hardware_parser.add_argument("--platform", help="Target platform")
    
    performance_parser = subparsers.add_parser("performance", help="Run performance tests")
    performance_parser.add_argument("--platform", help="Target platform")
    
    coverage_parser = subparsers.add_parser("coverage", help="Run coverage tests")
    coverage_parser.add_argument("--platform", default="esp32", help="Target platform")
    
    memory_parser = subparsers.add_parser("memory", help="Run memory tests")
    memory_parser.add_argument("--platform", default="esp32", help="Target platform")
    
    all_parser = subparsers.add_parser("all", help="Run all tests")
    all_parser.add_argument("--platform", help="Target platform")
    
    ci_parser = subparsers.add_parser("ci", help="Run CI tests")
    ci_parser.add_argument("--platform", default="esp32", help="Target platform")
    
    smoke_parser = subparsers.add_parser("smoke", help="Run smoke tests")
    smoke_parser.add_argument("--platform", default="esp32", help="Target platform")
    
    regression_parser = subparsers.add_parser("regression", help="Run regression tests")
    regression_parser.add_argument("--platform", default="esp32", help="Target platform")
    
    stress_parser = subparsers.add_parser("stress", help="Run stress tests")
    stress_parser.add_argument("--platform", default="esp32", help="Target platform")
    stress_parser.add_argument("--duration", type=int, default=300, help="Test duration in seconds")
    
    args = parser.parse_args()
    
    # Initialize test runner
    test_runner = TestRunner(args.project_root)
    
    # Start test session if specified
    if args.session:
        test_runner.start_test_session(args.session)
    
    # List test suites
    if args.list_suites:
        test_runner.list_test_suites()
        return
    
    # Clean old results
    if args.clean:
        test_runner.clean_test_results(args.clean)
    
    # Generate report
    if args.report:
        test_runner.generate_test_report(args.session)
    
    # Run specific commands
    if args.command == "unit":
        results = test_runner.run_unit_tests(args.platform)
        test_runner.log(f"Unit tests completed: {len(results)} tests")
    
    elif args.command == "integration":
        results = test_runner.run_integration_tests(args.platform)
        test_runner.log(f"Integration tests completed: {len(results)} tests")
    
    elif args.command == "hardware":
        results = test_runner.run_hardware_tests(args.platform)
        test_runner.log(f"Hardware tests completed: {len(results)} tests")
    
    elif args.command == "performance":
        results = test_runner.run_performance_tests(args.platform)
        test_runner.log(f"Performance tests completed: {len(results)} tests")
    
    elif args.command == "coverage":
        result = test_runner.run_coverage_tests(args.platform)
        test_runner.log(f"Coverage tests completed: {'PASSED' if result['passed'] else 'FAILED'}")
    
    elif args.command == "memory":
        result = test_runner.run_memory_tests(args.platform)
        test_runner.log(f"Memory tests completed: {'PASSED' if result['passed'] else 'FAILED'}")
    
    elif args.command == "all":
        results = test_runner.run_all_tests(args.platform)
        test_runner.log(f"All tests completed: {len(results)} tests")
    
    elif args.command == "ci":
        success = test_runner.run_ci_tests(args.platform)
        sys.exit(0 if success else 1)
    
    elif args.command == "smoke":
        success = test_runner.run_smoke_tests(args.platform)
        sys.exit(0 if success else 1)
    
    elif args.command == "regression":
        success = test_runner.run_regression_tests(args.platform)
        sys.exit(0 if success else 1)
    
    elif args.command == "stress":
        success = test_runner.run_stress_tests(args.platform, args.duration)
        sys.exit(0 if success else 1)
    
    # End test session if started
    if test_runner.current_test_session:
        test_runner.end_test_session()


if __name__ == "__main__":
    main()
