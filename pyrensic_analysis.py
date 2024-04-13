import os
import subprocess

def run_command(command):
    """Executes a command and returns the output."""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running command: {e.cmd}")
        print(e.stderr)
        return None

def list_user_profiles(mount_point):
    """Lists all user profiles in the Users directory of the mounted image."""
    users_dir = os.path.join(mount_point, 'Users')
    try:
        users = os.listdir(users_dir)
        print("Available user profiles:")
        for user in users:
            print(user)
        return users
    except Exception as e:
        print(f"Failed to list user profiles: {str(e)}")
        return []

def select_user_hive(users):
    """Prompts the user to select a hive from available user profiles."""
    print("\nEnter the name of the user profile to analyze:")
    selected_user = input()
    if selected_user in users:
        return selected_user
    else:
        print("Invalid user profile selected.")
        return None


def analyze_hive(hive_path, hive_type, output_file, regripper_path):
    """Provides the command to run RegRipper manually."""
    if os.path.exists(hive_path):
        if hive_type == "ntuser":
            command = f"perl {regripper_path}/rip.pl -r {hive_path} -a > {output_file}"
        else:
            command = f"perl {regripper_path}/rip.pl -r {hive_path} -f {hive_type} > {output_file}"
        print(f"To analyze the {hive_type} hive, run the following command:")
        print(command)
    else:
        print(f"{hive_path} not found.")

def analyze_user_hives(mount_point, user_hive, regripper_path):
    """Prints commands for analyzing various hives of the selected user."""
    hives = {
        "ntuser": f"Users/{user_hive}/NTUSER.DAT",
        "sam": "Windows/System32/config/SAM",
        "security": "Windows/System32/config/SECURITY",
        "system": "Windows/System32/config/SYSTEM",
        "software": "Windows/System32/config/SOFTWARE"
    }
    for hive_name, relative_path in hives.items():
        hive_path = os.path.join(mount_point, relative_path)
        output_file = f"{hive_name.upper()}_{user_hive}_analysis.txt"
        analyze_hive(hive_path, hive_name, output_file, regripper_path)

def main():
    regripper_path = "/opt/regripper"  # Path to RegRipper
    mount_point = input("Enter your previous disk mount point (e.g., /mnt/...): ")
    users = os.listdir(os.path.join(mount_point, 'Users'))
    print("Available user profiles:")
    for user in users:
        print(user)
    
    user_hive = input("\nEnter the name of the user profile to analyze: ")
    if user_hive in users:
        analyze_user_hives(mount_point, user_hive, regripper_path)
        # Opens an interactive shell for the user to run commands manually
        print("\nOpening an interactive shell for you to run the commands. Type 'exit' to leave the shell.")
        subprocess.call('/bin/bash')
    else:
        print("Invalid user profile selected.")

if __name__ == "__main__":
    main()