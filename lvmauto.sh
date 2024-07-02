#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <unique_name> <storage_size>"
    exit 1
fi

UNIQUE_NAME=$1
STORAGE_SIZE=$2

VG_NAME="myvg"
LV_PATH="/dev/$VG_NAME/$UNIQUE_NAME"
MOUNT_POINT="/mnt/$UNIQUE_NAME"

# Check if the logical volume already exists
if sudo lvdisplay $LV_PATH &> /dev/null; then
    echo "Logical volume $UNIQUE_NAME already exists. Exiting."
    exit 1
fi

# Ensure the volume group exists, create if it doesn't
if ! vgdisplay $VG_NAME &> /dev/null; then
    echo "Volume group $VG_NAME does not exist. Creating it now."
    sudo vgcreate $VG_NAME /dev/sdX  # Replace /dev/sdX with your physical volume path
else
    echo "Using existing volume group $VG_NAME."
fi

# Create the logical volume
echo "Creating logical volume $UNIQUE_NAME with size ${STORAGE_SIZE}G."
sudo lvcreate -L ${STORAGE_SIZE}G -n $UNIQUE_NAME $VG_NAME

# Format the logical volume with ext4
echo "Formatting logical volume $LV_PATH with ext4 filesystem."
sudo mkfs.ext4 $LV_PATH

# Create the mount point
echo "Creating mount point $MOUNT_POINT."
sudo mkdir -p $MOUNT_POINT

# Mount the logical volume
echo "Mounting $LV_PATH to $MOUNT_POINT."
sudo mount $LV_PATH $MOUNT_POINT

# Add to /etc/fstab for automount at boot
UUID=$(sudo blkid -s UUID -o value $LV_PATH)
echo "UUID=$UUID $MOUNT_POINT ext4 defaults 0 0" | sudo tee -a /etc/fstab

echo "Logical volume $UNIQUE_NAME created, formatted, and mounted at $MOUNT_POINT."
