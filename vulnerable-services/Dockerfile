FROM ubuntu:20.04

# Avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install vulnerable services and tools
RUN apt-get update && apt-get install -y \
    vsftpd \
    samba \
    apache2 \
    openssh-server \
    telnetd \
    rsh-redone-server \
    tftpd \
    python3 \
    python3-pip \
    wget \
    curl \
    vim \
    netcat \
    nmap \
    && rm -rf /var/lib/apt/lists/*

# Install Python vulnerable services
RUN pip3 install flask==2.0.1 pyftpdlib==1.5.6

# Create vulnerable FTP configuration
RUN echo "anonymous_enable=YES" >> /etc/vsftpd.conf \
    && echo "write_enable=YES" >> /etc/vsftpd.conf \
    && echo "anon_root=/srv/ftp" >> /etc/vsftpd.conf \
    && echo "no_anon_password=YES" >> /etc/vsftpd.conf \
    && echo "anon_upload_enable=YES" >> /etc/vsftpd.conf

# Create vulnerable SMB configuration
RUN echo "[global]" > /etc/samba/smb.conf \
    && echo "   workgroup = WORKGROUP" >> /etc/samba/smb.conf \
    && echo "   server string = Vulnerable SMB Server" >> /etc/samba/smb.conf \
    && echo "   security = share" >> /etc/samba/smb.conf \
    && echo "   map to guest = Bad User" >> /etc/samba/smb.conf \
    && echo "" >> /etc/samba/smb.conf \
    && echo "[public]" >> /etc/samba/smb.conf \
    && echo "   path = /srv/samba/public" >> /etc/samba/smb.conf \
    && echo "   browsable = yes" >> /etc/samba/smb.conf \
    && echo "   writable = yes" >> /etc/samba/smb.conf \
    && echo "   guest ok = yes" >> /etc/samba/smb.conf \
    && echo "   read only = no" >> /etc/samba/smb.conf

# Create vulnerable SSH configuration
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config \
    && echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config \
    && echo "PermitEmptyPasswords yes" >> /etc/ssh/sshd_config

# Create directories and files for exploitation
RUN mkdir -p /srv/ftp/uploads \
    && mkdir -p /srv/samba/public \
    && mkdir -p /var/www/html/uploads \
    && echo "root:password123" | chpasswd \
    && useradd -m user && echo "user:user123" | chpasswd

# Create vulnerable web files
RUN echo "<?php system(\$_GET['cmd']); ?>" > /var/www/html/shell.php \
    && echo "<?php echo file_get_contents(\$_GET['file']); ?>" > /var/www/html/lfi.php \
    && echo "<?php include(\$_GET['page']); ?>" > /var/www/html/rfi.php

# Create FTP files with sensitive data
RUN echo "FTP Server Configuration File" > /srv/ftp/config.txt \
    && echo "admin:admin123" >> /srv/ftp/config.txt \
    && echo "database_password: secret_db_pass" >> /srv/ftp/config.txt

# Create SMB files
RUN echo "SMB Share - Sensitive Data" > /srv/samba/public/secrets.txt \
    && echo "api_key: sk-1234567890abcdef" >> /srv/samba/public/secrets.txt

# Create vulnerable Python web service
RUN cat > /vulnerable_web.py << 'EOF'
from flask import Flask, request, render_template_string
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <h1>Vulnerable Web Service</h1>
    <ul>
        <li><a href="/ping?ip=127.0.0.1">Ping Service (RCE)</a></li>
        <li><a href="/read?file=/etc/passwd">File Reader (LFI)</a></li>
        <li><a href="/exec?cmd=ls">Command Execution (RCE)</a></li>
    </ul>
    '''

@app.route('/ping')
def ping():
    ip = request.args.get('ip', '127.0.0.1')
    try:
        result = subprocess.check_output(f'ping -c 2 {ip}', shell=True, text=True)
        return f"<pre>{result}</pre>"
    except Exception as e:
        return f"<pre>Error: {e}</pre>"

@app.route('/read')
def read_file():
    file_path = request.args.get('file', '/etc/passwd')
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return f"<pre>{content}</pre>"
    except Exception as e:
        return f"<pre>Error: {e}</pre>"

@app.route('/exec')
def exec_cmd():
    cmd = request.args.get('cmd', 'ls')
    try:
        result = subprocess.check_output(cmd, shell=True, text=True)
        return f"<pre>{result}</pre>"
    except Exception as e:
        return f"<pre>Error: {e}</pre>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
EOF

# Create startup script
RUN cat > /start.sh << 'EOF'
#!/bin/bash

# Start all vulnerable services
service vsftpd start
service smbd start
service ssh start
service apache2 start

# Create vulnerable telnet configuration
echo "telnet stream tcp nowait root /usr/sbin/telnetd telnetd" >> /etc/inetd.conf
service openbsd-inetd start

# Start Python vulnerable web service
python3 /vulnerable_web.py &

# Keep container running
tail -f /dev/null
EOF

RUN chmod +x /start.sh

EXPOSE 21 22 23 80 139 445 8080

CMD ["/start.sh"]
