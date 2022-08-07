# bluemap-server.py
Standalone Python Webserver for [BlueMap](https://github.com/BlueMap-Minecraft/BlueMap), a Minecraft Server plugin.
**This project is not affiliated with BlueMap.**

## How to use
1. Clone the repository
2. Copy `config.example.toml` to `config.toml`, make sure it is in the same directory as the rest of the files.
3. Place your choices in `config.toml`
4. Install the pipenv (or just do `pip install -r requirements.txt`)
5. Start the server

## Note
You will still need to route your webroot and `/live/` paths externally. The purpose of this server is to handle retrieving tile data from a BlueMap SQL database and is intended to sit behind a reverse proxy such as nginx.
