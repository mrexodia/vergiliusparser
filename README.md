# vergiliusparser

Simple script to scrape https://www.vergiliusproject.com/

1. Use https://www.httrack.com/ to make a mirror of https://www.vergiliusproject.com/
2. Use a webserver (caddy) to host the mirror locally
3. `python vergiliusparser http://localhost/path/to/kernel kernel.h`