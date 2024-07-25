This tool is for managing Proxmox virtual machines in Telegram.

## Bot features:
- Turning virtual machines on and off
- Obtaining the status of virtual machines
- Convenient control anywhere in the world

## Example of a bot workin:
![demo](https://github.com/FTT221/telegram-proxmox-bot/blob/main/.github/1.jpg)

## How to start a bot:
The bot requires Python 3 and python3-pip to operate. Install them if they are not already installed.

Install dependencies: `pip install -r requirements.txt`.

After installing the dependencies, configure the bot, open `proxmox-tg-bot.py` and adjust the settings.

**Requires a user with rights to disable and enable VMs (VM.PowerMgmt, VM.Audit)**

Run the bot by running and copy `python3 proxmox-tg-bot.py` in the terminal.

## Setting autostart in Linux
1. Copy the service file:
    ```
    cp /location-services-file/telegram-proxmox-bot/proxox-tg-bot.service /etc/systemd/system/proxox-tg-bot.service
    ```
    Replace the path in `proxox-tg-bot.service` with the desired file location.

2. Start bot:
    ```
    systemctl start proxox-tg-bot.service
    ```
    To check the operation, execute the command:
    ```
    systemctl status proxox-tg-bot.service
    ```

4. To perform autoloading, do:
    ```
    systemctl enable proxox-tg-bot.service
    ```
