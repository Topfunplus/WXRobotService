# 使用官方 Python 镜像作为基础镜像
FROM python:3.9-slim
# 设置工作目录
WORKDIR /app
# 安装依赖（如果需要安装包，可以使用清华源）
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
# 拷贝当前目录下的所有文件到容器中的 /app 目录
COPY . /app
# 设置环境变量（可选）
ENV PYTHONUNBUFFERED=1

# 添加 entrypoint.sh
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# 设置入口点
ENTRYPOINT ["/entrypoint.sh"]