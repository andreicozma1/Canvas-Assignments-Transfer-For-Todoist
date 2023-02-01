# Canvas-Sync

Canvas-Sync is a tool for syncing files from Canvas to your computer.

It also includes a module for syncing Canvas Assignments to your Todoist account as tasks.

**Modules**

- CanvasToTodoist
- CanvasFileDownloader

**Install dependencies**

- Install dependencies with `pip3 install -r requirements.txt`

**Run the main script**

- Run the main script by calling `python3 main.py`

**Options & Usage**

- Run the main script with the `-h` flag to see all available options and their usage: `python3 main.py -h`

**Example Crontab**

- Edit crontab

```
crontab -e
```

- Run every 60 minutes

```
@hourly /usr/bin/python3 /home/userid/Canvas-Sync/main.py -a -y
```

- Run on boot

```
@reboot /usr/bin/python3 /home/userid/Canvas-Sync/main.py -a -y
```

## Disclaimer

The original codebase has been tweaked and modified quite heavily over time. The following is the link to the original project:

- <https://github.com/scottquach/Canvas-Assignments-Transfer-For-Todoist>


