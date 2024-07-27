import os
import shutil
import hashlib
import time
import argparse
import logging
import signal
import sys

def setup_logging(log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def get_file_hash(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def normalize_path(path):
    #new_path = os.path.normcase(path)
    new_path = os.path.normpath(path)
    return new_path

def copy_files(source, replica):
    normalized_source = normalize_path(source)
    normalized_replica = normalize_path(replica)

    if not os.path.exists(normalized_source):
        logging.error(f"Source folder '{normalized_source}' does not exist. Exiting...")
        sys.exit(1)

    for root, _, files in os.walk(normalized_source):
        relative_path = os.path.relpath(root, normalized_source)
        replica_path = os.path.join(normalized_replica, relative_path)

        normalized_replica_path = normalize_path(replica_path)

        if not os.path.exists(normalized_replica_path):
            os.makedirs(normalized_replica_path)
            logging.info(f"Created directory: {normalized_replica_path}")

        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(normalized_replica_path, file)

            normalized_source_file = normalize_path(source_file)
            normalized_replica_file = normalize_path(replica_file)

            if not os.path.exists(normalized_replica_file):
                shutil.copy2(normalized_source_file, normalized_replica_file)
                logging.info(f"Copied file: {normalized_source_file} to {normalized_replica_file}")
                continue 

            if get_file_hash(normalized_source_file) != get_file_hash(normalized_replica_file):
                shutil.copy2(normalized_source_file, normalized_replica_file)
                logging.info(f"Updated file: {normalized_source_file} to {normalized_replica_file}")
                continue 

def delete_extra_files(source, replica):
    normalized_source = normalize_path(source)
    normalized_replica = normalize_path(replica)

    for root, _, files in os.walk(normalized_replica):
        relative_path = os.path.relpath(root, normalized_replica)
        source_path = os.path.join(normalized_source, relative_path)

        normalized_source_path = normalize_path(source_path)

        for file in files:
            replica_file = os.path.join(root, file)
            source_file = os.path.join(normalized_source_path, file)

            normalized_replica_file = normalize_path(replica_file)
            normalized_source_file = normalize_path(source_file)

            if not os.path.exists(normalized_source_file):
                os.remove(normalized_replica_file)
                logging.info(f"Deleted file: {normalized_replica_file}")


def synchronize(source, replica):
    copy_files(source, replica)
    delete_extra_files(source, replica)

def signal_handler(sig, frame):
    logging.info('Synchronization interrupted by user. Exiting...')
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Synchronize two folders.")
    parser.add_argument("source", help="Path to the source folder")
    parser.add_argument("replica", help="Path to the replica folder")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Path to the log file")
    args = parser.parse_args()

    setup_logging(args.log_file)

    # NOTE(@cobileacd): register the signal handler for SIGINT (Control-C)
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        logging.info("Starting synchronization process...")
        synchronize(args.source, args.replica)
        logging.info("Synchronization completed.")
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
