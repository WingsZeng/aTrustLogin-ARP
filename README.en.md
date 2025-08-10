# aTrustLogin-ARP

Modified to adapt to the ARP frontend, with the address filled in by default. Only the account and password need to be entered.

Below is the original Readme

# aTrustLogin

[中文版本](/README.md)

This project provides an automated solution for logging into Sangfor aTrust, enabling VPN connectivity without manual intervention. The main features of the project are:

- Automatically opens the aTrust Web login page
- Auto-fills username and password
- Automatically derives and inputs TOTP two-factor authentication codes
- Bypasses CAPTCHA using cookie state
- KeepAlive connection for session persistence and auto-reconnection on logout or disconnection
- Supports Windows, Linux, x86-64, and ARM64

## Usage Instructions
The project provides two methods: Docker and General.

The **Docker method** is Linux-specific and requires no dependency installation or configuration, making it ideal for headless environments like soft routers or industrial PCs.

The **General method** works on all platforms but requires manual installation of Python 3.8+ and Selenium. If possible, use the Docker method.

### General Method

#### Browser Setup
- **Windows:** Uses the default Microsoft Edge browser for Windows 10 1903+ and Windows 11. No additional browser or driver installation is typically required. For other browsers, refer to the [Selenium Documentation](https://www.selenium.dev/documentation/en/webdriver/driver_requirements/) for driver installation.
- **Linux:** Requires Chromium. Install it on Debian/Ubuntu using:
  ```bash
  apt-get install -y chromium chromium-driver chromium-l10n
  ```

#### Project Setup
Download the project and install dependencies. Both domestic and international download options are provided. If international downloads are slow, use the domestic option.

**International Option:**
```bash
git clone --depth=1 https://github.com/kenvix/aTrustLogin.git aTrustLogin
cd aTrustLogin/src
pip install -r requirements.txt
```

Run the program with the parameters outlined in the "Program Parameters" section.

### Program Parameters

The following parameters are supported:

- `--portal_address`: VPN portal address (URL), e.g., `https://atrust.moe.edu.cn/`
- `--username`: VPN username
- `--password`: VPN password
- `--totp_key`: TOTP secret for two-factor authentication (optional)
- `--cookie_tid`: Cookie ID for session tracking (optional, to bypass CAPTCHA)
- `--cookie_sig`: Cookie signature for session tracking (optional, to bypass CAPTCHA)
- `--keepalive`: Optional. Session keep-alive interval in seconds. `0` disables it.
- `--data_dir`: Optional. Path to store cookies and session data.
- `--driver_type`: Optional. WebDriver type (e.g., "chrome", "edge").
- `--driver_path`: Optional. Path to the WebDriver executable.
- `--browser_path`: Optional. Path to the browser executable.
- `--interactive`: Optional. Enables interactive mode.
- `--wait_atrust`: Optional. Waits for aTrust to listen on the specified port.

**Example Command:**
```bash
python main.py --portal_address "https://example.com" --username "your_username" --password "your_password" --totp_key "your_totp_key" --cookie_tid "your_cookie_tid" --cookie_sig "your_cookie_sig" --keepalive 300 --interactive True --wait_atrust True
```

### Docker Method

Pull the Docker image using:
```bash
docker pull kenvix/atrust-autologin:latest
```

If downloads are slow, use the domestic address:
```bash
wget https://modelscope.cn/models/kenvix/aTrustLoginRepo/resolve/master/docker-atrust-autologin-amd64.tar.xz -O - | xz -dc | docker load
docker tag kenvix/docker-atrust-autologin:amd64 kenvix/docker-atrust-autologin:latest
```

Set program parameters in the `ATRUST_OPTS` environment variable and run the Docker container:
```bash
docker run -it --rm -e ATRUST_OPTS='--portal_address="your_portal" --username="your_username" --password="your_password"' kenvix/atrust-autologin:latest
```

To avoid CAPTCHA during the first login:
1. Log in via the aTrust webpage and input the CAPTCHA manually.
2. Save `tid` and `tid.sig` cookies from your browser's developer tools.
3. Add these values to `--cookie_tid` and `--cookie_sig`.

**Note:** By default, containers are temporary. For persistent data and auto-start on boot, replace `--rm` with `--restart unless-stopped`.

### CAPTCHA Bypass

To bypass the CAPTCHA:
1. Open the aTrust login webpage, log in, and input the CAPTCHA manually.
2. Open browser developer tools (F12) and go to the Application tab.
3. Find the `tid` and `tid.sig` cookies, copy their values, and use them in `--cookie_tid` and `--cookie_sig`.

![Cookie Example](doc/cookie.webp)

### Integration with FRP

FRP (Fast Reverse Proxy) is an intranet penetration tool. You can use FRP to map local aTrust services to a public server.

1. Edit the `run.sh` script in the `frpc` directory.
2. Download the FRP binary and place it in the `frpc/frp` directory.
3. Run `run.sh` to automatically create and start the Docker image with port mapping.
4. Use `run.sh` for future starts, not `docker start`.

For further options and environment variables (e.g., `PING_ADDR`, `PING_INTERVAL`), refer to the [docker-easyconnect documentation](https://github.com/docker-easyconnect/docker-easyconnect/blob/master/doc/usage.md).

