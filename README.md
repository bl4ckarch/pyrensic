# pyrensic
This Tool is a Forensic Analysis Tool (University Project)

## Overview

This tool is designed to mount Expert Witness Compression Format (EWF) images, analyze mounted disks for forensic information, and run detailed analysis with RegRipper on specific Windows registry hives.

## Prerequisites

- **Linux Operating System**: Ubuntu, Debian, Fedora, or any other Linux distribution.
- **Perl**: Required to run RegRipper scripts.
- **sudo privileges**: Required for mounting operations.

## Required Tools

1. **libewf**: Tools for accessing and extracting data from EWF files.
   - **Installation**:
     ```bash
     sudo apt-get install libfuse-dev  libewf-dev libfuse2 uuid-dev lbzip2 python3-wchartype  # Ubuntu/Debian
     sudo apt-get install ewf-tools
     ```

2. **RegRipper**: Used to analyze Windows registry hives.
   - **Installation**:
     - Clone the repository from GitHub:
       ```bash
       cd /opt
       sudo git clone https://github.com/keydet89/RegRipper3.0.git regripper
       sudo chown -R $USER:$USER /opt/regripper
       ```
     - Ensure Perl is installed:
       ```bash
       sudo apt-get install perl # Ubuntu/Debian
       ```

3. **Mounting Tools**: Necessary for creating and managing mount points.
   - Typically pre-installed in most Linux distributions.

## Setup

- Ensure all prerequisites are installed as described above.
- Clone this repository to your local machine (if applicable):
  ```bash
  git clone https://github.com/bl4ckarch/pyrensic

## Usage

- Running the Tool:
- Navigate to the script directory:
    ```bash
    cd path/to/your/script
    ```
- Run the script with necessary arguments:

```bash
    sudo python3 pyrensic.py <path_to_ewf_image> <mount_point_for_ewf> <username>
    sudo python3 pyrensic_analysis.py
```
- Follow the on-screen prompts to analyze different partitions and registry hives.

    -Unmounting:
        The tool provides an interactive prompt to unmount the EWF image once you are done with the analysis. Type 'unmount' when prompted.

## Notes

- Ensure you have sufficient permissions to execute the commands, particularly those that require sudo.
- Adjust paths and environment variables according to your system's configuration, especially for RegRipper.

