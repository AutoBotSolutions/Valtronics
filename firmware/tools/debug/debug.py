#!/usr/bin/env python3
"""
Valtronics Firmware Debug Tool

This script provides comprehensive debugging capabilities for Valtronics firmware,
including serial monitoring, log analysis, memory profiling, and performance analysis.
"""

import os
import sys
import json
import time
import serial
import serial.tools.list_ports
import threading
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import re

class FirmwareDebugger:
    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.firmware_dir = self.project_root / "firmware"
        self.debug_dir = self.firmware_dir / "tools" / "debug"
        self.logs_dir = self.debug_dir / "logs"
        
        # Ensure directories exist
        self.debug_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        self.log("Firmware Debugger initialized")
        self.log(f"Project root: {self.project_root}")
        self.log(f"Debug directory: {self.debug_dir}")
        
        self.serial_port = None
        self.monitoring = False
        self.log_buffer = []
        self.filters = []
        
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def list_serial_ports(self):
        """List available serial ports"""
        self.log("Scanning for serial ports...")
        
        ports = serial.tools.list_ports.comports()
        available_ports = []
        
        for port in ports:
            port_info = {
                'device': port.device,
                'name': port.name,
                'description': port.description,
                'hwid': port.hwid,
                'vid': port.vid,
                'pid': port.pid
            }
            available_ports.append(port_info)
            self.log(f"Found port: {port.device} - {port.description}")
        
        return available_ports
    
    def detect_device(self, port):
        """Detect device type based on serial communication"""
        self.log(f"Detecting device on port {port}")
        
        try:
            ser = serial.Serial(port, 115200, timeout=2)
            
            # Send identification request
            ser.write(b'ID?\n')
            time.sleep(0.5)
            
            # Read response
            response = ser.read_all().decode('utf-8', errors='ignore').strip()
            ser.close()
            
            # Analyze response to determine device type
            if 'ESP32' in response:
                return 'esp32'
            elif 'Arduino' in response:
                return 'arduino'
            elif 'STM32' in response:
                return 'stm32'
            elif 'Valtronics' in response:
                return 'valtronics'
            else:
                self.log("Could not detect device type automatically")
                return None
                
        except Exception as e:
            self.log(f"Error detecting device: {e}")
            return None
    
    def start_serial_monitor(self, port, baud_rate=115200, filters=None):
        """Start serial monitoring"""
        self.log(f"Starting serial monitor on {port} at {baud_rate} baud")
        
        try:
            self.serial_port = serial.Serial(port, baud_rate, timeout=1)
            self.monitoring = True
            
            if filters:
                self.filters = filters
                self.log(f"Applied filters: {filters}")
            
            # Start monitoring thread
            monitor_thread = threading.Thread(target=self._monitor_serial)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            self.log("Serial monitor started (Press Ctrl+C to stop)")
            
            # Monitor in main thread
            self._monitor_serial()
            
        except Exception as e:
            self.log(f"Error starting serial monitor: {e}")
            return False
        
        return True
    
    def _monitor_serial(self):
        """Monitor serial port"""
        try:
            while self.monitoring and self.serial_port:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode('utf-8', errors='ignore').strip()
                    
                    if line:
                        # Apply filters
                        if self._should_log_line(line):
                            self._process_log_line(line)
                
                time.sleep(0.01)
                
        except serial.SerialException as e:
            self.log(f"Serial error: {e}")
        except KeyboardInterrupt:
            self.log("Serial monitor stopped by user")
        finally:
            if self.serial_port:
                self.serial_port.close()
                self.serial_port = None
            self.monitoring = False
    
    def _should_log_line(self, line):
        """Check if line should be logged based on filters"""
        if not self.filters:
            return True
        
        for filter_pattern in self.filters:
            if filter_pattern in line:
                return True
        
        return False
    
    def _process_log_line(self, line):
        """Process and log line"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        formatted_line = f"[{timestamp}] {line}"
        
        # Add to buffer
        self.log_buffer.append({
            'timestamp': timestamp,
            'line': line,
            'formatted': formatted_line
        })
        
        # Keep buffer size manageable
        if len(self.log_buffer) > 10000:
            self.log_buffer = self.log_buffer[-5000:]
        
        # Print to console
        print(formatted_line)
        
        # Save to log file
        self._save_log_line(formatted_line)
    
    def _save_log_line(self, line):
        """Save log line to file"""
        log_file = self.logs_dir / f"debug_log_{datetime.now().strftime('%Y%m%d')}.txt"
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(line + '\n')
        except Exception as e:
            self.log(f"Error saving log: {e}")
    
    def stop_serial_monitor(self):
        """Stop serial monitoring"""
        self.log("Stopping serial monitor...")
        self.monitoring = False
        if self.serial_port:
            self.serial_port.close()
            self.serial_port = None
    
    def analyze_logs(self, log_file=None, pattern=None):
        """Analyze log files"""
        self.log("Analyzing logs...")
        
        if not log_file:
            # Find latest log file
            log_files = list(self.logs_dir.glob("debug_log_*.txt"))
            if not log_files:
                self.log("No log files found")
                return None
            
            log_file = max(log_files, key=lambda x: x.stat().st_mtime)
        
        self.log(f"Analyzing log file: {log_file}")
        
        analysis = {
            'file': str(log_file),
            'total_lines': 0,
            'error_count': 0,
            'warning_count': 0,
            'info_count': 0,
            'debug_count': 0,
            'patterns': {},
            'timestamps': [],
            'errors': [],
            'warnings': []
        }
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    analysis['total_lines'] += 1
                    
                    # Count log levels
                    if 'ERROR' in line or 'error' in line:
                        analysis['error_count'] += 1
                        analysis['errors'].append({
                            'line_num': line_num,
                            'message': line
                        })
                    elif 'WARNING' in line or 'warning' in line:
                        analysis['warning_count'] += 1
                        analysis['warnings'].append({
                            'line_num': line_num,
                            'message': line
                        })
                    elif 'INFO' in line or 'info' in line:
                        analysis['info_count'] += 1
                    elif 'DEBUG' in line or 'debug' in line:
                        analysis['debug_count'] += 1
                    
                    # Extract timestamps
                    timestamp_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    if timestamp_match:
                        analysis['timestamps'].append(timestamp_match.group(1))
                    
                    # Search for specific pattern
                    if pattern and pattern in line:
                        pattern_key = f"pattern_{pattern}"
                        if pattern_key not in analysis['patterns']:
                            analysis['patterns'][pattern_key] = []
                        analysis['patterns'][pattern_key].append({
                            'line_num': line_num,
                            'message': line
                        })
        
        except Exception as e:
            self.log(f"Error analyzing logs: {e}")
            return None
        
        # Generate summary
        self.log(f"Log analysis complete:")
        self.log(f"  Total lines: {analysis['total_lines']}")
        self.log(f"  Errors: {analysis['error_count']}")
        self.log(f"  Warnings: {analysis['warning_count']}")
        self.log(f"  Info: {analysis['info_count']}")
        self.log(f"  Debug: {analysis['debug_count']}")
        
        if pattern:
            pattern_key = f"pattern_{pattern}"
            if pattern_key in analysis['patterns']:
                self.log(f"  Pattern matches: {len(analysis['patterns'][pattern_key])}")
        
        return analysis
    
    def generate_log_report(self, analysis):
        """Generate HTML log analysis report"""
        if not analysis:
            return None
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Firmware Log Analysis Report</title>
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
        .log-section {{ margin: 20px 0; }}
        .log-item {{ margin: 10px 0; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px; }}
        .log-item.error {{ background: #f8d7da; border-left: 4px solid #dc3545; }}
        .log-item.warning {{ background: #fff3cd; border-left: 4px solid #ffc107; }}
        .log-item.info {{ background: #d1ecf1; border-left: 4px solid #17a2b8; }}
        .log-item.debug {{ background: #e2e3e5; border-left: 4px solid #6c757d; }}
        .filter-buttons {{ margin: 20px 0; }}
        .filter-buttons button {{ margin: 5px; padding: 8px 16px; border: 1px solid #ddd; background: white; border-radius: 4px; cursor: pointer; }}
        .filter-buttons button.active {{ background: #007bff; color: white; }}
        .hidden {{ display: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Firmware Log Analysis Report</h1>
        
        <div class="summary">
            <div class="summary-item">
                <div class="summary-value">{analysis['total_lines']}</div>
                <div class="summary-label">Total Lines</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{analysis['error_count']}</div>
                <div class="summary-label">Errors</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{analysis['warning_count']}</div>
                <div class="summary-label">Warnings</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{analysis['info_count']}</div>
                <div class="summary-label">Info</div>
            </div>
        </div>
        
        <div class="filter-buttons">
            <button class="active" onclick="filterLogs('all')">All</button>
            <button onclick="filterLogs('error')">Errors</button>
            <button onclick="filterLogs('warning')">Warnings</button>
            <button onclick="filterLogs('info')">Info</button>
            <button onclick="filterLogs('debug')">Debug</button>
        </div>
        
        <div class="log-section">
            <h2>Errors</h2>
"""
        
        # Add errors
        for error in analysis.get('errors', [])[:50]:  # Limit to 50 errors
            html += f"""
            <div class="log-item error" data-level="error">
                <strong>Line {error['line_num']}:</strong> {error['message']}
            </div>
            """
        
        html += """
        </div>
        
        <div class="log-section">
            <h2>Warnings</h2>
"""
        
        # Add warnings
        for warning in analysis.get('warnings', [])[:50]:  # Limit to 50 warnings
            html += f"""
            <div class="log-item warning" data-level="warning">
                <strong>Line {warning['line_num']}:</strong> {warning['message']}
            </div>
            """
        
        html += """
        </div>
    </div>
    
    <script>
        function filterLogs(level) {
            const logs = document.querySelectorAll('.log-item');
            const buttons = document.querySelectorAll('.filter-buttons button');
            
            // Update button states
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Filter logs
            logs.forEach(log => {
                if (level === 'all' || log.dataset.level === level) {
                    log.classList.remove('hidden');
                } else {
                    log.classList.add('hidden');
                }
            });
        }
    </script>
</body>
</html>
"""
        
        return html
    
    def monitor_memory(self, port, baud_rate=115200):
        """Monitor memory usage via serial"""
        self.log(f"Monitoring memory usage on {port}")
        
        try:
            ser = serial.Serial(port, baud_rate, timeout=2)
            
            memory_data = []
            
            while True:
                # Send memory query
                ser.write(b'MEM?\n')
                time.sleep(0.5)
                
                # Read response
                response = ser.read_all().decode('utf-8', errors='ignore').strip()
                
                if response:
                    # Parse memory info
                    memory_match = re.search(r'Free: (\d+), Total: (\d+)', response)
                    if memory_match:
                        free_mem = int(memory_match.group(1))
                        total_mem = int(memory_match.group(2))
                        
                        memory_data.append({
                            'timestamp': datetime.now().isoformat(),
                            'free': free_mem,
                            'total': total_mem,
                            'used': total_mem - free_mem,
                            'percentage': ((total_mem - free_mem) / total_mem) * 100
                        })
                        
                        # Print current status
                        print(f"Memory: {free_mem}/{total_mem} bytes ({((total_mem - free_mem) / total_mem) * 100:.1f}% used)")
                
                time.sleep(5)  # Monitor every 5 seconds
                
        except KeyboardInterrupt:
            self.log("Memory monitoring stopped")
        except Exception as e:
            self.log(f"Error monitoring memory: {e}")
        
        finally:
            if 'ser' in locals():
                ser.close()
        
        return memory_data
    
    def monitor_performance(self, port, baud_rate=115200):
        """Monitor performance metrics"""
        self.log(f"Monitoring performance on {port}")
        
        try:
            ser = serial.Serial(port, baud_rate, timeout=2)
            
            performance_data = []
            
            while True:
                # Send performance query
                ser.write(b'PERF?\n')
                time.sleep(0.5)
                
                # Read response
                response = ser.read_all().decode('utf-8', errors='ignore').strip()
                
                if response:
                    # Parse performance info
                    perf_match = re.search(r'CPU: ([\d.]+)%, Loop: (\d+)ms, Tasks: (\d+)', response)
                    if perf_match:
                        cpu_usage = float(perf_match.group(1))
                        loop_time = int(perf_match.group(2))
                        task_count = int(perf_match.group(3))
                        
                        performance_data.append({
                            'timestamp': datetime.now().isoformat(),
                            'cpu_usage': cpu_usage,
                            'loop_time': loop_time,
                            'task_count': task_count
                        })
                        
                        # Print current status
                        print(f"Performance: CPU {cpu_usage}%, Loop {loop_time}ms, Tasks {task_count}")
                
                time.sleep(10)  # Monitor every 10 seconds
                
        except KeyboardInterrupt:
            self.log("Performance monitoring stopped")
        except Exception as e:
            self.log(f"Error monitoring performance: {e}")
        
        finally:
            if 'ser' in locals():
                ser.close()
        
        return performance_data
    
    def send_debug_command(self, port, command, baud_rate=115200):
        """Send debug command to device"""
        self.log(f"Sending command '{command}' to {port}")
        
        try:
            ser = serial.Serial(port, baud_rate, timeout=2)
            
            # Send command
            ser.write((command + '\n').encode())
            
            # Wait for response
            time.sleep(1)
            
            # Read response
            response = ser.read_all().decode('utf-8', errors='ignore').strip()
            
            self.log(f"Response: {response}")
            
            ser.close()
            return response
            
        except Exception as e:
            self.log(f"Error sending command: {e}")
            return None
    
    def capture_serial_data(self, port, duration=60, baud_rate=115200):
        """Capture serial data for specified duration"""
        self.log(f"Capturing serial data for {duration} seconds...")
        
        try:
            ser = serial.Serial(port, baud_rate, timeout=1)
            
            captured_data = []
            start_time = time.time()
            
            while time.time() - start_time < duration:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    captured_data.append({
                        'timestamp': datetime.now().isoformat(),
                        'data': data.hex(),
                        'text': data.decode('utf-8', errors='ignore')
                    })
                
                time.sleep(0.01)
            
            ser.close()
            
            # Save captured data
            capture_file = self.logs_dir / f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(capture_file, 'w') as f:
                json.dump(captured_data, f, indent=2)
            
            self.log(f"Captured {len(captured_data)} data packets to {capture_file}")
            return captured_data
            
        except Exception as e:
            self.log(f"Error capturing data: {e}")
            return None
    
    def analyze_serial_protocol(self, port, baud_rate=115200):
        """Analyze serial protocol"""
        self.log(f"Analyzing serial protocol on {port}")
        
        # Capture data for analysis
        captured_data = self.capture_serial_data(port, duration=30, baud_rate=baud_rate)
        
        if not captured_data:
            return None
        
        analysis = {
            'total_packets': len(captured_data),
            'packet_sizes': [],
            'patterns': {},
            'timing': [],
            'encoding': 'utf-8',
            'errors': 0
        }
        
        for packet in captured_data:
            # Analyze packet size
            data_bytes = bytes.fromhex(packet['data'])
            analysis['packet_sizes'].append(len(data_bytes))
            
            # Analyze patterns
            text = packet['text']
            if 'ERROR' in text:
                if 'error' not in analysis['patterns']:
                    analysis['patterns']['error'] = 0
                analysis['patterns']['error'] += 1
            
            if 'WARNING' in text:
                if 'warning' not in analysis['patterns']:
                    analysis['patterns']['warning'] = 0
                analysis['patterns']['warning'] += 1
            
            if 'DEBUG' in text:
                if 'debug' not in analysis['patterns']:
                    analysis['patterns']['debug'] = 0
                analysis['patterns']['debug'] += 1
        
        self.log(f"Protocol analysis complete:")
        self.log(f"  Total packets: {analysis['total_packets']}")
        self.log(f"  Average packet size: {sum(analysis['packet_sizes']) / len(analysis['packet_sizes']) if analysis['packet_sizes'] else 0}")
        self.log(f"  Patterns: {analysis['patterns']}")
        
        return analysis
    
    def create_debug_script(self, device_type, output_file=None):
        """Create debug script for specific device type"""
        self.log(f"Creating debug script for {device_type}")
        
        if not output_file:
            output_file = self.debug_dir / f"debug_{device_type}.py"
        
        script_content = f"""
#!/usr/bin/env python3
"""
Debug script for {device_type} devices
"""

import serial
import time
from firmware.tools.debug.debug import FirmwareDebugger

def debug_{device_type}():
    debugger = FirmwareDebugger()
    
    # List available ports
    ports = debugger.list_serial_ports()
    if not ports:
        print("No serial ports found")
        return
    
    # Auto-detect device
    for port_info in ports:
        device = debugger.detect_device(port_info['device'])
        if device == '{device_type}':
            print(f"Found {device_type} on {{port_info['device']}}")
            
            # Start monitoring
            debugger.start_serial_monitor(port_info['device'])
            break
    else:
        print(f"No {device_type} device found")
    
    # Send debug commands
    debugger.send_debug_command(port_info['device'], 'STATUS')
    debugger.send_debug_command(port_info['device'], 'MEM')
    debugger.send_debug_command(port_info['device'], 'PERF')

if __name__ == "__main__":
    debug_{device_type}()
"""
        
        try:
            with open(output_file, 'w') as f:
                f.write(script_content)
            
            # Make executable
            os.chmod(output_file, 0o755)
            
            self.log(f"Debug script created: {output_file}")
            return output_file
            
        except Exception as e:
            self.log(f"Error creating debug script: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(description="Valtronics Firmware Debug Tool")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument("--port", help="Serial port")
    parser.add_argument("--baud-rate", type=int, default=115200, help="Baud rate")
    parser.add_argument("--duration", type=int, default=60, help="Duration for capture operations")
    parser.add_argument("--log-file", help="Log file to analyze")
    parser.add_argument("--pattern", help="Pattern to search in logs")
    parser.add_argument("--filter", action="append", help="Filter patterns for serial monitor")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Monitor commands
    monitor_parser = subparsers.add_parser("monitor", help="Monitor serial port")
    monitor_parser.add_argument("--port", help="Serial port")
    monitor_parser.add_argument("--baud-rate", type=int, default=115200, help="Baud rate")
    monitor_parser.add_argument("--filter", action="append", help="Filter patterns")
    
    memory_parser = subparsers.add_parser("memory", help="Monitor memory usage")
    memory_parser.add_argument("--port", help="Serial port")
    memory_parser.add_argument("--baud-rate", type=int, default=115200, help="Baud rate")
    
    performance_parser = subparsers.add_parser("performance", help="Monitor performance")
    performance_parser.add_argument("--port", help="Serial port")
    performance_parser.add_argument("--baud-rate", type=int, default=115200, help="Baud rate")
    
    # Analysis commands
    analyze_parser = subparsers.add_parser("analyze", help="Analyze logs")
    analyze_parser.add_argument("--log-file", help="Log file to analyze")
    analyze_parser.add_argument("--pattern", help="Pattern to search")
    
    protocol_parser = subparsers.add_parser("protocol", help="Analyze serial protocol")
    protocol_parser.add_argument("--port", help="Serial port")
    protocol_parser.add_argument("--baud-rate", type=int, default=115200, help="Baud rate")
    
    # Utility commands
    list_parser = subparsers.add_parser("list", help="List serial ports")
    
    detect_parser = subparsers.add_parser("detect", help="Detect device")
    detect_parser.add_argument("--port", help="Serial port")
    
    command_parser = subparsers.add_parser("command", help="Send debug command")
    command_parser.add_argument("--port", help="Serial port")
    command_parser.add_argument("--command", required=True, help="Command to send")
    command_parser.add_argument("--baud-rate", type=int, default=115200, help="Baud rate")
    
    capture_parser = subparsers.add_parser("capture", help="Capture serial data")
    capture_parser.add_argument("--port", help="Serial port")
    capture_parser.add_argument("--duration", type=int, default=60, help="Capture duration")
    capture_parser.add_argument("--baud-rate", type=int, default=115200, help="Baud rate")
    
    script_parser = subparsers.add_parser("script", help="Create debug script")
    script_parser.add_argument("--device-type", required=True, help="Device type")
    script_parser.add_argument("--output", help="Output file")
    
    args = parser.parse_args()
    
    # Initialize debugger
    debugger = FirmwareDebugger(args.project_root)
    
    # Execute commands
    if args.command == "monitor":
        if not args.port:
            ports = debugger.list_serial_ports()
            if not ports:
                print("No serial ports found")
                return
            args.port = ports[0]['device']
        
        debugger.start_serial_monitor(args.port, args.baud_rate, args.filter)
    
    elif args.command == "memory":
        if not args.port:
            ports = debugger.list_serial_ports()
            if not ports:
                print("No serial ports found")
                return
            args.port = ports[0]['device']
        
        debugger.monitor_memory(args.port, args.baud_rate)
    
    elif args.command == "performance":
        if not args.port:
            ports = debugger.list_serial_ports()
            if not ports:
                print("No serial ports found")
                return
            args.port = ports[0]['device']
        
        debugger.monitor_performance(args.port, args.baud_rate)
    
    elif args.command == "analyze":
        analysis = debugger.analyze_logs(args.log_file, args.pattern)
        if analysis:
            # Generate HTML report
            html = debugger.generate_log_report(analysis)
            if html:
                report_file = debugger.logs_dir / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                with open(report_file, 'w') as f:
                    f.write(html)
                print(f"Analysis report generated: {report_file}")
    
    elif args.command == "protocol":
        if not args.port:
            ports = debugger.list_serial_ports()
            if not ports:
                print("No serial ports found")
                return
            args.port = ports[0]['device']
        
        debugger.analyze_serial_protocol(args.port, args.baud_rate)
    
    elif args.command == "list":
        debugger.list_serial_ports()
    
    elif args.command == "detect":
        if not args.port:
            ports = debugger.list_serial_ports()
            if not ports:
                print("No serial ports found")
                return
            args.port = ports[0]['device']
        
        device = debugger.detect_device(args.port)
        if device:
            print(f"Detected device: {device}")
        else:
            print("Could not detect device type")
    
    elif args.command == "command":
        if not args.port:
            ports = debugger.list_serial_ports()
            if not ports:
                print("No serial ports found")
                return
            args.port = ports[0]['device']
        
        debugger.send_debug_command(args.port, args.command, args.baud_rate)
    
    elif args.command == "capture":
        if not args.port:
            ports = debugger.list_serial_ports()
            if not ports:
                print("No serial ports found")
                return
            args.port = ports[0]['device']
        
        debugger.capture_serial_data(args.port, args.duration, args.baud_rate)
    
    elif args.command == "script":
        debugger.create_debug_script(args.device_type, args.output)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
