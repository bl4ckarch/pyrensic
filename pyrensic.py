import argparse
import subprocess
import os

def run_command(command, get_output=False):
    """Executes a command and returns the output if successful, or None on failure."""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
        return result.stdout if get_output else None
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running command: {e.cmd}")
        print(e.stderr)
        return None

def setup_mount_point(mount_point, username):
    """Ensures the mount point exists and is owned by the specified user."""
    if not os.path.exists(mount_point):
        os.makedirs(mount_point)
        print(f"Mount point {mount_point} created.")
    run_command(f"sudo chown {username} {mount_point}")
    print(f"Ownership of {mount_point} changed to {username}.")

def mount_ewf(image_path, mount_point, username):
    """Mounts an EWF image using ewfmount."""
    setup_mount_point(mount_point, username)
    result = run_command(f"sudo ewfmount {image_path} {mount_point}", get_output=True)
    if result:
        print(f"EWF image mounted at {mount_point}")
        return os.path.join(mount_point, 'ewf1')  # Path to the virtual ewf device
    else:
        return None

def unmount_ewf(mount_point):
    """Unmounts the EWF image from the mount point."""
    run_command(f"sudo umount {mount_point}")
    print(f"EWF image unmounted from {mount_point}")
    

def list_disk_structure(disk_path):
    """Lists the partition structure of the mounted EWF image."""
    return run_command(f"sudo fdisk -l {disk_path}", get_output=True)

def get_user_input():
    """Gets the partition and offset input from the user."""
    print("\nPlease enter the partition offset (in sectors):")
    offset = input()
    print("Please enter the mount point for the raw image:")
    mount_point = input()
    return offset, mount_point

def mount_partition(offset, source, mount_point):
    """Mounts a specific partition from an EWF image based on the given offset."""
    mount_cmd = f"sudo mount -o ro,norecovery,loop,offset=$(({offset}*512)) {source} {mount_point}"
    if run_command(mount_cmd):
        print(f"Partition mounted at {mount_point}")

def main():
    parser = argparse.ArgumentParser(description="Forensic Data Extraction Tool")
    parser.add_argument("image_path", help="Path to the EWF image")
    parser.add_argument("ewf_mount_point", help="Mount point for the EWF image")
    parser.add_argument("username", help="Username that will own the mount point")
    args = parser.parse_args()

    disk_path = mount_ewf(args.image_path, args.ewf_mount_point, args.username)
    if disk_path:
        try:
            disk_structure = list_disk_structure(disk_path)
            if disk_structure:
                print("Disk Structure:")
                print(disk_structure)
                offset, raw_mount_point = get_user_input()
                mount_partition(offset, disk_path, raw_mount_point)
            # Wait for user to manually request unmounting
            print(f"Now run the pyrensic_analysic.py and use {args.ewf_mount_point} mount point when prompted for further analysis")
            while True:
                command = input("Type 'unmount' to unmount the EWF and exit, or 'continue' to keep working: ").lower()
                if command == "unmount":
                    break
        finally:
            unmount_ewf(args.ewf_mount_point)

if __name__ == "__main__":
    main()
