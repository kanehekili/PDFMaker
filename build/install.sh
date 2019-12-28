#!/bin/bash
#check if sudo
if [ "$EUID" -ne 0 ] ; then
  echo "Sorry, but you are not root. Use sudo to run"
  exit 1
fi
#copy desktop to /usr/share applications
sudo cp PDFMaker.desktop /usr/share/applications;
sudo mkdir -p /usr/local/bin/PDFMaker;
sudo cp * /usr/local/bin/PDFMaker/;

echo "####################################################"
echo "#   Ensure you have installed:                     #"                     
echo "#       *imagemagick                               #"
echo "#       *ghostscript                               #"
echo "####################################################"
echo "App installed."