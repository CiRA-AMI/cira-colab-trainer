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
#sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
#apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
#apt update
#apt install -y ros-noetic-ros-base 

apt update
apt install -y ros-base

# opencv
unzip -qq -o opencv_install.zip
cp -r install/* /usr/local/
rm -r install


############ cuda && cudnn #############################
#apt install -y libcudnn8=8.1.1.33-1+cuda11.2

    #apt-key del 7fa2af80
    #wget -P /tmp/ https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
    #mv /tmp/cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
    #apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub
    #add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /" -y
    #apt-get update
    
    NV_CUDA_LIB_VERSION=11.8.0-1

    NV_NVTX_VERSION=11.8.86-1
    NV_LIBNPP_VERSION=11.8.0.86-1
    NV_LIBNPP_PACKAGE=libnpp-11-8=${NV_LIBNPP_VERSION}
    NV_LIBCUSPARSE_VERSION=11.7.5.86-1

    NV_LIBCUBLAS_PACKAGE_NAME=libcublas-11-8
    NV_LIBCUBLAS_VERSION=11.11.3.6-1
    NV_LIBCUBLAS_PACKAGE=${NV_LIBCUBLAS_PACKAGE_NAME}=${NV_LIBCUBLAS_VERSION}

    NV_LIBNCCL_PACKAGE_NAME=libnccl2
    NV_LIBNCCL_PACKAGE_VERSION=2.15.5-1
    NCCL_VERSION=2.15.5-1
    NV_LIBNCCL_PACKAGE=${NV_LIBNCCL_PACKAGE_NAME}=${NV_LIBNCCL_PACKAGE_VERSION}+cuda11.8
    NV_LIBNCCL_DEVPACKAGE=libnccl-dev=${NV_LIBNCCL_PACKAGE_VERSION}+cuda11.8

    apt install -y --no-install-recommends --allow-downgrades --allow-change-held-packages \
    cuda-libraries-11-8=${NV_CUDA_LIB_VERSION} \
    ${NV_LIBNPP_PACKAGE} \
    cuda-nvtx-11-8=${NV_NVTX_VERSION} \
    libcusparse-11-8=${NV_LIBCUSPARSE_VERSION} \
    ${NV_LIBCUBLAS_PACKAGE} \
    ${NV_LIBNCCL_PACKAGE} ${NV_LIBNCCL_DEVPACKAGE} 
    
    #for dev
    #apt install -y --no-install-recommends --allow-downgrades cuda-libraries-dev-11-8=${NV_CUDA_LIB_VERSION} cuda-toolkit-11-8=${NV_CUDA_LIB_VERSION}
    
    apt-get -y -o Dpkg::Options::="--force-overwrite" install -f
    ln -sfn /usr/local/cuda-11.8 /usr/local/cuda
    
    NV_CUDNN_VERSION=8.7.0.84
    NV_CUDNN_PACKAGE_NAME="libcudnn8"
    NV_CUDNN_PACKAGE="libcudnn8=$NV_CUDNN_VERSION-1+cuda11.8"
    NV_CUDNN_DEV_PACKAGE="libcudnn8-dev=$NV_CUDNN_VERSION-1+cuda11.8"

    apt install -y --no-install-recommends --allow-downgrades --allow-change-held-packages ${NV_CUDNN_PACKAGE} 
    apt-mark hold ${NV_CUDNN_PACKAGE_NAME}
    
    #for dev
	# sudo apt install -y --no-install-recommends --allow-downgrades ${NV_CUDNN_PACKAGE} ${NV_CUDNN_DEV_PACKAGE}

###########################################################

# install Others
apt install -y libqt5widgets5 libqt5opengl5 libqt5network5 -y
#libgstreamer1.0-0 libgstreamer-plugins-base1.0-0 -y

echo -e """\e[1;32m******  ********\e[1m"""
