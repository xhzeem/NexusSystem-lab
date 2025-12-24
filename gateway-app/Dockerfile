FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exploitability features: make ping available for internal service if needed
RUN apt-get update && apt-get install -y iputils-ping curl unzip && rm -rf /var/lib/apt/lists/*

# Download Chisel for post-RCE tunneling
RUN curl -L -o /tmp/chisel.gz https://github.com/jpillora/chisel/releases/download/v1.8.1/chisel_1.8.1_linux_amd64.gz \
    && cd /tmp && gunzip chisel.gz \
    && mv chisel /usr/local/bin/chisel \
    && chmod +x /usr/local/bin/chisel \
    && rm -rf /tmp/*

EXPOSE 5000

CMD ["python", "app.py"]
