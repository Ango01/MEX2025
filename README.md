# Raspberry Pi Python Project

This project runs on a Raspberry Pi and uses system-installed packages (e.g., `picamera2`) along with Python packages installed via `pip`. To ensure compatibility and reproducibility, we use a Python virtual environment **with access to system packages**.

---

## Requirements

- Raspberry Pi OS (Bookworm or newer recommended)
- Python 3
- `python3-venv` installed via `apt`
- System packages listed in `apt-requirements.txt`

---

## Setup Instructions 

### 1. Clone the Repository

```bash
git clone https://github.com/Ango01/MEX2025.git
cd MEX2025
```

### 2. Install System Dependencies

Make sure all system-wide dependencies (like `picamera2`) are installed:

```bash
sudo apt update
sudo apt install $(cat apt-requirements.txt)
```

### 3. Create and Activate a Virtual Environment

Create a virtual environment that has access to system-wide packages:

```bash
python3 -m venv venv --system-site-packages
source venv/bin/activate
```

### 4. Install Python Packages (via pip)

Install Python packages listed in requirements.txt:

```bash
pip install -r requirements.txt
```

### 5. Run the Application

With the virtual environment activated, run Python script:

```bash
python app.py
```