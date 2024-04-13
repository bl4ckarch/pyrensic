#!/usr/bin/python3

import subprocess
import argparse
import os
import sys
from loguru import logger
import platform
import re
from yaspin import yaspin

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

def ListPartitions(ewf: str | os.PathLike) -> list[str]:
    """
    List Partition of our EWF 
    """
    if not os.path.exists(ewf):
        raise FileNotFoundError
    try:
        s = subprocess.run(["mmls",ewf],capture_output=True,text=True,check=True)
        p_info = s.stdout
        logger.info(p_info)
        return p_info
    except Exception as e:
        logger.exception(f"Can't find partitions of {ewf}: {e}")


def ExportPartition(ewf: str,partinfo: str) -> str | os.PathLike:
    choose = input(str("Choose the partition for your export: "))
    choose = choose.zfill(3)
    partition_pattern = re.compile(fr"^{choose}:.*$", re.MULTILINE)
    match_partition = partition_pattern.search(partinfo)
    if match_partition:
        choosen_partition = match_partition.group(0)
        offset_part.append(choosen_partition.split()[2].lstrip("0"))
        name_raw = input(str("Choose a name for our RAW image: "))
        with yaspin(text=f"Exportation de l'image RAW en cours ...") as sp:
            try:
                subprocess.run(["ewfexport","-u","-t",name_raw,ewf],check=True)
                sp.ok(" ")
                return name_raw
            except Exception as e:
                logger.exception(f"Problem with exportation of {ewf}: {e}")
    else:
        logger.error(f"Partition not found")
        return None

def MountRAW(source: str, mountpoint: str | os.PathLike ) -> None:
    """
    Mont an RAW file to a dest mountpoint
    """
    if not CheckImage(source):
        sys.exit(1)
    
    if not os.path.exists(mountpoint):
        logger.error("MountPoint doesn't exist ...")
        sys.exit(1)

    try:
        subprocess.run(["mount","-t","ntfs","-o","ro","loop",f"offset=$(({offset_part[0]}*512))",source,mountpoint], check=True)
        logger.success(f"Image mounted correctly")
    except subprocess.CalledProcessError as e:
        logger.exception(f"Error while mounting the image ... :{e}")
        sys.exit(1)

def ListFilesFromPartition(ewf,r) -> None:
    """
    File from partition
    """
    ListPartitions(ewf)
    choose = input(str("Choose the partition where you want to look for files (ex: 1): "))
    choose = choose.zfill(3)
    partition_pattern = re.compile(fr"^{choose}:.*$", re.MULTILINE)
    match_partition = partition_pattern.search(ListPartitions(ewf))
    if match_partition:
        choosen_partition = match_partition.group(0)
        try:
            s = subprocess.run(["fls","-r" if r else "","-o",choosen_partition.split()[2].lstrip("0"), ewf],check=True,capture_output=True,text=True)
            logger.info(s.stdout)
        except Exception as e:
            logger.exception(f"Wrong OFFSET: {e}")
    else:
        logger.error("Partition not found")

def GetHives() -> None:
    raise NotImplementedError("not implemented yet")

def GetMFT() -> None:
    raise NotImplementedError("not implemented yet")

def GetBrowser() -> None: 
    raise NotImplementedError("not implemented yet")
    
def CheckImage(image : str | os.PathLike ) -> bool:
    try:
        c = subprocess.run(["file",image],check=True)
        output = c.stdout.lower()
        if "raw" in output:
            return True
        return False
    except Exception as e:
        logger.exception(f"Image isn't in RAW FORMAT... :{e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EWF Utility - FORENSIC",
                                     epilog="@kaidoh",
                                     formatter_class=argparse.RawTextHelpFormatter)

    subparsers = parser.add_subparsers()

    parser_list_partition= subparsers.add_parser("list_part",help="List partitions availaible")
    parser_list_partition.add_argument("ewf_image_path",help="EWF PATH")

    parser_list_files = subparsers.add_parser("list_files", help="List partitions files")
    parser_list_files.add_argument("ewf_image_path",help="EWF PATH")
    parser_list_files.add_argument("--recursive","-r",dest="recursif",action="store_true",default=True,help="Show recursively files")

    parser_extract_files = subparsers.add_parser("extract",help="Extract a list of files")
    parser_extract_files.add_argument("ewf_image_path",help="Path de l'image EWF")
    parser_extract_files.add_argument("mountdest",help="Destination du mountpoint")
    parser_extract_files.add_argument("--hives",help="Not implemented yet")
    parser_extract_files.add_argument("--mft",help="Not implemented yet")
    parser_extract_files.add_argument("--browser",help="Not implemented yet")
    parser_extract_files.add_argument("--win_event",help="Not implemented yet")

    options = parser.parse_args()
    offset_part = []
   
    if len(sys.argv) > 1:
        if GetOS() == "Linux":
            if sys.argv[1] == 'list_part':
                ListPartitions(options.ewf_image_path)
            elif sys.argv[1] == 'list_files':
                ListFilesFromPartition(options.ewf_image_path,options.recursif)
            elif sys.argv[1] == 'extract':
                MountRAW(ExportPartition(partinfo=ListPartitions(options.ewf_image_path),ewf=options.ewf_image_path),options.ewf_image_path)
    else:
        parser.print_help()
