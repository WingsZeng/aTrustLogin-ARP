FROM kenvix/docker-atrust-autologin:latest
LABEL authors="Wings"

ENV TZ="Asia/Shanghai"
COPY ./docker/bin /bin
COPY ./src /opt/atrust-autologin

# 再次定义 ARG 变量以确保构建过程中可以使用这些参数
ARG ANDROID_PATCH
ARG EC_HOST
ARG VPN_TYPE=EC_GUI
ARG VPN_URL
ARG ELECTRON_URL
ARG USE_VPN_ELECTRON
ARG VPN_DEB_PATH

# 重新定义 ENV 变量，以确保环境变量在最终镜像中可用
ENV PING_INTERVAL=1800

# 保留基础镜像的卷（这会继承 `/root` 和 `/usr/share/sangfor/EasyConnect/resources/logs/` 的设置）
VOLUME ["/root", "/usr/share/sangfor/EasyConnect/resources/logs/"]

RUN chmod +x /bin/start-with-autologin.sh && \
  chmod +x /bin/start-with-autologin-actual.sh && \
  chmod +x /bin/start-port-forwarding.sh

CMD ["/bin/start-with-autologin.sh"]
