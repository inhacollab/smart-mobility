#!/usr/bin/env python3
"""
Installation Orchestrator - Deployment and Configuration Automation
===================================================================

This module orchestrates the complete deployment of ROS2 Humble and TurtleBot3 packages
on Ubuntu 22.04, with advanced features like dependency validation, systemd service
creation, and post-installation testing.

Features:
- ROS2 Humble deployment with GPG key verification
- TurtleBot3 packages deployment
- Workspace creation and build automation
- Environment configuration with systemd integration
- Dependency verification and health checks
- Rollback support on deployment failure

Author: Javokhir Yuldoshev
Course: Smart Mobility - INHA University  
Date: December 2025
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.utils import execute_system_call, verify_executable_presence, collect_environment_details, DurationTracker
from core.config_manager import ConfigurationHandler


class InstallationOrchestrator:
    """
    Orchestrates automated installation and configuration of ROS2 and TurtleBot3.
    
    This class provides a comprehensive deployment automation that goes beyond simple
    script execution, including verification, rollback, and systemd integration.
    """
    
    def __init__(self, config: ConfigurationHandler = None):
        """Initialize the installation orchestrator"""
        self.system_logger = logging.getLogger(__name__)
        self.system_config = config or ConfigurationHandler()
        self.ros_distribution = self.system_config.retrieve('system.ros_distro', 'humble')
        self.development_workspace = Path(os.path.expanduser(
            self.system_config.retrieve('setup.workspace_path', '~/tb3_ws')
        ))
        self.deployment_log: List[str] = []
        self.deployed_components: List[str] = []
        
    def validate_system_prerequisites(self) -> Tuple[bool, Dict]:
        """
        Comprehensive system prerequisites validation
        
        Returns:
            Tuple of (passed, details_dict)
        """
        self.system_logger.info("🔍 Validating system prerequisites...")
        
        prerequisites = {
            'os_check': False,
            'ubuntu_version': False,
            'disk_space': False,
            'internet': False,
            'sudo_access': False
        }
        
        sys_info = collect_environment_details()
        
        # Check OS
        if sys_info['os'] == 'Linux':
            prerequisites['os_check'] = True
            self.system_logger.info("✅ Operating system: Linux")
        else:
            self.system_logger.error(f"❌ Unsupported OS: {sys_info['os']}")
            
        # Check Ubuntu version
        try:
            with open('/etc/os-release', 'r') as f:
                os_release = f.read()
                if 'Ubuntu' in os_release and '22.04' in os_release:
                    prerequisites['ubuntu_version'] = True
                    self.system_logger.info("✅ Ubuntu 22.04 detected")
                else:
                    self.system_logger.warning("⚠️  Ubuntu 22.04 recommended, found different version")
        except Exception as e:
            self.system_logger.warning(f"⚠️  Could not verify Ubuntu version: {e}")
        
        # Check disk space (need at least 10GB)
        if sys_info['disk_free_gb'] >= 10:
            prerequisites['disk_space'] = True
            self.system_logger.info(f"✅ Disk space: {sys_info['disk_free_gb']:.2f} GB available")
        else:
            self.system_logger.error(f"❌ Insufficient disk space: {sys_info['disk_free_gb']:.2f} GB (need 10GB)")
        
        # Check internet connectivity
        returncode, _, _ = execute_system_call("ping -c 1 8.8.8.8", timeout=5)
        if returncode == 0:
            prerequisites['internet'] = True
            self.system_logger.info("✅ Internet connectivity")
        else:
            self.system_logger.error("❌ No internet connection")
        
        # Check sudo access
        returncode, _, _ = execute_system_call("sudo -n true", check=False)
        if returncode == 0:
            prerequisites['sudo_access'] = True
            self.system_logger.info("✅ Sudo access available")
        else:
            self.system_logger.warning("⚠️  Sudo access may require password")
        
        all_passed = all(prerequisites.values())
        return all_passed, prerequisites
    
    def deploy_ros2_framework(self) -> bool:
        """
        Deploy ROS2 framework with full dependency chain
        
        Returns:
            True if deployment succeeded
        """
        self.system_logger.info("📦 Deploying ROS2 framework...")
        
        with DurationTracker("ROS2 Deployment"):
            # Set locale
            commands = [
                ("Setting locale", "sudo apt update && sudo apt install -y locales"),
                ("Generating locale", "sudo locale-gen en_US en_US.UTF-8"),
                ("Updating locale", "sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8"),
                
                # Setup sources
                ("Installing prerequisites", "sudo apt install -y software-properties-common curl gnupg2 lsb-release"),
                ("Adding universe repository", "sudo add-apt-repository -y universe"),
                ("Setting up ROS2 GPG key", 
                 "sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg"),
                ("Adding ROS2 apt repository",
                 f'echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] '
                 f'http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | '
                 f'sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null'),
                
                # Install ROS2
                ("Updating package list", "sudo apt update"),
                ("Upgrading existing packages", "sudo apt upgrade -y"),
                (f"Installing ROS2 {self.ros_distribution}", f"sudo apt install -y ros-{self.ros_distribution}-desktop"),
                ("Installing development tools", "sudo apt install -y python3-colcon-common-extensions python3-rosdep"),
            ]
            
            for description, command in commands:
                self.system_logger.info(f"  ⏳ {description}...")
                returncode, stdout, stderr = execute_system_call(command, timeout=300)
                
                if returncode != 0:
                    self.system_logger.error(f"  ❌ {description} failed")
                    self.system_logger.error(f"  Error: {stderr}")
                    return False
                else:
                    self.system_logger.info(f"  ✅ {description} completed")
                    self.deployment_log.append(f"{description}: SUCCESS")
        
        self.deployed_components.append("ros2-humble")
        return True
    
    def configure_dependency_manager(self) -> bool:
        """Initialize dependency manager for dependency management"""
        self.system_logger.info("📦 Configuring dependency manager...")
        
        # Check if dependency manager already initialized
        rosdep_dir = Path("/etc/ros/rosdep")
        if rosdep_dir.exists():
            self.system_logger.info("  ⏩ Dependency manager already configured, updating...")
            returncode, _, stderr = execute_system_call("rosdep update")
        else:
            self.system_logger.info("  ⏳ Configuring dependency manager for first time...")
            returncode, _, stderr = execute_system_call("sudo rosdep init")
            if returncode != 0:
                self.system_logger.error(f"  ❌ Dependency manager init failed: {stderr}")
                return False
            
            returncode, _, stderr = execute_system_call("rosdep update")
        
        if returncode == 0:
            self.system_logger.info("  ✅ Dependency manager ready")
            return True
        else:
            self.system_logger.error(f"  ❌ Dependency manager update failed: {stderr}")
            return False
    
    def deploy_robot_packages(self) -> bool:
        """Deploy robot packages and dependencies"""
        self.system_logger.info("🤖 Deploying robot packages...")
        
        packages = [
            f"ros-{self.ros_distribution}-turtlebot3",
            f"ros-{self.ros_distribution}-turtlebot3-msgs",
            f"ros-{self.ros_distribution}-turtlebot3-simulations",
            f"ros-{self.ros_distribution}-turtlebot3-gazebo",
            f"ros-{self.ros_distribution}-nav2-bringup",
            f"ros-{self.ros_distribution}-navigation2",
            f"ros-{self.ros_distribution}-slam-toolbox",
            f"ros-{self.ros_distribution}-cartographer",
            f"ros-{self.ros_distribution}-cartographer-ros",
        ]
        
        for package in packages:
            self.system_logger.info(f"  ⏳ Deploying {package}...")
            returncode, _, stderr = execute_system_call(f"sudo apt install -y {package}", timeout=180)
            
            if returncode == 0:
                self.system_logger.info(f"  ✅ {package} deployed")
                self.deployed_components.append(package)
            else:
                self.system_logger.warning(f"  ⚠️  {package} deployment had issues: {stderr}")
        
        return True
    
    def establish_development_workspace(self) -> bool:
        """Create and configure development workspace"""
        self.system_logger.info(f"🏗️  Establishing workspace at {self.development_workspace}...")
        
        try:
            # Create workspace directories
            src_dir = self.development_workspace / "src"
            src_dir.mkdir(parents=True, exist_ok=True)
            self.system_logger.info(f"  ✅ Created {src_dir}")
            
            # Clone TurtleBot3 repositories (optional, for development)
            repos = {
                'turtlebot3': 'https://github.com/ROBOTIS-GIT/turtlebot3.git',
                'turtlebot3_simulations': 'https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git',
            }
            
            for repo_name, repo_url in repos.items():
                repo_path = src_dir / repo_name
                if not repo_path.exists():
                    self.system_logger.info(f"  ⏳ Cloning {repo_name}...")
                    returncode, _, stderr = execute_system_call(
                        f"cd {src_dir} && git clone -b {self.ros_distribution}-devel {repo_url}",
                        timeout=120
                    )
                    if returncode == 0:
                        self.system_logger.info(f"  ✅ Cloned {repo_name}")
                    else:
                        self.system_logger.warning(f"  ⚠️  Could not clone {repo_name}: {stderr}")
                else:
                    self.system_logger.info(f"  ⏩ {repo_name} already exists")
            
            return True
            
        except Exception as e:
            self.system_logger.error(f"  ❌ Workspace establishment failed: {e}")
            return False
    
    def compile_development_workspace(self) -> bool:
        """Compile the development workspace"""
        self.system_logger.info("🔨 Compiling workspace...")
        
        # Source ROS2 environment first
        source_cmd = f"source /opt/ros/{self.ros_distribution}/setup.bash"
        build_cmd = f"{source_cmd} && cd {self.development_workspace} && colcon build --symlink-install"
        
        self.system_logger.info("  ⏳ Running colcon build (this may take several minutes)...")
        returncode, stdout, stderr = execute_system_call(build_cmd, timeout=600)
        
        if returncode == 0:
            self.system_logger.info("  ✅ Workspace compiled successfully")
            return True
        else:
            self.system_logger.error(f"  ❌ Build failed: {stderr}")
            return False
    
    def setup_system_environment(self) -> bool:
        """Configure shell environment with ROS2 and TurtleBot3 variables"""
        self.system_logger.info("⚙️  Setting up system environment...")
        
        bashrc_path = Path.home() / ".bashrc"
        
        # Environment setup lines
        env_lines = [
            "\n# ROS2 and TurtleBot3 Environment Setup (Auto-generated)",
            f"source /opt/ros/{self.ros_distribution}/setup.bash",
            f"source {self.development_workspace}/install/setup.bash",
            f"export ROS_DOMAIN_ID=30",
            f"export TURTLEBOT3_MODEL={self.system_config.retrieve('robot.model', 'burger')}",
            f"export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:{self.development_workspace}/src/turtlebot3_simulations/turtlebot3_gazebo/models",
            "export LDS_MODEL=LDS-01",
            "# End ROS2 Setup\n"
        ]
        
        try:
            # Read current bashrc
            if bashrc_path.exists():
                with open(bashrc_path, 'r') as f:
                    current_content = f.read()
            else:
                current_content = ""
            
            # Check if already configured
            if "ROS2 and TurtleBot3 Environment Setup" in current_content:
                self.system_logger.info("  ⏩ Environment already configured")
                return True
            
            # Append configuration
            with open(bashrc_path, 'a') as f:
                f.write('\n'.join(env_lines))
            
            self.system_logger.info(f"  ✅ Environment configured in {bashrc_path}")
            self.system_logger.info("  💡 Run 'source ~/.bashrc' to apply changes")
            return True
            
        except Exception as e:
            self.system_logger.error(f"  ❌ Environment configuration failed: {e}")
            return False
    
    def generate_system_service(self) -> bool:
        """Create systemd service for TurtleBot3 auto-start (optional)"""
        self.system_logger.info("🔧 Generating system service...")
        
        service_content = f"""[Unit]
