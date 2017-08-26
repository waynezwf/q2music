# q2music
 Q2Music is an online music player.

# install plugins
 First you need install ffmpeg, PySide, PyAudio and PortAudio.

# download source code
 Then you need to download the source code to you installation folder.

# create shell command file
 In the installation folder we create a file named "q2music" and input:
 
 #!/bin/bash
 python (your installation folder)/src/qqmusic.py
 
# create shortcut
 Sample For Fedora, in /usr/share/applications create a file named "q2music.desktop" and input:
 
 [Desktop Entry]
 Name=Q2Music
 Exec=(your installation folder)
 Icon=(your installation folder)/res/icons/qq_music.png
 Type=Application
 Categories=Application;Development
 Terminal=false
 StartupNotify=true
 
