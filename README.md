# Analyzer v1

Analyzer v1 is a program for monitoring and mounting/unmounting block devices using PyQt5, pyudev, and `udisksctl`.

## Features

- Monitors block device events (add/remove).
- Automatically updates the list of mounted devices.
- Allows unmounting and remounting of selected devices via `udisksctl`.
- Displays log messages in a GUI using PyQt5.

## Requirements

- Python 3.x
- PyQt5
- pyudev
- udisks2

## Installation

1. Ensure you have Python 3 installed.
2. Install the required Python packages:
   ```bash
   pip install PyQt5 pyudev

OR

sudo apt-get install udisks2


Running:

python3 analyzer.py


License:

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.


Author:

JJ Posti <techtimejourney.net>

Disclaimer:

Please note that improper use of mounting/unmounting devices could lead to data loss. Use this software at your own risk.
