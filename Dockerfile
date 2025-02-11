# 用于构建和设置变量
FROM python:3.12-alpine AS builder

# 将requirements.txt复制到新的一层的镜像内的构建上下文目录中
RUN mkdir -p /tmp/build-base
COPY requirements.txt /tmp/build-base

# 安装必要的环境
RUN apk add --no-cache --virtual .build-deps gcc git musl-dev \
    && pip install -r /tmp/build-base/requirements.txt \
    && apk del --purge .build-deps \
    && rm -rf /tmp/* /root/.cache /var/cache/apk/*

# 设置时区为Asia/Shanghai, DOCKER_MODE为1
ENV TZ=Asia/Shanghai \
    DOCKER_MODE=1 \
    PUID=0 \
    PGID=0 \
    UMASK=000 \
    PYTHONWARNINGS="ignore:semaphore_tracker:UserWarning" \
    WORKDIR="/app"

# 设置默认工作目录
WORKDIR ${WORKDIR}

# 将从构建上下文目录中的文件和目录复制到新的一层的镜像内的工作目录中
COPY . .

# 将应用日志输出到stdout
RUN ln -sf /dev/stdout /app/default.log

# 定义容器启动时执行的默认命令
ENTRYPOINT ["python3"]

# 设置默认的CMD为app.py，这样在容器启动时会自动执行app.py
CMD ["app.py"]