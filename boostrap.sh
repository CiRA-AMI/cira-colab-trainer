git clone -b main --depth=1 http://git.cira-lab.com/cira/cira-core-android-termux.git

cd cira-core-android-termux
unzip  ros.zip && cp -r ros /data/data/com.termux/files/home/ 


mkdir /data/data/com.termux/files/home/.cira_core_install
unzip install.zip && cp -r install /data/data/com.termux/files/home/.cira_core_install/

pip3 install defusedxml rospkg netifaces
#dpkg -i libs/qt5-qtbase_5.15.3-4_with_opengl_aarch64.deb

chmod +x bin/*
cp -r bin/* /data/data/com.termux/files/usr/bin/

cp release_notes.txt ~/.cira_core_install/

cp -r UbuntuFonts/*.ttf /data/data/com.termux/files/usr/share/fonts

cp -r icons ~/.cira_core_install/
cp -r shortcuts/* ~/Desktop/
chmod +x ~/Desktop/CiRA\ CORE.desktop
chmod +x ~/Desktop/CiRA\ CORE\ Debug.desktop
chmod +x ~/Desktop/CiRA\ CORE\ GDB.desktop
#for i in ~/Desktop/*.desktop; do gio set "$i" "metadata::trusted" yes ;done

cd ..
rm -rf cira-core-android-termux
apt install -f
echo "------------"
echo -e """\e[1;32m****** Welcome to CiRA CORE Android Termux ********\e[1m"""