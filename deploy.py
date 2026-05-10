import os
import sys
import paramiko
import stat

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HOST = "miko089.space"
USER = "boromir-max"
PASSWORD = "p@ssword"
REMOTE_DIR = "/home/boromir-max/clutchup"

LOCAL_ROOT = os.path.dirname(os.path.abspath(__file__))

SKIP_DIRS = {"node_modules", "__pycache__", ".git", "dist", ".pytest_cache", "htmlcov", ".venv", "venv"}
SKIP_EXTS = {".pyc", ".db"}

UPLOAD_PATHS = [
    ("backend", "backend"),
    ("frontend", "frontend"),
    ("podman-compose.yml", "podman-compose.yml"),
]


def should_skip(name):
    return name in SKIP_DIRS or any(name.endswith(e) for e in SKIP_EXTS)


def upload_dir(sftp, local_path, remote_path):
    try:
        sftp.stat(remote_path)
    except FileNotFoundError:
        sftp.mkdir(remote_path)

    for item in os.listdir(local_path):
        if should_skip(item):
            continue
        local_item = os.path.join(local_path, item)
        remote_item = remote_path + "/" + item
        if os.path.isdir(local_item):
            upload_dir(sftp, local_item, remote_item)
        else:
            print(f"  upload: {remote_item}")
            sftp.put(local_item, remote_item)


def run(ssh, cmd):
    print(f"\n$ {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    out = stdout.read().decode(errors="replace")
    err = stderr.read().decode(errors="replace")
    if out:
        print(out.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))
    if err:
        print("[stderr]", err.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))
    return stdout.channel.recv_exit_status()


def main():
    print(f"Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
    print("Connected.")

    sftp = ssh.open_sftp()

    # Create remote root dir
    try:
        sftp.stat(REMOTE_DIR)
    except FileNotFoundError:
        sftp.mkdir(REMOTE_DIR)

    # Upload files
    for local_rel, remote_rel in UPLOAD_PATHS:
        local_abs = os.path.join(LOCAL_ROOT, local_rel)
        remote_abs = REMOTE_DIR + "/" + remote_rel
        if os.path.isdir(local_abs):
            print(f"\nUploading dir: {local_rel} -> {remote_abs}")
            upload_dir(sftp, local_abs, remote_abs)
        else:
            print(f"\nUploading file: {local_rel} -> {remote_abs}")
            sftp.put(local_abs, remote_abs)

    sftp.close()
    print("\nUpload complete.")

    # Build and start containers
    rc = run(ssh, f"cd {REMOTE_DIR} && podman-compose down 2>/dev/null; true")
    rc = run(ssh, f"cd {REMOTE_DIR} && podman-compose up --build -d")
    if rc != 0:
        print("ERROR: podman-compose failed")
        ssh.close()
        return

    # Quick health check
    import time
    print("\nWaiting 10s for containers to start...")
    time.sleep(10)
    rc = run(ssh, "curl -s -o /dev/null -w '%{http_code}' http://localhost:9999/")
    run(ssh, "curl -s http://localhost:8000/health")
    run(ssh, "podman ps")

    ssh.close()
    print("\nDone. Site should be live at http://catstest.miko089.space:9999")


if __name__ == "__main__":
    main()
