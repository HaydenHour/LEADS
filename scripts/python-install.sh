if ! sudo -v &>/dev/null;
then
  echo "Error: This script requires root permission"
  exit 1
fi
sudo su
apt update
apt install python3.11
apt install python3-tk
apt install python3-rpi.gpi