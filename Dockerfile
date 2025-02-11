# 用于构建和设置变量
FROM python:3.12-alpine AS builder

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

#复制uv文件到工作目录中
COPY pyproject.toml ${WORKDIR}

COPY requirements.txt ${WORKDIR}

# 安装必要的环境

RUN apk add --no-cache --virtual .build-deps gcc git musl-dev curl  \
  && curl -LsSf https://astral.sh/uv/install.sh | sh \
  && source /root/.local/bin/env \
  && uv sync \
  && uv add -r ${WORKDIR}/requirements.txt \
  && apk del --purge .build-deps \
  && rm -rf /tmp/* /root/.cache /var/cache/apk/*

# 将从构建上下文目录中的文件和目录复制到新的一层的镜像内的工作目录中
COPY . .

# 将应用日志输出到stdout
RUN ln -sf /dev/stdout /app/default.log

# 定义容器启动时执行的默认命令
ENTRYPOINT ["/root/.local/bin/uv","run","app.py"]

