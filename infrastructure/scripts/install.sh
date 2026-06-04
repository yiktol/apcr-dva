#!/bin/bash

sudo dnf update -y

# Install Apache
sudo dnf install -y httpd.x86_64 
sudo systemctl start httpd.service
sudo systemctl enable httpd.service

# Install git
sudo dnf install -y git.x86_64
sudo git clone https://github.com/yiktol/website.git
sudo cp -R  website/coffeeshop/* /var/www/html/

# Install Stress-Ng
sudo dnf install -y stress-ng.x86_64 

# Install MariaDB and PHP
sudo dnf install -y  mariadb105.x86_64 php8.2.x86_64 php8.2-mysqlnd.x86_64
sudo wget https://docs.aws.amazon.com/aws-sdk-php/v3/download/aws.zip
sudo unzip aws.zip  -d /var/www/html/

# Install cfn-bootstrap
sudo dnf install -y aws-cfn-bootstrap.noarch

# Configure Web
sudo dnf install -y curl.x86_64 gettext.x86_64 --allowerasing

# Restart Apache Web Server
sudo systemctl restart httpd.service
