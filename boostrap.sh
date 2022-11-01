if [ -d "cira-colab-trainer-main" ] 
then
    rm -rf cira-colab-trainer-main 
fi

if [[ -f "cira-colab-trainer-main.zip" ]]
then
    rm -rf cira-colab-trainer-main.zip
fi

wget -O cira-colab-trainer-main.zip https://github.com/CiRA-AMI/cira-colab-trainer/archive/refs/heads/main.zip
unzip -qq cira-colab-trainer-main.zip

cd cira-colab-trainer-main
unzip -qq install.zip && cp -r install /root 
rm -r install


mkdir -p /root/.cira_core_install/share
unzip -qq d.zip && cp -r d /root/.cira_core_install/share

# install ros
sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
apt update
apt install -y ros-melodic-ros-base 

# opencv
unzip -qq -o opencv_install.zip
cp -r install/* /usr/local/
rm -r install

# cudnn
apt install -y libcudnn8=8.1.1.33-1+cuda11.2

# install Others
apt install -y libqt5widgets5 libqt5opengl5 libqt5network5 libgstreamer1.0-0 libgstreamer-plugins-base1.0-0 -y

echo -e """\e[1;32m******  ********\e[1m"""
