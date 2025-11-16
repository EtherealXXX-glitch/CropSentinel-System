# 使用官方轻量 Python 镜像
FROM python:3.11-slim

WORKDIR /app

# 复制 receiver.py 和 requirements.txt 到容器
COPY ../receiver.py ./ 
COPY ../requirements.txt ./ 

# 升级 pip 并安装依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 启动脚本
CMD ["python", "receiver.py"]
