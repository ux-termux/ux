<p align="center"><img src="https://upload.wikimedia.org/wikipedia/commons/f/f3/Termux_2.png"></p>

# Userge-X Termux 
 Userge-x fork for local termux deploys

### Requirements:
 1. 2.5 GB of free storage. 
 2. Termux app installed from GitHub or fdroid.
 3. 500-750MB of data to download everything.

### Setup

- Termux:  
    Download Latest [Termux](https://github.com/termux/termux-app/releases).  
    Run:
  ```bash
    # Change default Package Repository of Termux
    # Select single North American mirror
    #  OR
    # Default Cloudflare host
    termux-change-repo
    # Update local packages after changing mirrors.
    yes|pkg update
    yes|pkg upgrade 
    yes|apt update
    yes|apt upgrade
    # Install Proot-distro 
    apt install proot proot-distro
    proot-distro install ubuntu
  ```
  - Start Ubuntu:
  ```bash
    termux-chroot
    proot-distro login ubuntu
  ```
  - Bot:
  ```bash
  bash -c "$(curl -fsSL https://raw.githubusercontent.com/ux-termux/ux/alpha/xtra/ux_termux.sh)"
  ```

- Config:
    ```bash
    cd ~/ux
    mv xtra/sample_config.env config.env
    nano config.env
    ```
    Start the config editor.    
    Enclose [alphanumeric](https://www.google.com/search?q=alphanumeric) variables in "quotes".      
    Press ```ctrl + x``` + `y` + `enter` to save changes.  

### Start Command:    
   Restart Termux and then do these  
- Setup a quick-login command:
   ```bash
   cd ~/ && echo 'alias ubuntu="proot-distro login ubuntu"' >> .bashrc && bash
   ```
- Then:    
   ```ubuntu```    
- Once you are in proot ubuntu run:
   ```bash
   cd ~/ && echo 'alias runux="cd ux && bash run"' >> .bashrc && bash
   ```

- Steps to start bot on each launch of termux:
   1. ```ubuntu``` 
   2. ```runux```

### Potential errors and fixes:

- Extra Plugins not found:    
    Extra plugins are present but not loaded by default.
    - To install plugins run these one time commands:
    ```bash
    ubuntu
    cd ~/ux
    # Install extra requirements.
    pip install -r xtra/req_extra.txt
    # Move plugins into bot folder for loading.
    mv xtra/plugins/ userge/plugins/xtra/
    ```
- Pymongo Error while starting bot:
  Run `termux-chroot` before running `ubuntu`

### Contact:
  * [Ryuk](https://t.me/anonymousx97)
  * UX-Termux: [Group](https://t.me/ux_termux_support) | [Channel](https://t.me/ux_termux)
