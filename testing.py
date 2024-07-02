
#!/usr/bin/env python3
import os
import sys
import subprocess


def get_lv_size(lv_path):
    output = run_command(f"sudo lvdisplay {lv_path}", exit_on_failure=False)
    if output is None:
        print(f"Logical volume {lv_path} does not exist.")
        return
    for line in output.split('\n'):
        if "LV Size" in line:
            size_info = line.split()
            return(int(size_info[-2].split('.')[0]))

def run_command(command, exit_on_failure=True):
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        if exit_on_failure:
            print(f"Error running command: {command}\n{result.stderr}")
            sys.exit(1)
        else:
            return None
    return result.stdout.strip()


def create_lv(unique_name, storage_size, vg_name="snalvm"):
    lv_path = f"/dev/{vg_name}/{unique_name}"
    mount_point = f"/mnt/{unique_name}"
    thin_pool_name = "thinpool"

    # Check if the logical volume already exists
    lv_exists = run_command(f"sudo lvdisplay {lv_path}", exit_on_failure=False)
    if lv_exists is not None:
        print(f"Logical volume {unique_name} already exists. Exiting.")
        sys.exit(1)

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

    print(f"Logical volume {unique_name} created, formatted, and mounted at {mount_point}.")



def expand_lv(unique_name, size_increase, vg_name="snalvm"):
    lv_path = f"/dev/{vg_name}/{unique_name}"

    # Check if the logical volume exists
    lv_exists = run_command(f"sudo lvdisplay {lv_path}", exit_on_failure=False)
    if lv_exists is None:
        print(f"Logical volume {unique_name} does not exist. Exiting.")
        sys.exit(1)

    # Expand the logical volume
    print(f"Expanding logical volume {unique_name} by {size_increase}G.")
    run_command(f"sudo lvextend -L+{size_increase}G {lv_path}")

    # Resize the filesystem
    print(f"Resizing filesystem on {lv_path}.")
    run_command(f"sudo resize2fs {lv_path}")

    print(f"Logical volume {unique_name} expanded by {size_increase}G.")




# Example usage
expand_lv("testing10", 10)