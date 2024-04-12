import argparse
import subprocess
import os

def run_command(command, get_output=False):
    """Executes a command, optionally returning its output."""
    try:
        if get_output:
            result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
            return result.stdout
        else:
            subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running command: {e.cmd}")
        print(e.stderr)
        return None

def get_ewf_info(image_path):
    """Displays information about the EWF image."""
    return run_command(f"ewfinfo {image_path}", get_output=True)

def mount_ewf(image_path, mount_point):
    """Mounts an EWF image using ewfmount and checks for success."""
    if not os.path.exists(mount_point):
        os.makedirs(mount_point)
        print(f"Mount point {mount_point} created.")
    
    # Running ewfmount command
    result = run_command(f"sudo ewfmount {image_path} {mount_point}", get_output=True)
    if result and 'ewfmount' in result:
        print(f"EWF image mounted at {mount_point}")
        mounted_path = os.path.join(mount_point, 'ewf1')
        if os.path.exists(mounted_path):
            return mounted_path  # Only return path if the mount was definitively successful
        else:
            print("Mount successful but expected mount output not found.")
    return None


def list_disk_structure(mount_point):
    """Lists the partition structure of the mounted EWF image."""
    return run_command(f"sudo fdisk -l {mount_point}/ewf1", get_output=True)

def mount_partition(offset, source, mount_point):
    """Mounts a specific partition from an EWF image based on the given offset."""
    if not os.path.exists(mount_point):
        os.makedirs(mount_point)
    mount_cmd = f"sudo mount -o ro,norecovery,loop,offset={offset} {source} {mount_point}"
    return run_command(mount_cmd)

def main():
    parser = argparse.ArgumentParser(description="Forensic Data Extraction Tool")
    parser.add_argument("image_path", help="Path to the EWF image")
    parser.add_argument("ewf_mount_point", help="Mount point for the EWF image")
    parser.add_argument("raw_mount_point", help="Mount point for the raw image")
    args = parser.parse_args()

    # Get information about the EWF image
    ewf_info = get_ewf_info(args.image_path)
    if ewf_info:
        print("EWF Information:")
        print(ewf_info)
    # Mount the EWF image
    if mount_ewf(args.image_path, args.ewf_mount_point):
        print(f"EWF image mounted at {args.ewf_mount_point}")
        
        # List disk structure
        disk_structure = list_disk_structure(args.ewf_mount_point)
        if disk_structure:
            print("Disk Structure:")
            print(disk_structure)

            # Calculate offset for the partition to mount (example calculation provided)
            # Adjust based on actual disk structure output parsing
            sector_offset = 489472  # This should be parsed from `disk_structure`
            byte_offset = sector_offset * 512
            if mount_partition(byte_offset, f"{args.ewf_mount_point}/ewf1", args.raw_mount_point):
                print(f"Partition mounted at {args.raw_mount_point}")

                # Further operations such as RegRipper can be performed here

        # Unmount EWF after operations are done
        run_command(f"sudo umount {args.ewf_mount_point}")
        print(f"EWF image unmounted from {args.ewf_mount_point}")

if __name__ == "__main__":
    main()
