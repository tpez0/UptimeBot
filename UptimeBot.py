 #-------------------------------------------------------------------------------------
 # Script: UptimeBot.py
 # Author: tpez0
 # Notes : No warranty expressed or implied.
 #         Use at your own risk.
 #
 # Function: Simple tool to monitor the uptime of one or multiple websites
 #           with log rotation and SHA256 hash
 #              
 #--------------------------------------------------------------------------------------


import requests
import time
import logging
from logging.handlers import TimedRotatingFileHandler
import subprocess
import os
import hashlib

urls = [
    "https://www.WEBSITE.com"
]
timeout_seconds = 10
log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "NOMELOG.log")

# Configure logger
logger = logging.getLogger("WebsiteMonitor")
logger.info(f"Log level set to {level}")
logger.setLevel(logging.INFO)  # Set log level on INFO
#handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=30)
handler = TimedRotatingFileHandler(log_file, when="M", interval=1, backupCount=1000)
handler.suffix = "%Y-%m-%d_%H-%M"
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# FFunction to make the file read-only and generate SHA256
def make_file_immutable(filepath):
    if not os.path.exists(filepath):
        print(f"Log file {filepath} does not exist. Cannot make it immutable.")
        return
    try:
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        hash_value = sha256_hash.hexdigest()
        with open(filepath + ".sha256", "w") as hash_file:
            hash_file.write(f"{hash_value} {os.path.basename(filepath)}\n")
        print(f"SHA256 checksum written to {filepath}.sha256")
    except Exception as e:
        print(f"Failed to generate SHA256 for {filepath}: {e}")
    try:
        # Use the absolute path of the file
        abs_filepath = os.path.abspath(filepath)
        subprocess.run(["attrib", "+R", abs_filepath], check=True)
        subprocess.run(["attrib", "+R", abs_filepath + ".sha256"], check=True)
        print(f"Log file {abs_filepath} and its checksum have been made read-only.")
    except Exception as e:
        print(f"Failed to make file read-only: {abs_filepath}, Error: {e}")

# Monitoring function
def monitor():
    logger.info("Starting monitor function")
    while True:
        for url in urls:
            try:
                response = requests.get(url, timeout=timeout_seconds)
                log_message = f"URL: {url}, Status Code: {response.status_code}, Response Time: {response.elapsed.total_seconds()} seconds"
                print(log_message)
                logger.info(log_message)
            except requests.exceptions.RequestException as e:
                log_message = f"URL: {url}, Website is down or unreachable. Error: {e}"
                print(log_message)
                logger.info(log_message)
        
        # Check if a log file exists without .log and .sha256 extension
        for file in os.listdir(log_dir):
            if not file.endswith(".log") and not file.endswith(".sha256"):
                previous_log = os.path.join(log_dir, file)
                sha256_file = previous_log + ".sha256"
                if not os.path.exists(sha256_file):
                    logger.info(f"Preparing to create SHA256 file for: {previous_log}")
                    make_file_immutable(previous_log)
        
        time.sleep(30)

if __name__ == "__main__":
    monitor()