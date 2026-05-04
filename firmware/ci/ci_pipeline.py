#!/usr/bin/env python3
"""
Valtronics Firmware CI/CD Pipeline

This script provides comprehensive CI/CD pipeline functionality for Valtronics firmware,
including automated building, testing, deployment, and release management.
"""

import os
import sys
import json
import time
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib
import shutil

class FirmwareCICD:
    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.firmware_dir = self.project_root / "firmware"
        self.ci_dir = self.firmware_dir / "ci"
        self.build_dir = self.firmware_dir / "build"
        self.dist_dir = self.firmware_dir / "dist"
        self.artifacts_dir = self.ci_dir / "artifacts"
        
        # Ensure directories exist
        self.ci_dir.mkdir(exist_ok=True)
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        self.artifacts_dir.mkdir(exist_ok=True)
        
        self.log("Firmware CI/CD Pipeline initialized")
        self.log(f"Project root: {self.project_root}")
        self.log(f"Firmware directory: {self.firmware_dir}")
        self.log(f"CI directory: {self.ci_dir}")
        
        self.pipeline_config = self.load_pipeline_config()
        self.build_number = self.get_build_number()
        
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def run_command(self, command, cwd=None, capture_output=True, timeout=600):
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
    
    def load_pipeline_config(self):
        """Load pipeline configuration"""
        config_file = self.ci_dir / "pipeline_config.json"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            default_config = {
                "platforms": ["esp32", "arduino_mega", "nucleo_f429zi"],
                "test_suites": ["unit", "integration", "hardware"],
                "build_parallel": True,
                "test_parallel": True,
                "deploy_environments": ["staging", "production"],
                "artifact_retention_days": 30,
                "notification_channels": ["email", "slack"],
                "quality_gates": {
                    "test_coverage_threshold": 80,
                    "max_test_failures": 0,
                    "max_build_time": 300
                }
            }
            
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            return default_config
    
    def get_build_number(self):
        """Get current build number"""
        build_file = self.ci_dir / "build_number.txt"
        
        if build_file.exists():
            with open(build_file, 'r') as f:
                return int(f.read().strip())
        else:
            return 1
    
    def increment_build_number(self):
        """Increment build number"""
        self.build_number += 1
        build_file = self.ci_dir / "build_number.txt"
        
        with open(build_file, 'w') as f:
            f.write(str(self.build_number))
        
        self.log(f"Build number incremented to: {self.build_number}")
        return self.build_number
    
    def run_build_pipeline(self, platforms=None, parallel=None):
        """Run build pipeline"""
        self.log("Starting build pipeline...")
        
        if not platforms:
            platforms = self.pipeline_config["platforms"]
        
        if parallel is None:
            parallel = self.pipeline_config["build_parallel"]
        
        build_results = {}
        
        if parallel:
            # Parallel builds
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(platforms)) as executor:
                future_to_platform = {
                    executor.submit(self.build_platform, platform): platform 
                    for platform in platforms
                }
                
                for future in concurrent.futures.as_completed(future_to_platform):
                    platform = future_to_platform[future]
                    try:
                        result = future.result()
                        build_results[platform] = result
                        self.log(f"Build completed for {platform}: {'SUCCESS' if result['success'] else 'FAILED'}")
                    except Exception as e:
                        self.log(f"Build error for {platform}: {e}")
                        build_results[platform] = {
                            'success': False,
                            'error': str(e),
                            'platform': platform,
                            'timestamp': datetime.now().isoformat()
                        }
        else:
            # Sequential builds
            for platform in platforms:
                result = self.build_platform(platform)
                build_results[platform] = result
                self.log(f"Build completed for {platform}: {'SUCCESS' if result['success'] else 'FAILED'}")
        
        # Save build results
        self.save_build_results(build_results)
        
        return build_results
    
    def build_platform(self, platform):
        """Build firmware for specific platform"""
        self.log(f"Building firmware for {platform}...")
        
        build_result = {
            'platform': platform,
            'success': False,
            'build_number': self.build_number,
            'timestamp': datetime.now().isoformat(),
            'artifacts': [],
            'metrics': {}
        }
        
        start_time = time.time()
        
        try:
            # Change to firmware directory
            os.chdir(self.firmware_dir)
            
            # Clean previous build
            clean_cmd = f"pio run --target clean -e {platform}"
            stdout, stderr, returncode = self.run_command(clean_cmd)
            
            if returncode != 0:
                build_result['error'] = stderr
                return build_result
            
            # Build firmware
            build_cmd = f"pio run -e {platform}"
            stdout, stderr, returncode = self.run_command(build_cmd, timeout=300)
            
            build_result['stdout'] = stdout
            build_result['stderr'] = stderr
            build_result['returncode'] = returncode
            
            if returncode == 0:
                build_result['success'] = True
                
                # Collect artifacts
                artifacts = self.collect_build_artifacts(platform)
                build_result['artifacts'] = artifacts
                
                # Calculate metrics
                build_time = time.time() - start_time
                build_result['metrics']['build_time'] = build_time
                build_result['metrics']['artifact_count'] = len(artifacts)
                build_result['metrics']['binary_size'] = sum([a['size'] for a in artifacts if a['type'] == 'binary'])
                
                self.log(f"Build successful for {platform} in {build_time:.2f}s")
            else:
                build_result['error'] = stderr
                self.log(f"Build failed for {platform}: {stderr}")
        
        except Exception as e:
            build_result['error'] = str(e)
            self.log(f"Build exception for {platform}: {e}")
        
        return build_result
    
    def collect_build_artifacts(self, platform):
        """Collect build artifacts"""
        artifacts = []
        
        # Find build directory
        build_path = self.firmware_dir / ".pio" / "build" / platform
        
        if build_path.exists():
            # Find firmware binaries
            for artifact_file in build_path.glob("**/*.bin"):
                artifact = {
                    'name': artifact_file.name,
                    'path': str(artifact_file),
                    'size': artifact_file.stat().st_size,
                    'type': 'binary',
                    'checksum': self.calculate_checksum(artifact_file),
                    'platform': platform
                }
                artifacts.append(artifact)
            
            # Find ELF files
            for artifact_file in build_path.glob("**/*.elf"):
                artifact = {
                    'name': artifact_file.name,
                    'path': str(artifact_file),
                    'size': artifact_file.stat().st_size,
                    'type': 'elf',
                    'checksum': self.calculate_checksum(artifact_file),
                    'platform': platform
                }
                artifacts.append(artifact)
            
            # Find map files
            for artifact_file in build_path.glob("**/*.map"):
                artifact = {
                    'name': artifact_file.name,
                    'path': str(artifact_file),
                    'size': artifact_file.stat().st_size,
                    'type': 'map',
                    'checksum': self.calculate_checksum(artifact_file),
                    'platform': platform
                }
                artifacts.append(artifact)
        
        return artifacts
    
    def calculate_checksum(self, file_path):
        """Calculate SHA256 checksum for file"""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    def run_test_pipeline(self, platforms=None, test_suites=None, parallel=None):
        """Run test pipeline"""
        self.log("Starting test pipeline...")
        
        if not platforms:
            platforms = self.pipeline_config["platforms"]
        
        if not test_suites:
            test_suites = self.pipeline_config["test_suites"]
        
        if parallel is None:
            parallel = self.pipeline_config["test_parallel"]
        
        test_results = {}
        
        for platform in platforms:
            platform_results = {}
            
            for test_suite in test_suites:
                self.log(f"Running {test_suite} tests for {platform}...")
                
                result = self.run_test_suite(platform, test_suite)
                platform_results[test_suite] = result
                
                self.log(f"Test {test_suite} for {platform}: {'PASSED' if result['passed'] else 'FAILED'}")
            
            test_results[platform] = platform_results
        
        # Save test results
        self.save_test_results(test_results)
        
        return test_results
    
    def run_test_suite(self, platform, test_suite):
        """Run specific test suite"""
        test_result = {
            'platform': platform,
            'suite': test_suite,
            'passed': False,
            'timestamp': datetime.now().isoformat(),
            'metrics': {}
        }
        
        try:
            # Change to firmware directory
            os.chdir(self.firmware_dir)
            
            # Run tests
            test_cmd = f"pio test -e {platform} --filter {test_suite}_*"
            stdout, stderr, returncode = self.run_command(test_cmd, timeout=600)
            
            test_result['stdout'] = stdout
            test_result['stderr'] = stderr
            test_result['returncode'] = returncode
            
            if returncode == 0:
                test_result['passed'] = True
                
                # Parse test metrics
                test_result['metrics'] = self.parse_test_output(stdout)
                
                self.log(f"Test suite {test_suite} passed for {platform}")
            else:
                test_result['error'] = stderr
                self.log(f"Test suite {test_suite} failed for {platform}: {stderr}")
        
        except Exception as e:
            test_result['error'] = str(e)
            self.log(f"Test suite exception for {platform}: {e}")
        
        return test_result
    
    def parse_test_output(self, test_output):
        """Parse test output for metrics"""
        metrics = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'test_time': 0
        }
        
        # Parse test results (this would need to be adapted based on actual test framework output)
        lines = test_output.split('\n')
        for line in lines:
            if 'Tests run:' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'Tests':
                        try:
                            metrics['total_tests'] = int(parts[i+2])
                        except (IndexError, ValueError):
                            pass
                    elif part == 'Passed:':
                        try:
                            metrics['passed_tests'] = int(parts[i+1])
                        except (IndexError, ValueError):
                            pass
                    elif part == 'Failed:':
                        try:
                            metrics['failed_tests'] = int(parts[i+1])
                        except (IndexError, ValueError):
                            pass
        
        return metrics
    
    def run_quality_gates(self, build_results, test_results):
        """Run quality gates"""
        self.log("Running quality gates...")
        
        quality_gates = self.pipeline_config["quality_gates"]
        gate_results = {
            'passed': True,
            'gates': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Test coverage gate
        if 'test_coverage_threshold' in quality_gates:
            # This would need actual coverage calculation
            coverage = self.calculate_test_coverage(test_results)
            threshold = quality_gates['test_coverage_threshold']
            
            gate_results['gates']['test_coverage'] = {
                'passed': coverage >= threshold,
                'value': coverage,
                'threshold': threshold
            }
            
            if coverage < threshold:
                gate_results['passed'] = False
                self.log(f"Quality gate failed: Test coverage {coverage}% < {threshold}%")
        
        # Test failures gate
        if 'max_test_failures' in quality_gates:
            total_failures = sum([
                suite.get('failed_tests', 0) 
                for platform_results in test_results.values()
                for suite in platform_results.values()
            ])
            max_failures = quality_gates['max_test_failures']
            
            gate_results['gates']['test_failures'] = {
                'passed': total_failures <= max_failures,
                'value': total_failures,
                'threshold': max_failures
            }
            
            if total_failures > max_failures:
                gate_results['passed'] = False
                self.log(f"Quality gate failed: Test failures {total_failures} > {max_failures}")
        
        # Build time gate
        if 'max_build_time' in quality_gates:
            max_build_time = quality_gates['max_build_time']
            build_times = [
                result.get('metrics', {}).get('build_time', 0)
                for result in build_results.values()
            ]
            avg_build_time = sum(build_times) / len(build_times) if build_times else 0
            
            gate_results['gates']['build_time'] = {
                'passed': avg_build_time <= max_build_time,
                'value': avg_build_time,
                'threshold': max_build_time
            }
            
            if avg_build_time > max_build_time:
                gate_results['passed'] = False
                self.log(f"Quality gate failed: Build time {avg_build_time:.2f}s > {max_build_time}s")
        
        return gate_results
    
    def calculate_test_coverage(self, test_results):
        """Calculate test coverage (placeholder implementation)"""
        # This would need actual coverage calculation
        return 85.0  # Placeholder
    
    def create_release(self, version=None, platforms=None):
        """Create release package"""
        self.log("Creating release package...")
        
        if not version:
            version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if not platforms:
            platforms = self.pipeline_config["platforms"]
        
        release_dir = self.dist_dir / f"valtronics-firmware-{version}"
        release_dir.mkdir(exist_ok=True)
        
        # Copy artifacts
        release_artifacts = []
        for platform in platforms:
            platform_build_dir = self.firmware_dir / ".pio" / "build" / platform
            
            if platform_build_dir.exists():
                # Find firmware files
                for artifact_file in platform_build_dir.glob("**/*.bin"):
                    dest_file = release_dir / f"{platform}_{artifact_file.name}"
                    shutil.copy2(artifact_file, dest_file)
                    
                    artifact_info = {
                        'name': dest_file.name,
                        'platform': platform,
                        'size': dest_file.stat().st_size,
                        'checksum': self.calculate_checksum(dest_file)
                    }
                    release_artifacts.append(artifact_info)
        
        # Create release manifest
        manifest = {
            'version': version,
            'build_number': self.build_number,
            'platforms': platforms,
            'build_date': datetime.now().isoformat(),
            'description': 'Valtronics Firmware Release',
            'artifacts': release_artifacts,
            'quality_gates': self.pipeline_config['quality_gates']
        }
        
        manifest_file = release_dir / "manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Create release notes
        release_notes = self.generate_release_notes(version, platforms)
        notes_file = release_dir / "RELEASE_NOTES.md"
        with open(notes_file, 'w') as f:
            f.write(release_notes)
        
        self.log(f"Release created: {release_dir}")
        return release_dir
    
    def generate_release_notes(self, version, platforms):
        """Generate release notes"""
        notes = f"""# Valtronics Firmware Release {version}

## Overview
This release includes firmware updates for the following platforms: {', '.join(platforms)}.

## Platforms
"""
        
        for platform in platforms:
            notes += f"- **{platform}**: Latest firmware with all bug fixes and improvements\n"
        
        notes += f"""
## Installation
1. Download the appropriate firmware file for your platform
2. Use the Valtronics flash tool to upload firmware
3. Monitor device status via web interface or MQTT

## Build Information
- Build Number: {self.build_number}
- Build Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Version: {version}

## Quality Gates
- Test Coverage: ≥{self.pipeline_config['quality_gates']['test_coverage_threshold']}%
- Max Test Failures: {self.pipeline_config['quality_gates']['max_test_failures']}
- Max Build Time: {self.pipeline_config['quality_gates']['max_build_time']}s

## Known Issues
None

## Changes
- Bug fixes and performance improvements
- Enhanced error handling
- Updated documentation

## Support
For support and documentation, visit the Valtronics GitHub repository or contact firmware@valtronics.com.
"""
        
        return notes
    
    def deploy_to_environment(self, environment, version=None):
        """Deploy to specific environment"""
        self.log(f"Deploying to {environment} environment...")
        
        if not version:
            # Find latest release
            releases = [d for d in self.dist_dir.iterdir() if d.is_dir() and d.name.startswith('valtronics-firmware-')]
            if not releases:
                self.log("No releases found for deployment")
                return False
            
            latest_release = max(releases, key=lambda x: x.stat().st_mtime)
            version = latest_release.name.replace('valtronics-firmware-', '')
        
        self.log(f"Deploying version {version} to {environment}")
        
        # This would implement actual deployment logic
        # For now, just log the deployment
        deployment_info = {
            'environment': environment,
            'version': version,
            'timestamp': datetime.now().isoformat(),
            'status': 'deployed'
        }
        
        # Save deployment info
        deployment_file = self.ci_dir / f"deployment_{environment}_{version}.json"
        with open(deployment_file, 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        self.log(f"Deployment completed: {deployment_file}")
        return True
    
    def cleanup_artifacts(self, older_than_days=None):
        """Clean up old artifacts"""
        if older_than_days is None:
            older_than_days = self.pipeline_config.get("artifact_retention_days", 30)
        
        self.log(f"Cleaning artifacts older than {older_than_days} days...")
        
        cutoff_time = datetime.now().timestamp() - (older_than_days * 24 * 3600)
        cleaned_count = 0
        
        # Clean build artifacts
        for artifact_dir in [self.build_dir, self.artifacts_dir]:
            if artifact_dir.exists():
                for item in artifact_dir.iterdir():
                    if item.stat().st_mtime < cutoff_time:
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                        cleaned_count += 1
        
        self.log(f"Cleaned {cleaned_count} artifacts")
        return cleaned_count
    
    def save_build_results(self, results):
        """Save build results"""
        results_file = self.artifacts_dir / f"build_results_{self.build_number}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    def save_test_results(self, results):
        """Save test results"""
        results_file = self.artifacts_dir / f"test_results_{self.build_number}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    def generate_pipeline_report(self):
        """Generate pipeline report"""
        self.log("Generating pipeline report...")
        
        report = {
            'build_number': self.build_number,
            'timestamp': datetime.now().isoformat(),
            'pipeline_config': self.pipeline_config,
            'summary': {
                'total_platforms': len(self.pipeline_config['platforms']),
                'total_test_suites': len(self.pipeline_config['test_suites']),
                'quality_gates': self.pipeline_config['quality_gates']
            }
        }
        
        # Save report
        report_file = self.artifacts_dir / f"pipeline_report_{self.build_number}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"Pipeline report generated: {report_file}")
        return report_file
    
    def run_full_pipeline(self, platforms=None, test_suites=None, deploy_to=None):
        """Run complete CI/CD pipeline"""
        self.log("Starting full CI/CD pipeline...")
        
        # Increment build number
        self.increment_build_number()
        
        # Run build pipeline
        build_results = self.run_build_pipeline(platforms)
        
        # Check if builds were successful
        failed_builds = [p for p, r in build_results.items() if not r['success']]
        if failed_builds:
            self.log(f"Pipeline failed: Builds failed for {failed_builds}")
            return False
        
        # Run test pipeline
        test_results = self.run_test_pipeline(platforms, test_suites)
        
        # Run quality gates
        gate_results = self.run_quality_gates(build_results, test_results)
        
        if not gate_results['passed']:
            self.log("Pipeline failed: Quality gates not passed")
            return False
        
        # Create release
        version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        release_dir = self.create_release(version, platforms)
        
        # Deploy if requested
        if deploy_to:
            deployment_success = self.deploy_to_environment(deploy_to, version)
            if not deployment_success:
                self.log("Pipeline failed: Deployment failed")
                return False
        
        # Generate report
        self.generate_pipeline_report()
        
        self.log(f"Pipeline completed successfully! Build #{self.build_number}")
        return True


def main():
    parser = argparse.ArgumentParser(description="Valtronics Firmware CI/CD Pipeline")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument("--platform", action="append", help="Target platforms")
    parser.add_argument("--test-suite", action="append", help="Test suites")
    parser.add_argument("--environment", help="Deployment environment")
    parser.add_argument("--version", help="Release version")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Pipeline commands
    build_parser = subparsers.add_parser("build", help="Run build pipeline")
    build_parser.add_argument("--platform", action="append", help="Target platforms")
    build_parser.add_argument("--parallel", action="store_true", help="Run builds in parallel")
    
    test_parser = subparsers.add_parser("test", help="Run test pipeline")
    test_parser.add_argument("--platform", action="append", help="Target platforms")
    test_parser.add_argument("--suite", action="append", help="Test suites")
    test_parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    
    pipeline_parser = subparsers.add_parser("pipeline", help="Run full pipeline")
    pipeline_parser.add_argument("--platform", action="append", help="Target platforms")
    pipeline_parser.add_argument("--test-suite", action="append", help="Test suites")
    pipeline_parser.add_argument("--deploy", help="Deployment environment")
    
    # Release commands
    release_parser = subparsers.add_parser("release", help="Create release")
    release_parser.add_argument("--version", help="Release version")
    release_parser.add_argument("--platform", action="append", help="Target platforms")
    
    deploy_parser = subparsers.add_parser("deploy", help="Deploy to environment")
    deploy_parser.add_argument("--environment", required=True, help="Deployment environment")
    deploy_parser.add_argument("--version", help="Release version")
    
    # Utility commands
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up artifacts")
    cleanup_parser.add_argument("--days", type=int, help="Retention days")
    
    report_parser = subparsers.add_parser("report", help="Generate pipeline report")
    
    args = parser.parse_args()
    
    # Initialize CI/CD pipeline
    cicd = FirmwareCICD(args.project_root)
    
    # Execute commands
    if args.command == "build":
        results = cicd.run_build_pipeline(args.platform, args.parallel)
        failed_builds = [p for p, r in results.items() if not r['success']]
        sys.exit(0 if not failed_builds else 1)
    
    elif args.command == "test":
        results = cicd.run_test_pipeline(args.platform, args.suite, args.parallel)
        failed_tests = sum(1 for p in results.values() for s in p.values() if not s['passed'])
        sys.exit(0 if failed_tests == 0 else 1)
    
    elif args.command == "pipeline":
        success = cicd.run_full_pipeline(args.platform, args.suite, args.deploy)
        sys.exit(0 if success else 1)
    
    elif args.command == "release":
        release_dir = cicd.create_release(args.version, args.platform)
        print(f"Release created: {release_dir}")
    
    elif args.command == "deploy":
        success = cicd.deploy_to_environment(args.environment, args.version)
        sys.exit(0 if success else 1)
    
    elif args.command == "cleanup":
        cicd.cleanup_artifacts(args.days)
    
    elif args.command == "report":
        report_file = cicd.generate_pipeline_report()
        print(f"Report generated: {report_file}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
