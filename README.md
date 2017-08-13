```sh
sudo apt-get update -y
sudo apt-get upgrade -y

adduser ship
gpasswd -a ship sudo
su ship
mkdir -p ~/.ssh ~/app
chmod 700 ~/.ssh
curl -L http://goo.gl/FXAaqw >> ~/.ssh/authorized_keys
cd ~
chmod 600 .ssh/authorized_keys


ssh ship@XXX.XXX.XXX.XXX -p2200


sudo apt-get install -y python-software-properties software-properties-common htop nginx  git
sudo add-apt-repository -y ppa:fkrull/deadsnakes
sudo apt-get -y update
sudo apt-get -y install python3.5-dev python-virtualenv python-pip

sudo unlink /etc/nginx/sites-enabled/default
sudo ln -s  /home/ship/app/conf/nginx.conf /etc/nginx/sites-enabled/ship.conf

su ship
git clone https://github.com/niko83/xlimb.git ~/app

sudo locale-gen en_US en_US.UTF-8
sudo dpkg-reconfigure locales

sudo pip install --upgrade virtualenv
virtualenv --python python3.5 ~/venv
source ~/venv/bin/activate
pip install -r ~/app/src/.meta/requirements.pip
echo "source /home/ship/venv/bin/activate" >> ~/.bashrc
echo "~/app/src" >> ~/.bashrc
```
