import argparse
import subprocess
import os
import pytsk3

def mount_ewf(image_path, mount_point):
    """
    Mounts an EWF image using pyEWFmount at a specified mount point.
    """
    if not os.path.exists(mount_point):
        os.makedirs(mount_point)
    
    # Mount command
    mount_command = f"sudo pyEWFmount -i {image_path} -o {mount_point}"
    subprocess.run(mount_command, shell=True, check=True)
    print(f"EWF image mounted at {mount_point}")

def unmount_ewf(mount_point):
    """
    Unmounts the EWF image from the mount point.
    """
    unmount_command = f"sudo umount {mount_point}"
    subprocess.run(unmount_command, shell=True, check=True)
    print("EWF image unmounted")

def list_files_in_partition(mount_point):
    """
    List files using pytsk3 by navigating the file system.
    """
    img_info = pytsk3.Img_Info(f'ewf:{mount_point}')
    filesystem = pytsk3.FS_Info(img_info)
    directory = filesystem.open_dir(path="/")
    
    print("Files in the filesystem:")
    for entry in directory:
        print(entry.info.name.name)

def extract_and_analyze_file(filesystem, file_path, output_path, report_path=None):
    """
    Extracts a specific file and potentially analyzes it with RegRipper.
    """
    try:
        file_object = filesystem.open(file_path)
        with open(output_path, 'wb') as output_file:
            file_data = file_object.read_random(0, file_object.info.meta.size)
            output_file.write(file_data)
        print(f"File extracted to {output_path}")

        if report_path:
            run_regripper(output_path, report_path)

    except IOError as e:
        print(f"Error opening file {file_path}: {e}")

def run_regripper(reg_file_path, report_path):
    """
    Runs RegRipper on the extracted registry file.
    """
    regripper_cmd = f"perl rip.pl -r {reg_file_path} -f all > {report_path}"
    subprocess.run(regripper_cmd, shell=True, check=True)
    print(f"RegRipper report generated at {report_path}")

def main():
    parser = argparse.ArgumentParser(description="Forensic Data Extraction Tool")
    parser.add_argument("image_path", help="Path to the EWF image")
    parser.add_argument("mount_point", help="Mount point for the EWF image")
    parser.add_argument("--extract_file", help="File path within the image to extract")
    parser.add_argument("--output_path", help="Local path to save the extracted file")
    parser.add_argument("--report_path", help="Local path to save the RegRipper report", default=None)
    args = parser.parse_args()

    mount_ewf(args.image_path, args.mount_point)

    try:
        if args.extract_file and args.output_path:
            img_info = pytsk3.Img_Info(f'ewf:{args.mount_point}')
            filesystem = pytsk3.FS_Info(img_info)
            extract_and_analyze_file(filesystem, args.extract_file, args.output_path, args.report_path)
        else:
            list_files_in_partition(args.mount_point)
    finally:
        unmount_ewf(args.mount_point)

if __name__ == "__main__":
    main()
