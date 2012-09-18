echo "Enter your computer password:"
sudo echo "Thanks!"

sudo apt-get -y install python-qt4 python-mechanize
chmod 755 MoodleSync.sh
sh MoodleSync.sh
rm install.sh
