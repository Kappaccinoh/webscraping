sudo systemctl start scraper.service

sudo systemctl stop scraper.service

sudo systemctl status scraper.service

sudo systemctl disable scraper.service

sudo systemctl restart scraper.service

view live logs
sudo journalctl -u scraper.service -f
