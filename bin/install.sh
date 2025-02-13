# name
APP_NAME="photoframepi"

# directories 
SRC_DIR=$(dirname $(readlink -f $0))
APP_DIR="/usr/local/$APP_NAME"
VENV_DIR="$APP_DIR/.venv"
BIN_DIR="/usr/local/bin"

# requirements
PIP_REQ="$APP_DIR/install/requirements.txt"
APT_REQ="$APP_DIR/install/apt-requirements.txt"

# service
SERVICE_FILE="$APP_NAME.service"
SERVICE_SOURCE="$SRC_DIR/install/$SERVICE_FILE"
SERVICE_TARGET="/etc/systemd/system/$SERVICE_FILE"

# Ensure the script is run with sudo
check_permissions() {
  if [ "$EUID" -ne 0 ]; then
    echo_error "ERROR: Installation requires root privileges. Please run it with sudo."
    exit 1
  fi
}

# Stop the service if it is running
stop_service() {
    echo "Checking if $SERVICE_FILE is running"
    if /usr/bin/systemctl is-active --quiet $SERVICE_FILE
    then
      /usr/bin/systemctl stop $SERVICE_FILE > /dev/null &
      show_loader "Stopping $APP_NAME service"
    else  
      echo_success "\t$SERVICE_FILE not running"
    fi
}

# Enable hardware interfaces required for the application
enable_interfaces(){
  echo "Enabling interfaces required for $APPNAME"
  #enable spi
  sudo sed -i 's/^dtparam=spi=.*/dtparam=spi=on/' /boot/config.txt
  sudo sed -i 's/^#dtparam=spi=.*/dtparam=spi=on/' /boot/config.txt
  sudo raspi-config nonint do_spi 0
  echo_success "\tSPI Interface has been enabled."
  #enable i2c
  sudo sed -i 's/^dtparam=i2c_arm=.*/dtparam=i2c_arm=on/' /boot/config.txt
  sudo sed -i 's/^#dtparam=i2c_arm=.*/dtparam=i2c_arm=on/' /boot/config.txt
  sudo raspi-config nonint do_i2c 0
  echo_success "\tI2C Interface has been enabled."
  sed -i '/^dtparam=spi=on/a dtoverlay=spi0-0cs' /boot/firmware/config.txt
}

# Install apt dependencies
install_apt_dependencies() {
  if [ -f "$APT_REQ" ]; then
    xargs -a "$APT_REQ" sudo apt-get install -y > /dev/null &
    show_loader "Installing system dependencies. "
  else
    echo "ERROR: System dependencies file $APT_REQ not found!"
    exit 1
  fi
}

# Symlink the project to the installation directory
symlink_project() {
  # Check if an existing installation is present
  echo "Installing $APP_NAME to $APP_DIR"
  if [[ -d $APP_DIR ]]; then
    rm -rf "$APP_DIR" > /dev/null
    show_loader "\tRemoving existing installation found at $APP_DIR"
  fi

  mkdir -p "$APP_DIR"

  ln -sf "$SRC_DIR" "$APP_DIR"
  show_loader "\tCreating symlink from $SRC_DIR to $APP_DIR"
}

# Install the executable in the bin directory
install_executable() {
  echo "Adding executable to ${BIN_DIR}/$APP_NAME"
  cp $SRC_DIR/install/$APP_NAME $BIN_DIR/
  sudo chmod +x $BIN_DIR/$APP_NAME
}

# Install python dependencies
create_venv(){
  echo "Creating python virtual environment. "
  python3 -m venv "$VENV_DIR"
  $VENV_DIR/bin/python -m pip install -r $PIP_REQ > /dev/null &
  show_loader "\tInstalling python dependencies. "
}

# Install the systemd service
install_app_service() {
  echo "Installing $APP_NAME systemd service."
  if [ -f "$SERVICE_SOURCE" ]; then
    cp "$SERVICE_SOURCE" "$SERVICE_TARGET"
    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_FILE
  else
    echo_error "ERROR: Service file $SERVICE_SOURCE not found!"
    exit 1
  fi
}

# Get Raspberry Pi hostname
get_hostname() {
  echo "$(hostname)"
}

# Get Raspberry Pi IP address
get_ip_address() {
  ip_address=$(hostname -I | awk '{print $1}')
  echo "$ip_address"
}

# Ask for system to be rebooted so the service starts automatically
ask_for_reboot() {
  # Get hostname and IP address
  hostname=$(get_hostname)
  ip_address=$(get_ip_address)
  echo_header "$(echo_success "${APPNAME^^} Installation Complete!")"
  echo_header "[•] A reboot of your Raspberry Pi is required for the changes to take effect"
  echo_header "[•] After your Pi is rebooted, you can access the web UI by going to $(echo_blue "'$hostname'") or $(echo_blue "'$ip_address'") in your browser."

  read -p "Would you like to restart your Raspberry Pi now? [Y/N] " userInput
  userInput="${userInput^^}"

  if [[ "${userInput,,}" == "y" ]]; then
    echo_success "You entered 'Y', rebooting now..."
    sleep 2
    sudo reboot now
  elif [[ "${userInput,,}" == "n" ]]; then
    echo "Please restart your Raspberry Pi later to apply changes by running 'sudo reboot now'."
    exit
  else
    echo "Unknown input, please restart your Raspberry Pi later to apply changes by running 'sudo reboot now'."
    sleep 1
  fi
}

# ------------------ Helper functions ------------------

# Display a spinner while the process is running
show_loader() {
  local pid=$!
  local delay=0.1
  local spinstr='|/-\'
  printf "$1 [${spinstr:0:1}] "
  while ps a | awk '{print $1}' | grep -q "${pid}"; do
    local temp=${spinstr#?}
    printf "\r$1 [${temp:0:1}] "
    spinstr=${temp}${spinstr%"${temp}"}
    sleep ${delay}
  done
  if [[ $? -eq 0 ]]; then
    printf "\r$1 [\e[32m\xE2\x9C\x94\e[0m]\n"
  else
    printf "\r$1 [\e[31m\xE2\x9C\x98\e[0m]\n"
  fi
}

# Message formatting
bold=$(tput bold)
normal=$(tput sgr0)
red=$(tput setaf 1)
green=$(tput setaf 2)

echo_success() {
  echo -e "$1 [\e[32m\xE2\x9C\x94\e[0m]"
}

echo_override() {
  echo -e "\r$1"
}

echo_header() {
  echo -e "${bold}$1${normal}"
}

echo_error() {
  echo -e "${red}$1${normal} [\e[31m\xE2\x9C\x98\e[0m]\n"
}

echo_blue() {
  echo -e "\e[38;2;65;105;225m$1\e[0m"
}


check_permissions
stop_service
enable_interfaces
install_apt_dependencies
symlink_project
create_venv
install_app_service
ask_for_reboot