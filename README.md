此项目旨在handheld设备上适配屏幕键盘。

This project aims to adapt the on-screen keyboard for handheld devices.

在vboard的基础上添加了esc按键，shift切换特殊字符等功能。 

Based on vboard, features such as the ESC key and special character switching via Shift have been added.

主要适用于wayland。

Mainly suitable for Wayland.


### **For BazziteOS distributions**  
```bash
rpm-ostree install python3-uinput
```

### **2. Download vboard**  
Retrieve the latest version of `vboard.py` using `wget`:  
```bash
wget https://github.com/Decbuan/vboard-handheld/releases/download/vboard-handheld/vboard.py
```

### **3. Create an executable application**  
```bash
mkdir -p ~/.local/share/applications
nano ~/.local/share/applications/vboard.desktop
```
```bash
[Desktop Entry]
Name=VBoard
Comment=Run vboard.py
Exec=python3 vboard.py
Icon=/path/to/icon.png  
Terminal=false  
Type=Application
Categories=Utility;
```

### **4. "Find in Start Menu → Pin to Taskbar/Desktop → Click to launch."**  

# vboard
*A virtual keyboard for Linux with Wayland support and extensive customization options.*


## Overview
vboard is a lightweight, customizable virtual keyboard designed for Linux systems with Wayland support. It provides an on-screen keyboard solution that's especially useful for:

- Touchscreen devices without physical keyboards
- Systems with malfunctioning physical keyboards
- Accessibility needs
- Kiosk applications

The keyboard supports customizable colors, opacity settings, and can be easily modified to support different layouts.

## Features
- **Customizable appearance**: Change background color, text color, and opacity
- **Persistent settings**: Configuration is saved between sessions
- **Modifier key support**: Use Shift, Ctrl, Alt and Super keys
- **Compact interface**: Headerbar with minimal controls to save screen space
- **Always-on-top**: Stays above other windows for easy access


## License
vboard is licensed under the GNU Lesser General Public License v2.1. See LICENSE.md for the full license text.

## Note
Currently, only the QWERTY US layout is supported, so other layouts may cause some keys to produce different keystrokes. BUT this could easily be fixed by modifying the row list arrangement
