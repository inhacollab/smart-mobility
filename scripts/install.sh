#!/bin/bash
#############################################################################
# TurtleBot3 Smart Automation - Full Setup Script
# ================================================================
# Automated installation script for Ubuntu 22.04 + ROS2 Humble
# Based on official ROS2 documentation:
# https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html
#
# Author: Javokhir Yuldoshev
# Course: Smart Mobility - INHA University
# Date: December 2025
#
# This script automates the complete setup process including:
# - System requirements check
# - ROS2 Humble installation (via official debian packages)
# - TurtleBot3 packages installation
# - Workspace creation and build
# - Environment configuration
# - Python dependencies installation
#
# Usage: bash install.sh (NO sudo needed - script will ask when required)
#############################################################################

# Exit on error, but handle errors gracefully
set -e
trap 'echo -e "\n${RED}Error on line $LINENO${NC}"; exit 1' ERR

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ROS_DISTRO="humble"
WORKSPACE_DIR="$HOME/tb3_ws"
TURTLEBOT3_MODEL="burger"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Check if running as root (we don't want that)
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}ERROR: Do not run this script as root or with sudo${NC}"
    echo "The script will ask for sudo password when needed"
    exit 1
fi

echo -e "${BLUE}"
echo "============================================================================"
echo "  TurtleBot3 Smart Automation - Installation Script"
echo "============================================================================"
echo -e "${NC}"
echo "  OS: Ubuntu 22.04 (Jammy Jellyfish)"
echo "  ROS2: ${ROS_DISTRO}"
echo "  Workspace: ${WORKSPACE_DIR}"
echo "  Robot Model: ${TURTLEBOT3_MODEL}"
echo "  Project: ${PROJECT_DIR}"
echo ""
echo -e "${YELLOW}⚠️  This script will install ROS2 and TurtleBot3 packages${NC}"
echo "   Press Ctrl+C to cancel, or Enter to continue..."
read

#############################################################################
# Function: Print step header
#############################################################################
print_step() {
    echo ""
    echo -e "${BLUE}===> $1${NC}"
    echo ""
}

#############################################################################
# Function: Check if command succeeded
#############################################################################
check_result() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1 succeeded${NC}"
    else
        echo -e "${RED}❌ $1 failed${NC}"
        exit 1
    fi
}

#############################################################################
# Step 1: System Requirements Check
#############################################################################
print_step "Step 1: Checking system requirements"

# Check Ubuntu version
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "  OS: $NAME $VERSION"
    if [[ "$VERSION_ID" != "22.04" ]]; then
        echo -e "${YELLOW}  ⚠️  Warning: Ubuntu 22.04 recommended, found $VERSION_ID${NC}"
    fi
else
    echo -e "${RED}  ❌ Cannot detect OS version${NC}"
    exit 1
fi

# Check disk space (need at least 10GB)
available_space=$(df / | tail -1 | awk '{print $4}')
available_gb=$((available_space / 1024 / 1024))
echo "  Available disk space: ${available_gb} GB"
if [ $available_gb -lt 10 ]; then
    echo -e "${RED}  ❌ Insufficient disk space. Need at least 10GB${NC}"
    exit 1
fi

# Check internet connection
echo "  Testing internet connection..."
if ping -c 1 8.8.8.8 &> /dev/null; then
    echo -e "${GREEN}  ✅ Internet connection OK${NC}"
else
    echo -e "${RED}  ❌ No internet connection${NC}"
    exit 1
fi

#############################################################################
# Step 2: Install ROS2 Humble (Official Method)
#############################################################################
print_step "Step 2: Installing ROS2 Humble"

# Step 2.1: Set locale (UTF-8 support required)
echo "  Setting locale to UTF-8..."
sudo apt update && sudo apt install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
locale  # verify settings
check_result "Locale setup"

# Step 2.2: Enable Ubuntu Universe repository
echo "  Enabling Ubuntu Universe repository..."
sudo apt install -y software-properties-common
sudo add-apt-repository -y universe
check_result "Universe repository"

# Step 2.3: Install ros-apt-source package (Official ROS2 method)
echo "  Installing ROS2 apt repositories..."
sudo apt update && sudo apt install -y curl
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.jammy_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb
rm /tmp/ros2-apt-source.deb
check_result "ROS2 apt source installation"

# Step 2.4: Update apt cache and upgrade
echo "  Updating package lists..."
sudo apt update
check_result "Apt update"

# Step 2.5: Install ROS2 Desktop (full installation with RViz, demos, tutorials)
echo "  Installing ROS2 ${ROS_DISTRO}-desktop (this may take 10-15 minutes)..."
echo "  This includes: ROS core, RViz, demos, and tutorials"
sudo apt install -y ros-${ROS_DISTRO}-desktop
check_result "ROS2 ${ROS_DISTRO}-desktop installation"

# Step 2.6: Install development tools (optional but recommended)
echo "  Installing ROS development tools..."
sudo apt install -y ros-dev-tools
check_result "ROS development tools installation"

#############################################################################
# Step 3: Initialize rosdep
#############################################################################
print_step "Step 3: Initializing rosdep"

if [ ! -d "/etc/ros/rosdep" ]; then
    sudo rosdep init
    check_result "rosdep init"
fi

rosdep update
check_result "rosdep update"

#############################################################################
# Step 4: Install TurtleBot3 Packages
#############################################################################
print_step "Step 4: Installing TurtleBot3 packages"

echo "  Installing TurtleBot3 and Navigation packages..."
sudo apt install -y \
    ros-${ROS_DISTRO}-turtlebot3* \
    ros-${ROS_DISTRO}-dynamixel-sdk \
    ros-${ROS_DISTRO}-nav2-bringup \
    ros-${ROS_DISTRO}-navigation2 \
    ros-${ROS_DISTRO}-slam-toolbox \
    ros-${ROS_DISTRO}-cartographer \
    ros-${ROS_DISTRO}-cartographer-ros \
    ros-${ROS_DISTRO}-gazebo-* \
    python3-colcon-common-extensions
