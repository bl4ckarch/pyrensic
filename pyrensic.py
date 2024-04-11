import argparse
import subprocess
#import libewf
import pytsk3
import os

def open_ewf(image_path):
    """
    Opens an EWF image and returns an EWF handle.
    :param image_path: Path to the EWF image file.
    :return: EWF handle.
    """
    ewf_handle = libewf.handle()
    ewf_handle.open(image_path)
    return ewf_handle
def read_ewf_info(ewf_handle):
    """
    Reads and prints some information from an EWF handle.
    :param ewf_handle: Opened EWF handle.
    """
    print("EWF information:")
    print("Number of segments:", ewf_handle.number_of_segments)
    print("Media size:", ewf_handle.media_size, "bytes")


def list_partitions(img_info):
    volume_info = pytsk3.Volume_Info(img_info)
    partitions = []
    for partition in volume_info:
        if "Win" in partition.desc.decode('utf-8'):
            partitions.append((partition.addr, partition.desc.decode('utf-8'), partition.len))
    return partitions

def list_files_in_partition(img_info, partition_addr, indent=0):
    volume_info = pytsk3.Volume_Info(img_info)
    partition = next((p for p in volume_info if p.addr == partition_addr), None)
    if not partition:
        raise ValueError("Partition not found.")
    filesystem = pytsk3.FS_Info(img_info, offset=partition.start * volume_info.info.block_size)
    return list_directory_contents(filesystem, filesystem.open_dir(path="/"), indent=indent)

def list_directory_contents(filesystem, directory, indent=0):
    results = []
    for entry in directory:
        if entry.info.name.name in [".", ".."]:
            continue
        file_info = f"{' ' * indent}{entry.info.name.name}"
        results.append(file_info)
        if entry.info.meta and entry.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
            sub_directory = entry.as_directory()
            results.extend(list_directory_contents(filesystem, sub_directory, indent + 2))
    return results

def extract_file(filesystem, file_path, output_path):
    try:
        file_object = filesystem.open(file_path)
    except IOError:
        print(f"File {file_path} could not be opened.")
        return False
    with open(output_path, 'wb') as output_file:
        offset = 0
        size = file_object.info.meta.size
        while offset < size:
            data = file_object.read_random(offset, min(1024, size - offset))
            if not data:
                break
            output_file.write(data)
            offset += len(data)
    return True

def run_regripper(reg_file_path, report_path):
    regripper_cmd = 'perl rip.pl'
    command = f"{regripper_cmd} -r {reg_file_path} -f all > {report_path}"
    subprocess.run(command, shell=True, check=True)
    return f"Report generated: {report_path}"

def main():
    parser = argparse.ArgumentParser(description="Forensic Data Extraction Tool")
    parser.add_argument("image_path", help="Path to the EWF image")
    parser.add_argument("--list_partitions", action="store_true", help="List the partitions in the EWF image")
    parser.add_argument("--partition", type=int, help="Partition number for file listing or extraction")
    parser.add_argument("--list_files", action="store_true", help="List files in a specified partition")
    parser.add_argument("--extract_file", help="Extract a specific file from the filesystem")
    parser.add_argument("--output_path", help="Path to save the extracted file")
    parser.add_argument("--run_regripper", action="store_true", help="Run RegRipper on the extracted registry file")
    parser.add_argument("--report_path", help="Path to save the RegRipper report")

    args = parser.parse_args()

    img_info = open_ewf(args.image_path)

    if args.list_partitions:
        partitions = list_partitions(img_info)
        for addr, desc, length in partitions:
            print(f"Partition {addr}: {desc}, Length: {length} sectors")
    elif args.list_files and args.partition is not None:
        files = list_files_in_partition(img_info, args.partition)
        for file in files:
            print(file)
    elif args.extract_file and args.output_path:
        if args.partition is None:
            raise ValueError("Partition number must be specified.")
        volume_info = pytsk3.Volume_Info(img_info)
        partition = next((p for p in volume_info if p.addr == args.partition), None)
        filesystem = pytsk3.FS_Info(img_info, offset=partition.start * volume_info.info.block_size)
        success = extract_file(filesystem, args.extract_file, args.output_path)
        if success:
            print(f"File extracted to {args.output_path}")
            if args.run_regripper and args.report_path:
                report = run_regripper(args.output_path, args.report_path)
                print(report)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
