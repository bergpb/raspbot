# Raspberry Pi Bot
Telegram Bot to control pins and see some system status in Raspberry Pi.

Running with a Service(systemd):
 1. Clone project,
 1. Enter inside a project folder,
 1. Get your bot token in ```@botfather```,
 1. Copy your token and paste in ```config.ini``` file,
 1. Set admin and authorized ids in ```config.ini```,
 1. Create a service file: ```sudo touch /etc/systemd/system/raspbot.service```,
 1. Copy content from raspbot.service and editing if necessary,
 1. Start service: ```sudo systemctl start raspbot.service```,
 1. (Optional) Automatically get it to start on boot: ```sudo systemctl enable raspbot.service```.