check_result "TurtleBot3 packages installation"

#############################################################################
# Step 5: Create Workspace (Optional - for building from source)
#############################################################################
print_step "Step 5: Creating ROS2 workspace"

echo "  Creating workspace at ${WORKSPACE_DIR}..."
mkdir -p ${WORKSPACE_DIR}/src
cd ${WORKSPACE_DIR}

# Note: Since we installed TurtleBot3 from apt packages, we don't necessarily need to build from source
# But creating a workspace is still useful for custom packages
echo "  Workspace created for custom development"
check_result "Workspace creation"

#############################################################################
# Step 6: Configure Environment
#############################################################################
print_step "Step 6: Configuring environment"

echo "  Adding ROS2 environment to .bashrc..."

# Backup .bashrc
cp ~/.bashrc ~/.bashrc.backup.$(date +%Y%m%d_%H%M%S)

# Add ROS2 setup to .bashrc if not already present
if ! grep -q "ROS2 and TurtleBot3 Environment Setup" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'

# ROS2 and TurtleBot3 Environment Setup (Auto-generated)
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=30
export TURTLEBOT3_MODEL=burger
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models
export LDS_MODEL=LDS-01
# End ROS2 Setup
EOF
    echo -e "${GREEN}  ✅ Environment configuration added to .bashrc${NC}"
else
    echo -e "${YELLOW}  ⏩ Environment already configured${NC}"
fi

# Source immediately for this session
source /opt/ros/${ROS_DISTRO}/setup.bash
export ROS_DOMAIN_ID=30
export TURTLEBOT3_MODEL=${TURTLEBOT3_MODEL}
check_result "Environment configuration"

#############################################################################
# Step 7: Install Python Dependencies for Smart Automation
#############################################################################
print_step "Step 7: Installing Python dependencies"

echo "  Installing Python packages for vision, gesture control, and monitoring..."
pip3 install --user -q \
    pyyaml \
    psutil \
    ultralytics \
    opencv-python \
    mediapipe \
    numpy
check_result "Python dependencies installation"

#############################################################################
# Step 8: Setup Project Files
#############################################################################
print_step "Step 8: Setting up project files"

echo "  Making scripts executable..."
chmod +x "${SCRIPT_DIR}"/*.sh
chmod +x "${PROJECT_DIR}/main.py" 2>/dev/null || true
check_result "Script permissions"

#############################################################################
# Step 9: Verification
#############################################################################
print_step "Step 9: Verifying installation"

echo "  Checking ROS2 installation..."
if command -v ros2 &> /dev/null; then
    echo -e "${GREEN}  ✅ ros2 command available${NC}"
    echo "  ROS2 Humble is installed"
else
    echo -e "${RED}  ❌ ros2 command not found${NC}"
    echo -e "${YELLOW}  You may need to open a new terminal or run: source ~/.bashrc${NC}"
fi

echo "  Checking TurtleBot3 packages..."
if dpkg -l | grep -q ros-${ROS_DISTRO}-turtlebot3; then
    echo -e "${GREEN}  ✅ TurtleBot3 packages installed${NC}"
else
    echo -e "${YELLOW}  ⚠️  TurtleBot3 packages may not be properly installed${NC}"
fi

echo "  Checking Python dependencies..."
python3 -c "import yaml, psutil, cv2, mediapipe" 2>/dev/null && echo -e "${GREEN}  ✅ Core Python packages available${NC}" || echo -e "${YELLOW}  ⚠️  Some Python packages may be missing${NC}"

#############################################################################
# Completion
#############################################################################
echo ""
echo -e "${GREEN}"
echo "============================================================================"
echo "  ✅ INSTALLATION COMPLETED SUCCESSFULLY!"
echo "============================================================================"
echo -e "${NC}"
echo ""
echo "📝 Next Steps:"
echo "  1. Open a NEW terminal (or source environment in current terminal):"
echo "     ${YELLOW}source ~/.bashrc${NC}"
echo ""
echo "  2. Verify ROS2 installation:"
echo "     ${YELLOW}ros2 --version${NC}"
echo "     ${YELLOW}ros2 pkg list | grep turtlebot3${NC}"
echo ""
echo "  3. Test TurtleBot3 simulation:"
echo "     ${YELLOW}export TURTLEBOT3_MODEL=burger${NC}"
echo "     ${YELLOW}ros2 launch turtlebot3_gazebo empty_world.launch.py${NC}"
echo ""
echo "  4. Run the Smart Automation system:"
echo "     ${YELLOW}cd ${PROJECT_DIR}${NC}"
echo "     ${YELLOW}python3 main.py --help${NC}"
echo ""
echo "  5. Try a quick demo:"
echo "     ${YELLOW}python3 main.py setup --check${NC}"
echo ""
echo "============================================================================"
echo ""
echo "💡 Tips:"
echo "  - All configuration is in: ${PROJECT_DIR}/config/system_config.yaml"
echo "  - Test scripts are in: ${SCRIPT_DIR}/"
echo "  - Documentation is in: ${PROJECT_DIR}/README.md"
echo "  - Your .bashrc was backed up before modification"
echo ""
echo "⚠️  If you encounter issues:"
echo "  1. Check system requirements: Ubuntu 22.04, 10GB+ disk space"
echo "  2. Verify internet connection"
echo "  3. Try re-sourcing: source ~/.bashrc"
echo "  4. Check logs in /tmp/ directory"
echo ""
echo "============================================================================"
