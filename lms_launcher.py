import socket
import subprocess
import threading
import time
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext


HOST = "127.0.0.1"
PORT = 8000


class LMSLauncher:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("LMS Launcher")
        self.root.geometry("760x460")
        self.root.minsize(700, 420)

        self.server_process = None
        self.project_dir = self._find_project_dir()
        self.python_exe = self._find_python_executable()

        self._build_ui()
        self.log("Project: {}".format(self.project_dir))
        self.log("Python: {}".format(self.python_exe))
        self.log("Auto-start enabled. Launching LMS...")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(350, self.start_server)

    def _build_ui(self) -> None:
        top = tk.Frame(self.root, padx=12, pady=12)
        top.pack(fill="x")

        self.status_var = tk.StringVar(value="Status: Stopped")
        tk.Label(top, textvariable=self.status_var, font=("Segoe UI", 10, "bold")).pack(anchor="w")

        button_bar = tk.Frame(top)
        button_bar.pack(anchor="w", pady=(10, 0))

        self.start_btn = tk.Button(button_bar, text="Start LMS", width=14, command=self.start_server)
        self.start_btn.grid(row=0, column=0, padx=(0, 8))

        self.stop_btn = tk.Button(button_bar, text="Stop LMS", width=14, state="disabled", command=self.stop_server)
        self.stop_btn.grid(row=0, column=1, padx=(0, 8))

        self.open_btn = tk.Button(button_bar, text="Open in Browser", width=14, command=self.open_browser)
        self.open_btn.grid(row=0, column=2, padx=(0, 8))

        tk.Label(
            top,
            text="Fast launch mode: opens as app and starts LMS automatically.",
            fg="#355070",
        ).pack(anchor="w", pady=(10, 0))

        log_frame = tk.Frame(self.root, padx=12, pady=(0, 12))
        log_frame.pack(fill="both", expand=True)
        self.log_box = scrolledtext.ScrolledText(log_frame, wrap="word", state="disabled")
        self.log_box.pack(fill="both", expand=True)

    def _find_project_dir(self) -> Path:
        candidates = [Path(__file__).resolve().parent, Path.cwd()]
        for candidate in candidates:
            if (candidate / "manage.py").exists():
                return candidate
            parent = candidate.parent
            if (parent / "manage.py").exists():
                return parent
        raise FileNotFoundError("Could not find manage.py. Put this launcher in your LMS project folder.")

    def _find_python_executable(self) -> Path:
        candidates = [
            self.project_dir / "env" / "Scripts" / "python.exe",
            self.project_dir / ".venv" / "Scripts" / "python.exe",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate

        return Path("python")

    def log(self, message: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        line = "[{}] {}\n".format(timestamp, message)
        self.log_box.configure(state="normal")
        self.log_box.insert("end", line)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _run_command(self, command: list[str], title: str) -> int:
        self.log("{}: {}".format(title, " ".join(str(item) for item in command)))
        process = subprocess.Popen(
            command,
            cwd=self.project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        assert process.stdout is not None
        for line in process.stdout:
            self.log(line.rstrip())
        process.wait()
        return process.returncode

    def _is_port_open(self) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.4)
            return sock.connect_ex((HOST, PORT)) == 0

    def _wait_for_server(self, timeout_seconds: int = 20) -> bool:
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            if self._is_port_open():
                return True
            time.sleep(0.3)
        return False

    def start_server(self) -> None:
        if self.server_process and self.server_process.poll() is None:
            self.log("Server is already running.")
            return

        def worker() -> None:
            try:
                self.log("Starting Django server...")
                self.server_process = subprocess.Popen(
                    [str(self.python_exe), "manage.py", "runserver", "{}:{}".format(HOST, PORT), "--noreload"],
                    cwd=self.project_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )

                self._set_running_state(starting=True)

                if self.server_process.stdout is not None:
                    threading.Thread(target=self._stream_server_logs, daemon=True).start()

                if self._wait_for_server():
                    self.log("Server is up at http://{}:{}/".format(HOST, PORT))
                    self.status_var.set("Status: Running")
                    self.open_browser()
                else:
                    self.log("Server did not become ready in time.")
            except Exception as exc:
                self.log("Error: {}".format(exc))
                self._set_stopped_state()

        threading.Thread(target=worker, daemon=True).start()

    def _stream_server_logs(self) -> None:
        assert self.server_process is not None
        assert self.server_process.stdout is not None
        for line in self.server_process.stdout:
            self.log(line.rstrip())
        code = self.server_process.poll()
        self.log("Server exited (code {}).".format(code))
        self._set_stopped_state()

    def stop_server(self) -> None:
        if not self.server_process or self.server_process.poll() is not None:
            self.log("Server is not running.")
            self._set_stopped_state()
            return

        self.log("Stopping server...")
        self.server_process.terminate()
        try:
            self.server_process.wait(timeout=6)
        except subprocess.TimeoutExpired:
            self.log("Force killing server process...")
            self.server_process.kill()
        self._set_stopped_state()

    def open_browser(self) -> None:
        url = "http://{}:{}/".format(HOST, PORT)
        webbrowser.open(url)
        self.log("Opened {}".format(url))

    def _set_running_state(self, starting: bool = False) -> None:
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.status_var.set("Status: Starting..." if starting else "Status: Running")

    def _set_stopped_state(self) -> None:
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_var.set("Status: Stopped")

    def on_close(self) -> None:
        if self.server_process and self.server_process.poll() is None:
            if not messagebox.askyesno("Exit", "LMS server is running. Stop and exit?"):
                return
            self.stop_server()
        self.root.destroy()


def main() -> None:
    app = tk.Tk()
    LMSLauncher(app)
    app.mainloop()


if __name__ == "__main__":
    main()
