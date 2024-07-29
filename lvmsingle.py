#!/usr/bin/env python3
import os
import sys
import subprocess
from multiprocessing import Pool

RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"


def run_command_with_logging(command):
    with open("error.txt", "a") as error_file:
        error_file.write(command)


def run_command(command, exit_on_failure=True):
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        if exit_on_failure:
            print(f"Error running command: {command}\n{result.stderr}")
            sys.exit(1)
        else:
            return None
    return result.stdout.strip()


def create_lv(unique_name, storage_size, vg_name="vgname"):
    lv_path = f"/dev/{vg_name}/{unique_name}"
    mount_point = f"/mnt/{unique_name}"
    thin_pool_name = "thinpool"

    # Check if the logical volume already exists
    lv_exists = run_command(f"sudo lvdisplay {lv_path}", exit_on_failure=False)
    if lv_exists is not None:
        print(f"Logical volume {unique_name} already exists. Exiting.")
        if os.path.ismount(mount_point):
            print(f"The mount point {mount_point} exists")
        else:
            run_command_with_logging(f"mount point not present {mount_point}")
            print(f"The mount point {mount_point} does not exist")
        return  # Exit the function instead of the entire program

    # Ensure the volume group exists
    vg_exists = run_command(f"sudo vgdisplay {vg_name}", exit_on_failure=False)
    if vg_exists is None:
        print(f"Volume group {vg_name} does not exist. Exiting.")
        sys.exit(1)

    # Create the logical volume
    print(f"Creating logical volume {unique_name} with size {storage_size}G.")
    run_command(f"sudo lvcreate -V{storage_size}G --thin -n {unique_name} {vg_name}/{thin_pool_name}")

    # Format the logical volume with ext4
    print(f"Formatting logical volume {lv_path} with ext4 filesystem.")
    run_command(f"sudo mkfs.ext4 {lv_path}")

    # Create the mount point
    print(f"Creating mount point {mount_point}.")
    run_command(f"sudo mkdir -p {mount_point}")

    # Mount the logical volume
    print(f"Mounting {lv_path} to {mount_point}.")
    run_command(f"sudo mount {lv_path} {mount_point}")

    # Add to /etc/fstab for automount at boot
    uuid = run_command(f"sudo blkid -s UUID -o value {lv_path}")
    fstab_entry = f"UUID={uuid} {mount_point} ext4 defaults,nofail 0 0"
    print(f"Adding entry to /etc/fstab: {fstab_entry}")
    with open("/etc/fstab", "a") as fstab:
        fstab.write(fstab_entry + "\n")

    print(f"{GREEN}Logical volume {unique_name} created, formatted, and mounted at {mount_point}.{RESET}")


def copy_data(unique_name):
    source_path = f"/var/selfmadelabs/storage/{unique_name}"
    mount_point = f"/mnt/{unique_name}"
    print(f"Copying data from {source_path} to {mount_point}.")
    run_command(f"sudo rsync -aAXP --owner --group {source_path}/* {mount_point}")


def remove_lv(unique_name, vg_name="vgname"):
    lv_path = f"/dev/{vg_name}/{unique_name}"
    mount_point = f"/mnt/{unique_name}"
    fstab_entry = f"UUID={run_command(f'sudo blkid -s UUID -o value {lv_path}')}"

    # Unmount the logical volume if it's mounted
    if os.path.ismount(mount_point):
        print(f"Unmounting {mount_point}.")
        run_command(f"sudo umount {mount_point}")

    # Remove the logical volume
    print(f"Removing logical volume {lv_path}.")
    run_command(f"sudo lvremove -f {lv_path}")

    # Remove the mount point directory
    if os.path.exists(mount_point):
        print(f"Removing mount point {mount_point}.")
        run_command(f"sudo rmdir {mount_point}")

    # Remove entry from /etc/fstabBak
    
    with open("/etc/fstab", "r") as fstab:
        lines = fstab.readlines()
    with open("/etc/fstab", "w") as fstab:
        for line in lines:
            if fstab_entry not in line:
                fstab.write(line)

    print(f"{GREEN}Logical volume {unique_name} removed and cleaned up.{RESET}")


def process_unique_name(name, storage_size):
    unique_name = name.strip()
    if unique_name:
        print("\n------------------------------------------------------------------------------------------\n")
        create_lv(unique_name, storage_size)
        copy_data(unique_name)
        # remove_lv(unique_name)

def main():
    file_path = "folders.txt"
    storage_size = 22  # Define the storage size in GB for each logical volume

    with open(file_path, "r") as file:
        unique_names = file.readlines()

    for name in unique_names:
        process_unique_name(name.strip(), storage_size)

if __name__ == "__main__":
    main()
