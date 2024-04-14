#!/usr/bin/env python3
# File name          : pyrensic.py
# Author             : bl4ckarch, KaidohTips
# Date created       : 13 avril 2024

import argparse
import subprocess
import os
import logging
import sys
import re
import platform

class CustomColors:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    CYAN = '\033[36m'
    RESET = '\033[0m'
    BOLD = '\033[01m'
    PURPLE = '\033[95m'

# Custom formatter with color support
class CustomFormatter(logging.Formatter):
    format_dict = {
        logging.DEBUG: CustomColors.CYAN + "[DEBUG] " + CustomColors.RESET,
        logging.INFO: CustomColors.GREEN + "[INFO] " + CustomColors.RESET,
        logging.WARNING: CustomColors.YELLOW + "[WARNING] " + CustomColors.RESET,
        logging.ERROR: CustomColors.RED + "[ERROR] " + CustomColors.RESET,
        logging.CRITICAL: CustomColors.PURPLE + "[CRITICAL] " + CustomColors.RESET
    }

    def format(self, record):
        log_fmt = self.format_dict.get(record.levelno)
        formatter = logging.Formatter('%(asctime)s ' + log_fmt + '%(message)s', "%Y-%m-%d %H:%M:%S")
        return formatter.format(record)
    
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logging.basicConfig(level=logging.DEBUG, handlers=[handler])

def pop_err(text: str) -> str:
    logging.error(text)
    sys.exit()

def pop_dbg(text: str) -> str:
    logging.debug(text)

def pop_info(text: str) -> str:
    logging.info(text)

def pop_valid(text: str) -> str:
    logging.info(text)


def GetOS() -> str:
    """
    Get OS
    """
    match platform.system():
        case "Linux":
            return "Linux"
        case "Windows":
            return "Windows"
        case _:
            raise OSError("OS not supported")

def run_command(command: str, get_output: bool =False) -> str:
    """Executes a command and returns the output if successful, or None on failure."""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
        return result.stdout if get_output else None
    except subprocess.CalledProcessError as e:
        pop_err(f"An error occurred while running command: {e.cmd}")
        print(e.stderr)
        return None

def setup_mount_point(mount_point: str | os.PathLike, username: str) -> None:
    """Ensures the mount point exists and is owned by the specified user."""
    if not os.path.exists(mount_point):
        os.makedirs(mount_point)
        pop_info(f"Mount point {mount_point} created.")
    run_command(f"sudo chown {username} {mount_point}")
    pop_valid(f"Ownership of {mount_point} changed to {username}.")

def mount_ewf(image_path: str | os.PathLike , mount_point: str | os.PathLike, username: str) -> str | os.PathLike:
    """Mounts an EWF image using ewfmount."""
    setup_mount_point(mount_point, username)
    result = run_command(f"sudo ewfmount {image_path} {mount_point}", get_output=True)
    if result:
        pop_dbg(f"EWF image mounted at {mount_point}")
        return os.path.join(mount_point, 'ewf1')  # Path to the virtual ewf device
    else:
        return None

def unmount_ewf(mount_point: str | os.PathLike) -> None:
    """Unmounts the EWF image from the mount point."""
    run_command(f"sudo umount {mount_point}")
    print(f"EWF image unmounted from {mount_point}")
    

def ListPartitions(disk_path: str | os.PathLike) -> list[str]:
    """
    List Partition of our EWF 
    """
    if not os.path.exists(disk_path):
        raise FileNotFoundError
    try:
        s = run_command(f"mmls {disk_path}",True)
        pop_dbg(s)
        return s
    except Exception as e:
        pop_err(f"Can't find partitions of {disk_path}: {e}")


def ListFilesFromPartition(disk_path) -> None:
    """
    File from partition
    """
    list_p = ListPartitions(disk_path)
    choose = input(str("Choose the partition where you want to look for files (ex: 1): "))
    choose = choose.zfill(3)
    partition_pattern = re.compile(fr"^{choose}:.*$", re.MULTILINE)
    match_partition = partition_pattern.search(list_p)
    if match_partition:
        choosen_partition = match_partition.group(0)
        try:
            s = run_command(f"fls -r -o {choosen_partition.split()[2].lstrip('0')} {disk_path}",True)
            pop_dbg(s)
        except Exception as e:
            pop_err(f"Wrong OFFSET: {e}")
    else:
        pop_err("Partition not found")

def get_user_input(disk_path: str | os.PathLike) -> tuple[str, str | os.PathLike]:
    """Gets the partition and offset input from the user."""
    
    list_p = ListPartitions(disk_path)
    pop_dbg("Please, enter the partition number (ex: 1): ")
    choose = input()
    choose = choose.zfill(3)
    partition_pattern = re.compile(fr"^{choose}:.*$", re.MULTILINE)
    match_partition = partition_pattern.search(list_p)
    if match_partition:
        choosen_partition = match_partition.group(0)
        offset = choosen_partition.split()[2].lstrip("0")
        pop_dbg("Please enter the mount point for the raw image: ")
        mount_point = input()
    return offset, mount_point

def mount_partition(offset: str, source: str | os.PathLike, mount_point:str | os.PathLike) -> None:
    """Mounts a specific partition from an EWF image based on the given offset."""
    mount_cmd = f"sudo mount -o ro,norecovery,loop,offset=$(({offset}*512)) {source} {mount_point}"
    if run_command(mount_cmd):
        pop_info(f"Partition mounted at {mount_point}")

def main():
    
    parser = argparse.ArgumentParser(description="Forensic Data Extraction Tool")
    subparsers = parser.add_subparsers()
    parser_analyze = subparsers.add_parser("analyze",help="analyze disk")
    parser_analyze.add_argument("image_path", help="Path to the EWF image")
    parser_analyze.add_argument("ewf_mount_point", help="Mount point for the EWF image")
    parser_analyze.add_argument("username", help="Username that will own the mount point")

    parser_list_files = subparsers.add_parser("list_files", help="List partitions files")
    parser_list_files.add_argument("ewf_image_path",help="EWF PATH")
    
    args = parser.parse_args()

    if len(sys.argv) > 1:
        if GetOS() == "Linux":
            if sys.argv[1] == 'analyze':
                disk_path = mount_ewf(args.image_path, args.ewf_mount_point, args.username)
                if disk_path:
                    try:
                        offset, raw_mount_point = get_user_input(args.image_path)
                        mount_partition(offset, disk_path, raw_mount_point)
                        # Wait for user to manually request unmounting
                        pop_valid(f"Now run the pyrensic_analysic.py and use {args.ewf_mount_point} mount point when prompted for further analysis")
                        while True:
                            command = input("Type 'unmount' to unmount the EWF and exit, or 'continue' to keep working: ").lower()
                            if command == "unmount":
                                break
                    finally:
                        unmount_ewf(args.ewf_mount_point)

            elif sys.argv[1] == 'list_files':
                ListFilesFromPartition(args.ewf_image_path)
            else:
                parser.print_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
