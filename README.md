# linuxcnc-proxy

![Python](https://img.shields.io/badge/Python-3.7%2B-blue?logo=python)
![License](https://img.shields.io/github/license/atrex66/linuxcnc-proxy?color=blue)

> **A modern Python proxy for LinuxCNC remote control and monitoring.**

---

## 🚀 Features

- **Remote Command Execution**: Send commands to LinuxCNC remotely.
- **Status Monitoring**: Query and monitor machine status in real-time.
- **Error Handling**: Robust error reporting and handling.
- **HAL Integration**: Interface with LinuxCNC HAL components.
- **Easy Integration**: Simple Python API for client applications.

---

## 📦 Project Structure

```text
linuxcnc-proxy/
├── linuxcnc_qt_demo.py      # Demo application
├── linuxcnc_remote/        # Core remote modules
│   ├── command.py
│   ├── error.py
│   ├── hal.py
│   ├── stat.py
│   └── __init__.py
├── proxy/
│   └── linuxcnc_proxy.py   # Proxy server implementation
├── LICENSE
└── README.md
```

---

## 🛠️ Installation

1. **Clone the repository:**
	 ```bash
	 git clone https://github.com/your-repo/linuxcnc-proxy.git
	 cd linuxcnc-proxy
	 ```
2. **(Optional) Create a virtual environment:**
	 ```bash
	 python3 -m venv venv
	 source venv/bin/activate
	 ```
3. **Install dependencies:**
	 ```bash
	 pip install -r requirements.txt
	 ```

---

## ⚡ Usage

- **Run the Proxy Server:**

	### On the LinuxCNC Host (Server)

	1. **Copy the proxy script to /usr/bin and make it executable:**
		```bash
		sudo cp proxy/linuxcnc_proxy.py /usr/bin/linuxcnc_proxy
		sudo chmod +x /usr/bin/linuxcnc_proxy
		```

	2. **Edit your LinuxCNC INI file:**
		In your INI file, set the display to use the proxy:
		```ini
		DISPLAY=linuxcnc_proxy
		```

	3. **Start LinuxCNC as usual.**

	---

	### On the Remote Client

	Import the remote library and use it as you would on a native LinuxCNC installation:

	```python
	import linuxcnc_remote as linuxcnc
	# Use linuxcnc.Command(), linuxcnc.Stat(), etc. as normal
	```

	---

	- **Demo Application:**
	  ```bash
	  python3 linuxcnc_qt_demo.py
	  ```

- See the source code for module-level documentation and usage examples.
- Main modules:
	- `linuxcnc_remote.command` — Remote command interface
	- `linuxcnc_remote.stat` — Status monitoring
	- `linuxcnc_remote.error` — Error handling
	- `linuxcnc_remote.hal` — HAL integration

---

## 🤝 Contributing

Contributions are welcome! Please open issues and pull requests to help improve this project.

---

## 📝 License

This project is licensed under the terms of the [LICENSE](LICENSE).
