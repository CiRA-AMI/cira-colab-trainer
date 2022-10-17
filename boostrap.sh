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
