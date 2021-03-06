# PDFMaker
## Simple PDF converter GUI for Pictures using Image-Magick
Version 1.0.1
![Download](https://github.com/kanehekili/PDFMaker/raw/master/build/PDFMaker1.0.1.tar)

This simple program is written in python 3 with the GTK3 Library. Drag'n drop files (png, jpg, etc) onto the list and convert these files into one PDF with a simple click
![Screenshot](https://github.com/kanehekili/PDFMaker/blob/master/PDFMaker.png)

## Prerequisites
* python 3.x
* image-magick
* ghostscript (gs)

### How to install
* Download the PDFMaker*.tar contained in the "build" folder ![here](https://github.com/kanehekili/PDFMaker/raw/master/build/PDFMaker1.0.1.tar)
* Unpack it and run the command  **sudo ./install.sh** in the unpacked folder.
* Install just copies a desktop file and some python scripts to /usr/local/sbin/PDFMaker
* You can now remove the unpacked files in your current download directory.

### Limitations
Can only convert files that image-magick or ghostscript support. So either only image files, or only PDFs files. Not mixed.

###Merging PDFs
Since merging PDFs is a close thing to merging pictures, a seconds API is using "ghostscript" to join pdfs. Note that you can't merge pdfs and images with goods results.  

#### Security issues
ImageMagick not authorized to convert PDF to an image. Change in /etc/ImageMagick-6/policy.xml this line:

```
 <!-- <policy domain="coder" rights="none" pattern="{PS,PS2,PS3,EPS,PDF,XPS}" /> -->
```

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

29.12.2019
Added PDF support, easy install scripts 