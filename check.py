import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import paramiko

HOST = "miko089.space"
USER = "boromir-max"
PASSWORD = "p@ssword"

def run(ssh, cmd, timeout=15):
    print(f"\n$ {cmd}")
    _, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode(errors="replace")
    err = stderr.read().decode(errors="replace")
    if out.strip(): print(out)
    if err.strip(): print("[err]", err[:300])

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)

# Is there a system nginx?
run(ssh, "systemctl status nginx 2>/dev/null | head -5 || echo 'no nginx service'")
run(ssh, "ls /etc/nginx/sites-enabled/ 2>/dev/null || ls /etc/nginx/conf.d/ 2>/dev/null || echo 'no nginx config dirs'")
# What's on port 80?
run(ssh, "ss -tlnp | grep ':80 '")
# Try curl from outside via the public IP
run(ssh, "curl -s -o /dev/null -w '%{http_code}' http://91.134.142.203:9999/ --connect-timeout 5")
# Check iptables without sudo
run(ssh, "iptables -L 2>&1 | head -5")

ssh.close()
print("\nDone.")
