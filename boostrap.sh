if [ -d "cira-colab-trainer" ] 
then
    rm -rf cira-colab-trainer 
fi

git clone -b main --depth=1 http://git.cira-lab.com/cira/cira-colab-trainer.git

cd cira-colab-trainer
unzip -qq install.zip && cp -r install /root 


mkdir -p /root/.cira_core_install/share
unzip -qq d.zip && cp -r d /root/.cira_core_install/share

echo -e """\e[1;32m******  ********\e[1m"""

# instaall ros
sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
apt-get update
apt-get install ros-melodic-ros-base -y

