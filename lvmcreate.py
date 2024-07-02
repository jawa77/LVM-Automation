#!/usr/bin/env python3

import sys
import subprocess

def run_command(command, exit_on_failure=True):
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        if exit_on_failure:
            print(f"Error running command: {command}\n{result.stderr}")
            sys.exit(1)
        else:
            return None
    return result.stdout.strip()

if len(sys.argv) != 3:
    print("Usage: file.py <unique_name> <storage_size>")
    sys.exit(1)

unique_name = sys.argv[1]
storage_size = sys.argv[2]

vg_name = "myvg"
lv_path = f"/dev/{vg_name}/{unique_name}"
mount_point = f"/mnt/{unique_name}"

# Check if the logical volume already exists
lv_exists = run_command(f"sudo lvdisplay {lv_path}", exit_on_failure=False)
if lv_exists is not None:
    print(f"Logical volume {unique_name} already exists. Exiting.")
    sys.exit(1)

# Ensure the volume group exists, create if it doesn't
vg_exists = run_command(f"sudo vgdisplay {vg_name}", exit_on_failure=False)
if vg_exists is None:
    print(f"Volume group {vg_name} does not exist. Creating it now.")
    sys.exit(1)
    #run_command(f"sudo vgcreate {vg_name} /dev/sdX")  # Replace /dev/sdX with your physical volume path
else:
    print(f"Using existing volume group {vg_name}.")

# Create the logical volume
print(f"Creating logical volume {unique_name} with size {storage_size}G.")
run_command(f"sudo lvcreate -L {storage_size}G -n {unique_name} {vg_name}")

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
fstab_entry = f"UUID={uuid} {mount_point} ext4 defaults 0 0"
print(f"Adding entry to /etc/fstab: {fstab_entry}")
with open("/etc/fstab", "a") as fstab:
    fstab.write(fstab_entry + "\n")

print(f"Logical volume {unique_name} created, formatted, and mounted at {mount_point}.")
