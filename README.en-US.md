# Minecraft Server Bot
This project is a management tool designed to simplify the start and stop operations of a Minecraft server.  
It includes features that the author personally finds useful.  
Built with Python 3 on Ubuntu LTS, the tool is lightweight and optimized for practical, hands-on deployment.

## Features
- Start and stop the Minecraft server via command
- Built with Discord bot integration in mind (easily expandable)
- Optimized for local environments and manual server operation

## Setup
First, install Python3 and tmux (for Ubuntu):

```bash
sudo apt update -y
sudo apt upgrade -y
sudo apt install python3 python3-venv tmux
```

After that, the `.venv/` virtual environment has already been created and all required packages are installed.  
To activate the environment and run the program, use the following commands:

### Create token.txt
Generate a Discord bot token and save it in a file named token.txt as plain text.

```bash
source .venv/bin/activate
python3 main.py
```

## Usage
Commands are prefixed with `!`.  
Please use `!help` to view available commands.