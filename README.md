# aTrustLogin-ARP

修改以适配 ARP 前端，并默认填写地址，只需要填写账号和密码即可。

下面是原 Readme

# aTrustLogin

[English Version](/README.en.md)

本项目提供了一个自动化的深信服 Sangfor aTrust 登录的解决方案，无需人工干预即可实现 VPN 联网。项目功能如下：

- 自动打开 aTrust Web 登录页面
- 自动填写用户名和密码
- 自动利用密钥推导 TOTP 两步验证并填写
- 使用 Cookie 状态绕过验证码
- KeepAlive 连接保活和掉线/登出重连
- 支持 Windows、Linux，支持 x86-64 和 ARM64
- (Docker) 支持端口转发，容器暴露端口然后自动转发到指定地址

## 使用方法
本项目提供Docker方法和通用方法两种方法。

Docker 方法只适用于 Linux 平台，但无需安装配置任何依赖，全自动运行，只需安装 Docker 即可。非常适合软路由、工控机等无图形界面的环境使用。

通用方法适合于所有平台，但需要手动安装 Python 3.8+ 和 Selenium 等依赖库。如果有条件，请使用 Docker 方法。

### 通用方法

首先需要配置浏览器。

在 Windows 下，默认使用系统自带的 Microsoft Edge 浏览器，因此对于 Windows 10 1903+、Windows 11 通常不需要额外安装浏览器和浏览器驱动。如果需要使用其他浏览器，请参考 [Selenium 文档](https://www.selenium.dev/documentation/en/webdriver/driver_requirements/) 安装对应的浏览器驱动。

在 Linux 下，需要安装 Chromium 浏览器。Debian/Ubuntu 可以使用 `apt-get install -y chromium chromium-driver chromium-l10n` 命令直接安装。

然后，下载本项目，安装依赖库。提供国内地址和国外地址两个下载方法。如果国外地址下载缓慢，可以使用国内地址：

国外地址：

```shell
git clone --depth=1 https://github.com/kenvix/aTrustLogin.git aTrustLogin
cd aTrustLogin/src
pip install -r requirements.txt
```

然后按照 “程序运行参数说明” 章节启动程序即可。

### 程序运行参数说明

各参数的说明如下：

- `--portal_address`：VPN 门户地址（URL）。例如 https://atrust.moe.edu.cn/
- `--username`：VPN 用户名。
- `--password`：VPN 密码。
- `--totp_key`：TOTP 密钥，用于双因素验证（可选，如果不需要双因素验证则无需提供）。
- `--cookie_tid`：用于会话追踪的 cookie ID（可选，用于绕过图形验证码）。具体见后文
- `--cookie_sig`：用于会话追踪的 cookie 签名（可选，用于绕过图形验证码）。具体见后文
- `--keepalive`：可选。会话保持时间（秒），每隔几秒后刷新页面检查是否掉线。0 为禁用
- `--data_dir`：可选。存储 cookies 和会话数据的目录路径。
- `--driver_type`：可选。WebDriver 类型（如 "chrome" 或 "edge"）。
- `--driver_path`：可选。WebDriver 可执行文件路径。
- `--browser_path`：可选。浏览器可执行文件路径。
- `--interactive`：可选。是否启用交互模式。
- `--wait_atrust`：可选。是否等待 aTrust 在指定端口上监听。用于等待 atrust 启动。

示例：

```shell
python main.py --portal_address "https://example.com" --username "your_username" --password "your_password" --totp_key "your_totp_key" --cookie_tid "your_cookie_tid" --cookie_sig "your_cookie_sig" --keepalive 300 --interactive True --wait_atrust True
```

### Docker 方法

首先使用下面的命令拉取镜像：

```shell
# 拉取最新版本（国外地址，如果下载缓慢请使用国内地址）
docker pull kenvix/atrust-autologin:latest
```

Docker 镜像如果下载缓慢，可以替换为国内地址。下载后使用 `xz -dc 文件名.tar.xz | docker load` 命令导入镜像。

国内地址请参见：https://modelscope.cn/models/kenvix/aTrustLoginRepo/files

```shell
# 使用国内地址拉取镜像
# 其中 amd64 表示架构x86-64，如果是 ARM64 请替换为 arm64
wget https://modelscope.cn/models/kenvix/aTrustLoginRepo/resolve/master/docker-atrust-autologin-amd64.tar.xz -O - | xz -dc | docker load
docker tag kenvix/docker-atrust-autologin:amd64 kenvix/docker-atrust-autologin:latest
```

阅读“程序运行参数说明” ，然后请将程序参数填入 `ATRUST_OPTS` 环境变量中，然后运行 Docker 容器即可。

```shell
docker run -it --rm -e ATRUST_OPTS='--portal_address="门户地址" --username=用户名 --password=密码 --totp_key=TOTP密钥 --cookie_tid "your_cookie_tid" --cookie_sig "your_cookie_sig" --device /dev/net/tun --cap-add NET_ADMIN -ti -e PASSWORD=xxxx -e URLWIN=1 -v $HOME/.atrust-data:/root -p 127.0.0.1:5901:5901 -p 127.0.0.1:8888:8888 --sysctl net.ipv4.conf.default.route_localnet=1 --shm-size 256m  kenvix/atrust-autologin:latest
```

cookie_sig 和 cookie_tid 可以不必设置，如果不设置，首次登录会遇到验证码，但是可以通过 VNC 远程连接服务器（VNC 端口 5901 ），手动输入验证码，然后程序会自动保存 cookie，之后就不会再遇到验证码了。

注意：**此命令默认创建的是临时容器**！容器停止或系统重启后就会删除！如果需要保存数据并且开机自动启动，请将 `--rm` 替换为 `--restart unless-stopped`。

默认带有每隔 `200` 秒的刷新登录保活机制，如果不需要此功能，可以在 `ATRUST_OPTS` 中添加 `--keepalive 0` 参数。也可以通过 `--keepalive` 参数设置保活时间，单位为秒。即 `docker run -it -e ATRUST_OPTS='--keepalive 0 ...其他参数' ...其他参数 kenvix/atrust-autologin:latest`

如果还需要发包保活功能，请添加 Docker `PING_ADDR` 和 `PING_INTERVAL` 环境变量，具体[参见此处](https://github.com/docker-easyconnect/docker-easyconnect/blob/master/doc/usage.md)。指定的服务器地址必须是 VPN 可到达的，例如 `docker run -it -e PING_ADDR=172.20.0.1 -e PING_INTERVAL=200 ...其他参数`。

`--shm-size 256m` 参数指定的 shm 大小不建议小于 256M，否则可能导致浏览器崩溃。

Docker 容器基于 [docker-easyconnect](https://github.com/docker-easyconnect/docker-easyconnect) 构建，在此表达感谢。其他的 Docker 参数也可以在这里找到。

## 如何绕过图形验证码

在第一次登录时，aTrust 会要求输入验证码。为了避免每次登录都需要输入验证码，可以通过以下方法绕过：

1. 打开 aTrust 登录网页，登录并输入验证码
2. 在浏览器中打开开发者工具（F12），切换到 Application（应用程序） 选项卡
3. 在左侧导航栏中找到 Cookies，点击对应的网站地址
4. 找到名为 `tid` 和 `tid.sig` 的两个 Cookie，将其“值”复制下来，填入程序的 `--cookie_tid` 和 `--cookie_sig` 参数中即可。

![Cookie](doc/cookie.webp)

## (Docker) 如何访问、如何端口转发

对于 Docker 容器，通过 Socks5 或 HTTP 代理访问内网网络。具体[参见此处](https://github.com/docker-easyconnect/docker-easyconnect/blob/master/doc/usage.md#%E4%BB%A3%E7%90%86%E6%9C%8D%E5%8A%A1)

容器支持直接设置端口转发以便访问内网服务而不经过 Socks5 代理。例如，如果你的 VPN 客户端在内网，可以使用 Docker 容器将你的本地服务映射到隧道另一侧的服务器上。方法是，添加 Docker 参数环境变量 `FORWARD_PORTS` ，该变量是一组将要转发的端口列表，用,分隔，格式是 `本地端口:远程IP:远程IP`，例如 `FORWARD_PORTS=41301:172.29.1.85:11111,41302:172.29.1.85:7777` 表示监听本地端口 `41301` ，然后转发到 `172.29.1.85:11111` ，监听本地端口 `41302` ，然后转发到 `172.29.1.85:7777`。最终参数如下：

```shell
-e 'FORWARD_PORTS=41301:172.29.1.85:11111,41302:172.29.1.85:7777' -p 41301:41301 -p 41302:41302
```

## 如何与 FRP 结合使用

Frp 是一套内网穿透工具，可以将内网服务映射出去。如果你的 VPN 客户端在内网，可以使用 Frp 将你的本地服务结合 ATrust 映射到隧道另一侧的服务器上。

由于 Frp 更新速度非常快且各个版本之间不兼容，本项目无法直接提供带 Frp 版本的镜像，但是，您可以查看 frp 目录下的脚本，实现自动登录并映射端口到 VPN 隧道另一侧的服务器上。

具体操作方法：

1. 进入 frpc 目录，修改 `run.sh` 文件的 18、23、85 行
2. 下载 frpc 发行版二进制文件，复制到 `frpc/frp` 下
3. 运行 `run.sh` 脚本，即可自动创建、自动启动 Docker 镜像，实现自动登录并映射端口到隧道另一侧的服务器上
4. 后续启动 Docker 容器均需要使用 `run.sh` 命令，不要使用 `docker start` 命令
