# telefilebot
![CI](https://github.com/grburgess/telefilebot/workflows/CI/badge.svg?branch=master)
[![codecov](https://codecov.io/gh/grburgess/telefilebot/branch/master/graph/badge.svg)](https://codecov.io/gh/grburgess/telefilebot)
[![Documentation Status](https://readthedocs.org/projects/telefilebot/badge/?version=latest)](https://telefilebot.readthedocs.io/en/latest/?badge=latest)
![PyPI](https://img.shields.io/pypi/v/telefilebot)
![PyPI - Downloads](https://img.shields.io/pypi/dm/telefilebot)

![alt text](https://raw.githubusercontent.com/grburgess/telefilebot/master/docs/media/logo.png)

Sometimes you have code that runs a long time and you do not want to
continuously check if it has finished. If that code writes a file to the disk at
the end, maybe you just want a text message when that file is created or
modified?

`telefilebot` allows you to do this with as a simple background listener. All
you need is an input YAML file and you can monitor multiple directories for
various new files being created.

## Installation

```bash
pip install telefilebot
```

## Usage

Say you have two directories you want to monitor. In one of them you want to
look for text files (files ending with a .txt extension) and the other you only
want to scan the top two level directories.

First you need to [create a telegram
bot](https://firstwarning.net/vanilla/discussion/4/create-telegram-bot-and-get-bots-token-and-the-groups-chat-id)
and attach it to some group where it can message you.

Now, create a YAML file that looks like this:

```yaml

name: "file_monitor"
chat_id: "-XXXXXXXX"
token: "XXXXXXX"
logging:
  level: "INFO"
directories:
  "~/my_dir1":
    extensions:
      - .txt
  "~/my_dir2":
  recursion_limit: 0
wait_time: 1
```


What do these things mean? The name just names the bot. The `chat_id` and
`token` are from you group and bot you created. `logging` sets the verbosity of
the printout in the terminal. For each directory you want to monitor, create an
entry with the directory path. If you want to monitor only certain file
extensions, list them under the director. If you only want to recurse down to a
certain level in the file structure, enter a recursion limit (here `zero` means
only the path entered and no sub-folders will be scanned).

Finally, the `wait_time` argument specifies in minutes how long to wait between
checks of the file system.

Now simply fire up a tmux session (or however you want to the bot to run in the
background) and enter


```bash

telefilebot --file=input.yml

```

and you are done! Your bot will let you know when new files are added or modified.


* Free software: GNU General Public License v3
* Documentation: https://telefilebot.readthedocs.io.

