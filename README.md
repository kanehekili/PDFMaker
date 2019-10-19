# PDFMaker
## Simple PDF converter GUI for Pictures using Image-Magick

This simple program is written in python 3 with the GTK3 Library. Drag'n drop files (png, jpg, etc) onto the list and convert these files into one PDF with a simple click
![Screenshot](https://github.com/kanehekili/PDFMaker/blob/master/PDFMaker.png)

## Prerequisites
* python 3.x
* image-magick

### Limitations
Can only convert files that image-magick can. So mostly image files, no text files.

Tested with
* Nemo (Cinnamon)
* Files(former Nautilus Gnome) 
* Thunar (XFCE)
* PcManFm Browser (LXDE) so far

### Thanks
To Erich, whose idea this was

### Changes
21.07.2018
First commit

28.07.2018
Fixed some UI features + support for URI calls from File explorers

19.10.2019
Adapted to new GTK API - removed deprecation Warnings