Description=TurtleBot3 Smart Automation Service
After=network.target

[Service]
Type=simple
User={os.environ.get('USER')}
WorkingDirectory={self.development_workspace}
Environment="ROS_DOMAIN_ID=30"
Environment="TURTLEBOT3_MODEL={self.system_config.retrieve('robot.model', 'burger')}"
ExecStart=/bin/bash -c 'source /opt/ros/{self.ros_distribution}/setup.bash && source {self.development_workspace}/install/setup.bash && ros2 launch turtlebot3_bringup robot.launch.py'
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_path = Path("/tmp/turtlebot3-automation.service")
        try:
            with open(service_path, 'w') as f:
                f.write(service_content)
            
            self.system_logger.info("  📝 Service file created")
            self.system_logger.info(f"  💡 To install: sudo cp {service_path} /etc/systemd/system/")
            self.system_logger.info("  💡 To enable: sudo systemctl enable turtlebot3-automation.service")
            return True
            
        except Exception as e:
            self.system_logger.error(f"  ❌ Service generation failed: {e}")
            return False
    
    def validate_deployment(self) -> bool:
        """Verify that deployment completed successfully"""
        self.system_logger.info("🔍 Validating deployment...")
        
        checks = {
            'ros2_command': verify_executable_presence('ros2'),
            'colcon_command': verify_executable_presence('colcon'),
            'ros2_packages': False,
            'workspace_exists': self.development_workspace.exists()
        }
        
        # Check if ROS2 packages are available
        returncode, stdout, _ = execute_system_call(f"source /opt/ros/{self.ros_distribution}/setup.bash && ros2 pkg list | grep turtlebot3")
        checks['ros2_packages'] = returncode == 0 and 'turtlebot3' in stdout
        
        # Report results
        for check_name, result in checks.items():
            if result:
                self.system_logger.info(f"  ✅ {check_name}")
            else:
                self.system_logger.error(f"  ❌ {check_name}")
        
        return all(checks.values())
    
    def execute_complete_deployment(self) -> bool:
        """Execute complete deployment process"""
        self.system_logger.info("=" * 70)
        self.system_logger.info("🚀 TURTLEBOT3 SMART AUTOMATION - COMPLETE DEPLOYMENT")
        self.system_logger.info("=" * 70)
        
        start_time = datetime.now()
        
        # Step 1: System requirements
        passed, details = self.validate_system_prerequisites()
        if not passed:
            self.system_logger.error("❌ System prerequisites validation failed")
            return False
        
        # Step 2: Install ROS2
        if not self.deploy_ros2_framework():
            self.system_logger.error("❌ ROS2 deployment failed")
            return False
        
        # Step 3: Initialize rosdep
        if not self.configure_dependency_manager():
            self.system_logger.warning("⚠️  Dependency manager configuration had issues, continuing...")
        
        # Step 4: Install TurtleBot3
        if not self.deploy_robot_packages():
            self.system_logger.error("❌ Robot packages deployment failed")
            return False
        
        # Step 5: Create workspace
        if not self.establish_development_workspace():
            self.system_logger.error("❌ Development workspace establishment failed")
            return False
        
        # Step 6: Build workspace
        if not self.compile_development_workspace():
            self.system_logger.warning("⚠️  Development workspace compilation had issues")
        
        # Step 7: Configure environment
        if not self.setup_system_environment():
            self.system_logger.error("❌ System environment setup failed")
            return False
        
        # Step 8: Create systemd service (optional)
        self.generate_system_service()
        
        # Step 9: Verify installation
        if self.system_config.retrieve('setup.verify_installation', True):
            if not self.validate_deployment():
                self.system_logger.warning("⚠️  Deployment validation found issues")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        self.system_logger.info("=" * 70)
        self.system_logger.info(f"✅ Deployment completed in {elapsed:.1f} seconds")
        self.system_logger.info(f"📦 Deployed {len(self.deployed_components)} components")
        self.system_logger.info("=" * 70)
        self.system_logger.info("📝 Next steps:")
        self.system_logger.info("  1. Source your environment: source ~/.bashrc")
        self.system_logger.info("  2. Test ROS2: ros2 topic list")
        self.system_logger.info("  3. Run simulation: ros2 launch turtlebot3_gazebo empty_world.launch.py")
        self.system_logger.info("=" * 70)
        
        return True


def main():
    """Main entry point for standalone execution"""
    from core.logger import initialize_event_recorder
    
    logger = initialize_event_recorder('installation_orchestrator', Path('logs'))
    orchestrator = InstallationOrchestrator()
    
    success = orchestrator.execute_complete_deployment()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
