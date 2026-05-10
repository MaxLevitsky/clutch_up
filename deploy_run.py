import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import paramiko
import time

HOST = "miko089.space"
USER = "boromir-max"
PASSWORD = "p@ssword"
REMOTE_DIR = "/home/boromir-max/clutchup"


def run(ssh, cmd, timeout=300):
    print(f"\n$ {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True, timeout=timeout)
    out = stdout.read().decode(errors="replace")
    err = stderr.read().decode(errors="replace")
    rc = stdout.channel.recv_exit_status()
    if out.strip():
        print(out)
    if err.strip():
        print("[stderr]", err)
    print(f"[exit {rc}]")
    return rc


ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
print("Connected.")

# Stop catosite to free port 9999
run(ssh, "podman stop catosite 2>/dev/null || true")
run(ssh, "podman rm catosite 2>/dev/null || true")

# Stop existing clutchup containers
run(ssh, f"cd {REMOTE_DIR} && podman-compose down 2>/dev/null || true")

# Upload updated Dockerfile for frontend
sftp = ssh.open_sftp()
sftp.put(
    r"C:\Users\Maksim.Levitskii\Projects\AISlopTry2\frontend\Dockerfile",
    f"{REMOTE_DIR}/frontend/Dockerfile"
)
sftp.put(
    r"C:\Users\Maksim.Levitskii\Projects\AISlopTry2\backend\Dockerfile",
    f"{REMOTE_DIR}/backend/Dockerfile"
)
print("Uploaded Dockerfiles")
sftp.close()

# Build and start
rc = run(ssh, f"cd {REMOTE_DIR} && podman-compose up --build -d", timeout=600)

if rc != 0:
    print("Build failed, checking logs...")
    run(ssh, f"cd {REMOTE_DIR} && podman-compose logs --tail=50")
else:
    print("\nWaiting 15s for startup...")
    time.sleep(15)
    run(ssh, "curl -s -o /dev/null -w 'frontend HTTP: %{http_code}\\n' http://localhost:9999/")
    run(ssh, "curl -s http://localhost:8000/health")
    run(ssh, "podman ps --format 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}'")

ssh.close()
