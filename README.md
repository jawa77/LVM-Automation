# LVM Automation Script and Controller

This project provides an automation script and controller for managing Logical Volume Management (LVM) on Linux systems. It supports operations such as shrinking, expanding, creating logical volumes (LVs), and retrieving details of LVs and volume groups (VGs). All actions are recorded in a MongoDB database for tracking and auditing purposes.

## Features

- **Create Logical Volumes:** Easily create new LVs within a specified VG.
- **Expand Logical Volumes:** Increase the size of existing LVs as needed.
- **Shrink Logical Volumes:** Reduce the size of LVs to free up space.
- **Get Single Person LVs:** Retrieve details of LVs assigned to individual users.
- **Get All LVs and VGs Details:** Fetch comprehensive details of all LVs and VGs in the system.
- **MongoDB Integration:** Record all LVM operations and their details in MongoDB for auditing and tracking.

## Project Structure

The project consists of the following main components:

1. **Scripts:** Python scripts for LVM operations.
2. **Controller:** A central controller to manage and coordinate LVM operations.
3. **Database:** MongoDB for recording operation details and system state.

## Requirements

- Python 3.x
- LVM2 installed on your Linux system
- MongoDB for recording and tracking operations
- Python libraries: `pymongo`, `subprocess`, `os`, `sys`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/lvm-automation.git
   cd lvm-automation
   ```
