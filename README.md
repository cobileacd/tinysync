# Tiny Sync 

## Overview
This is a Python script that synchronizes the contents of a source folder to a replica folder, ensuring that the replica is a full, identical copy of the source. Synchronization is one-way, from source to replica, and is performed periodically. The script logs all file operations to a specified log file and outputs them to the console.

## Usage
```bash
python sync_folders.py /path/to/source /path/to/replica 60 /path/to/logfile.log
