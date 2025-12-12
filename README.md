# 🌐 SubZero (IPv4 Subnet Calculator)

## 📌 Overview

**SubZero** is a dedicated desktop application (GUI) designed for network engineers and students. Its primary function is to accurately and efficiently calculate and detail all aspects of **IPv4 Subnetting** and **Supernetting**.

The application features a dark-themed, user-friendly interface built using **Python** and the standard **Tkinter** library, ensuring quick deployment and ease of use.

## ✨ Features

* **Comprehensive Calculation:** Calculates all properties of the resultant network based on the input IP address and the **new** Prefix (CIDR) length.
* **Integrated Rules & Results:** Displays the calculated result alongside the fundamental mathematical rule used (e.g., $2^N - 2$) for clear educational value.
* **Binary View:** Provides the binary representation of the Network Address, Subnet Mask, and Broadcast Address.
* **Detailed Subnet Listing:** Generates a full list of all resulting subnets, showing the Network Address, First Host, Last Host, Broadcast Address, and Usable Host count for each.
* **Performance Optimized:** Efficiently handles large network divisions (like subnetting a /8 network) while limiting the display of subnets (e.g., to the first 256) to prevent system resource drain.
* **Usability Features:**
    * **Zoom Functionality:** Easily increase or decrease the font size using `Ctrl +` and `Ctrl -`.
    * **Copy Support:** Copy any cell or row content using `Ctrl + C` or right-click.

## 🛠️ Requirements

* **Python 3.x**
* The application relies on standard Python libraries: `tkinter` (for GUI) and `ipaddress` (for calculation logic), which are typically included with Python installations.

## 🚀 Usage

The program is designed to be run either directly via the compiled executable (for users) or as a Python script (for developers).

### 🔹 Windows (Executable)

1.  Run the compiled file, typically named `SubZero.exe`, directly.
2.  In the input field, paste the target IP address along with the **New Prefix** (Example: `192.168.1.50/26`).
3.  Click the **Calculate** button.
4.  Review the detailed results presented in the two tables below.

### 🔹 Run with Python (Cross-platform)

1.  Open your terminal or command prompt in the program directory.
2.  Execute the main script using Python:

```bash
python3 subzero_main.py

```
## 📸 Screenshot
![App Screenshot](https://github.com/user-attachments/assets/f879b1f8-5a4e-4761-aac1-716cc59f9cc5)


