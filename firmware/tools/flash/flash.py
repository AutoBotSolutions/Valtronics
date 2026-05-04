#!/usr/bin/env python3
"""
Valtronics Firmware Flash Tool

This script provides automated firmware flashing functionality
for Valtronics devices across multiple platforms.
"""

import os
import sys
import json
import time
import serial
import serial.tools.list_ports
import argparse
from pathlib import Path
from datetime import datetime

class FirmwareFlasher:
    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.firmware_dir = self.project_root / "firmware" / "dist"
        
        self.log("Firmware Flasher initialized")
        self.log(f"Project root: {self.project_root}")
        self.log(f"Firmware directory: {self.firmware_dir}")
    
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
                'hwid': port.hwid
            }
            available_ports.append(port_info)
            self.log(f"Found port: {port.device} - {port.description}")
        
        return available_ports
    
    def detect_platform(self, port):
        """Detect platform based on serial port characteristics"""
        self.log(f"Detecting platform for port {port}")
        
        try:
            ser = serial.Serial(port, 115200, timeout=2)
            
            # Send identification request
            ser.write(b'ID?\n')
            time.sleep(0.5)
            
            # Read response
            response = ser.read_all().decode('utf-8', errors='ignore').strip()
            ser.close()
            
            # Analyze response to determine platform
            if 'ESP32' in response:
                return 'esp32'
            elif 'Arduino' in response:
                return 'arduino'
            elif 'STM32' in response:
                return 'stm32'
            else:
                self.log("Could not detect platform automatically")
                return None
                
        except Exception as e:
            self.log(f"Error detecting platform: {e}")
            return None
    
    def flash_esp32(self, port, firmware_file):
        """Flash ESP32 firmware"""
        self.log(f"Flashing ESP32 firmware to {port}")
        
        try:
            # Check if esptool is available
            import subprocess
            
            # Put ESP32 in bootloader mode
            self.log("Putting ESP32 in bootloader mode...")
            ser = serial.Serial(port, 115200, timeout=1)
            ser.setDTR(False)
            time.sleep(0.1)
            ser.setDTR(True)
            time.sleep(0.1)
            ser.setDTR(False)
            ser.close()
            time.sleep(1)
            
            # Flash firmware using esptool
            cmd = [
                'esptool.py',
                '--port', port,
                '--baud', '460800',
                'write_flash',
                '--flash_mode', 'dio',
                '--flash_freq', '40m',
                '--flash_size', 'detect',
                '0x0', str(firmware_file)
            ]
            
            self.log(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("ESP32 firmware flashed successfully")
                return True
            else:
                self.log(f"ESP32 flash failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"Error flashing ESP32: {e}")
            return False
    
    def flash_arduino(self, port, firmware_file):
        """Flash Arduino firmware"""
        self.log(f"Flashing Arduino firmware to {port}")
        
        try:
            import subprocess
            
            # Flash firmware using avrdude
            cmd = [
                'avrdude',
                '-p', 'atmega2560',
                '-c', 'wiring',
                '-P', port,
                '-b', '115200',
                '-U', f'flash:w:{firmware_file}:i'
            ]
            
            self.log(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("Arduino firmware flashed successfully")
                return True
            else:
                self.log(f"Arduino flash failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"Error flashing Arduino: {e}")
            return False
    
    def flash_stm32(self, port, firmware_file):
        """Flash STM32 firmware"""
        self.log(f"Flashing STM32 firmware to {port}")
        
        try:
            import subprocess
            
            # Flash firmware using STM32CubeProgrammer CLI
            cmd = [
                'STM32_Programmer_CLI.exe',
                '--connect', port,
                '--write', str(firmware_file),
                '--verify',
                '--reset'
            ]
            
            self.log(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("STM32 firmware flashed successfully")
                return True
            else:
                self.log(f"STM32 flash failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"Error flashing STM32: {e}")
            return False
    
    def flash_firmware(self, port, platform, firmware_file):
        """Flash firmware based on platform"""
        self.log(f"Flashing {platform} firmware from {firmware_file} to {port}")
        
        if not Path(firmware_file).exists():
            self.log(f"Firmware file not found: {firmware_file}")
            return False
        
        if platform == 'esp32':
            return self.flash_esp32(port, firmware_file)
        elif platform == 'arduino':
            return self.flash_arduino(port, firmware_file)
        elif platform == 'stm32':
            return self.flash_stm32(port, firmware_file)
        else:
            self.log(f"Unsupported platform: {platform}")
            return False
    
    def verify_flash(self, port, platform):
        """Verify firmware flash"""
        self.log(f"Verifying firmware flash on {port}")
        
        try:
            ser = serial.Serial(port, 115200, timeout=5)
            
            # Wait for device to boot
            time.sleep(2)
            
            # Send verification request
            ser.write(b'VER?\n')
            time.sleep(1)
            
            # Read response
            response = ser.read_all().decode('utf-8', errors='ignore').strip()
            ser.close()
            
            if 'OK' in response or 'READY' in response:
                self.log("Firmware verification successful")
                return True
            else:
                self.log(f"Firmware verification failed: {response}")
                return False
                
        except Exception as e:
            self.log(f"Error verifying firmware: {e}")
            return False
    
    def get_firmware_file(self, platform, version=None):
        """Get firmware file for platform"""
        if version:
            firmware_dir = self.firmware_dir / f"valtronics-firmware-{version}"
        else:
            # Get latest release
            releases = [d for d in self.firmware_dir.iterdir() if d.is_dir() and d.name.startswith('valtronics-firmware-')]
            if not releases:
                self.log("No firmware releases found")
                return None
            
            firmware_dir = max(releases, key=lambda x: x.stat().st_mtime)
        
        # Find firmware file for platform
        firmware_files = list(firmware_dir.glob(f"{platform}_*.bin"))
        if not firmware_files:
            self.log(f"No firmware file found for {platform}")
            return None
        
        # Return the most recent firmware file
        return max(firmware_files, key=lambda x: x.stat().st_mtime)
    
    def interactive_flash(self):
        """Interactive firmware flashing"""
        self.log("Starting interactive firmware flashing...")
        
        # List available ports
        ports = self.list_serial_ports()
        if not ports:
            self.log("No serial ports found")
            return False
        
        # Let user select port
        print("\nAvailable serial ports:")
        for i, port in enumerate(ports):
            print(f"{i + 1}. {port['device']} - {port['description']}")
        
        try:
            port_choice = int(input("Select port number: ")) - 1
            if port_choice < 0 or port_choice >= len(ports):
                self.log("Invalid port selection")
                return False
            
            selected_port = ports[port_choice]['device']
        except ValueError:
            self.log("Invalid input")
            return False
        
        # Detect platform
        platform = self.detect_platform(selected_port)
        if not platform:
            # Let user select platform
            platforms = ['esp32', 'arduino', 'stm32']
            print("\nAvailable platforms:")
            for i, p in enumerate(platforms):
                print(f"{i + 1}. {p}")
            
            try:
                platform_choice = int(input("Select platform number: ")) - 1
                if platform_choice < 0 or platform_choice >= len(platforms):
                    self.log("Invalid platform selection")
                    return False
                
                platform = platforms[platform_choice]
            except ValueError:
                self.log("Invalid input")
                return False
        
        # Get firmware file
        firmware_file = self.get_firmware_file(platform)
        if not firmware_file:
            self.log("No firmware file found")
            return False
        
        # Flash firmware
        success = self.flash_firmware(selected_port, platform, firmware_file)
        if success:
            # Verify flash
            self.verify_flash(selected_port, platform)
        
        return success
    
    def batch_flash(self, platform, firmware_file=None):
        """Batch flash multiple devices"""
        self.log(f"Starting batch flash for {platform}")
        
        # Get firmware file
        if not firmware_file:
            firmware_file = self.get_firmware_file(platform)
            if not firmware_file:
                self.log("No firmware file found")
                return False
        
        # List available ports
        ports = self.list_serial_ports()
        if not ports:
            self.log("No serial ports found")
            return False
        
        success_count = 0
        
        for port_info in ports:
            port = port_info['device']
            self.log(f"Flashing device on {port}")
            
            if self.flash_firmware(port, platform, firmware_file):
                if self.verify_flash(port, platform):
                    success_count += 1
                    self.log(f"Successfully flashed {port}")
                else:
                    self.log(f"Verification failed for {port}")
            else:
                self.log(f"Failed to flash {port}")
        
        self.log(f"Batch flash completed: {success_count}/{len(ports)} devices flashed successfully")
        return success_count > 0
    
    def monitor_device(self, port, baud_rate=115200):
        """Monitor device serial output"""
        self.log(f"Monitoring device on {port} at {baud_rate} baud")
        
        try:
            ser = serial.Serial(port, baud_rate, timeout=1)
            
            print(f"Monitoring {port} (Press Ctrl+C to stop)")
            print("-" * 50)
            
            while True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(line)
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            self.log("Monitoring stopped")
        except Exception as e:
            self.log(f"Error monitoring device: {e}")
        finally:
            if 'ser' in locals():
                ser.close()
    
    def reset_device(self, port):
        """Reset device via serial port"""
        self.log(f"Resetting device on {port}")
        
        try:
            ser = serial.Serial(port, 115200, timeout=1)
            
            # Toggle DTR to reset
            ser.setDTR(False)
            time.sleep(0.1)
            ser.setDTR(True)
            time.sleep(0.1)
            ser.setDTR(False)
            
            ser.close()
            self.log("Device reset successfully")
            return True
            
        except Exception as e:
            self.log(f"Error resetting device: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Valtronics Firmware Flash Tool")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument("--port", help="Serial port")
    parser.add_argument("--platform", help="Target platform (esp32, arduino, stm32)")
    parser.add_argument("--firmware", help="Firmware file path")
    parser.add_argument("--version", help="Firmware version")
    parser.add_argument("--baud-rate", type=int, default=115200, help="Baud rate for monitoring")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--batch", action="store_true", help="Batch flash mode")
    parser.add_argument("--monitor", action="store_true", help="Monitor device")
    parser.add_argument("--reset", action="store_true", help="Reset device")
    parser.add_argument("--verify", action="store_true", help="Verify flash")
    parser.add_argument("--list-ports", action="store_true", help="List serial ports")
    
    args = parser.parse_args()
    
    # Initialize flasher
    flasher = FirmwareFlasher(args.project_root)
    
    # List ports
    if args.list_ports:
        ports = flasher.list_serial_ports()
        for port in ports:
            print(f"{port['device']}: {port['description']}")
        return
    
    # Interactive mode
    if args.interactive:
        success = flasher.interactive_flash()
        sys.exit(0 if success else 1)
    
    # Batch flash mode
    if args.batch:
        if not args.platform:
            print("Platform required for batch flash mode")
            sys.exit(1)
        success = flasher.batch_flash(args.platform, args.firmware)
        sys.exit(0 if success else 1)
    
    # Monitor device
    if args.monitor:
        if not args.port:
            print("Port required for monitor mode")
            sys.exit(1)
        flasher.monitor_device(args.port, args.baud_rate)
        return
    
    # Reset device
    if args.reset:
        if not args.port:
            print("Port required for reset mode")
            sys.exit(1)
        success = flasher.reset_device(args.port)
        sys.exit(0 if success else 1)
    
    # Flash firmware
    if args.port and args.platform:
        firmware_file = args.firmware
        if not firmware_file:
            firmware_file = flasher.get_firmware_file(args.platform, args.version)
            if not firmware_file:
                print("No firmware file found")
                sys.exit(1)
        
        success = flasher.flash_firmware(args.port, args.platform, firmware_file)
        if success and args.verify:
            flasher.verify_flash(args.port, args.platform)
        
        sys.exit(0 if success else 1)
    
    # Default: show help
    parser.print_help()


if __name__ == "__main__":
    main()
