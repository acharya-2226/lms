import atexit
import base64
import socket
import subprocess
import threading
import time
from pathlib import Path

import webview


HOST = "127.0.0.1"
PORT = 8000
URL = f"http://{HOST}:{PORT}/"


class DesktopApi:
    def save_download(self, payload: dict) -> dict:
        try:
            filename = str(payload.get('filename') or 'download.bin')
            content_b64 = payload.get('content_b64')
            if not content_b64:
                return {'ok': False, 'error': 'No file content provided.'}

            response_bytes = base64.b64decode(content_b64)

            selected_path = webview.windows[0].create_file_dialog(
                webview.SAVE_DIALOG,
                save_filename=filename,
            )
            if not selected_path:
                return {'ok': False, 'cancelled': True, 'error': 'Save cancelled by user.'}

            output_path = selected_path[0] if isinstance(selected_path, (list, tuple)) else selected_path
            with open(output_path, 'wb') as file_handle:
                file_handle.write(response_bytes)

            return {'ok': True, 'path': output_path}
        except Exception as exc:
            return {'ok': False, 'error': str(exc)}


class LMSDesktopApp:
    def __init__(self) -> None:
        self.project_dir = self._find_project_dir()
        self.python_exe = self._find_python_executable()
        self.server_process = None
        self._log_thread = None
        atexit.register(self.stop_server)

    def _find_project_dir(self) -> Path:
        candidates = [Path(__file__).resolve().parent, Path.cwd()]
        for candidate in candidates:
            if (candidate / "manage.py").exists():
                return candidate
            parent = candidate.parent
            if (parent / "manage.py").exists():
                return parent
        raise FileNotFoundError("Could not find manage.py. Put this app in your LMS project folder.")

    def _find_python_executable(self) -> Path:
        candidates = [
            self.project_dir / "env" / "Scripts" / "python.exe",
            self.project_dir / ".venv" / "Scripts" / "python.exe",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return Path("python")

    def _is_port_open(self) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            return sock.connect_ex((HOST, PORT)) == 0

    def _wait_for_server(self, timeout_seconds: int = 25) -> bool:
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            if self._is_port_open():
                return True
            time.sleep(0.25)
        return False

    def _stream_logs(self) -> None:
        if not self.server_process or not self.server_process.stdout:
            return
        for line in self.server_process.stdout:
            # Keep logs available in console/dev use; hidden in windowed EXE.
            print(line.rstrip())

    def start_server(self) -> None:
        if self.server_process and self.server_process.poll() is None:
            return

        self.server_process = subprocess.Popen(
            [str(self.python_exe), "manage.py", "runserver", f"{HOST}:{PORT}", "--noreload"],
            cwd=self.project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

        self._log_thread = threading.Thread(target=self._stream_logs, daemon=True)
        self._log_thread.start()

    def stop_server(self) -> None:
        if not self.server_process or self.server_process.poll() is not None:
            return
        self.server_process.terminate()
        try:
            self.server_process.wait(timeout=6)
        except subprocess.TimeoutExpired:
            self.server_process.kill()

    def run(self) -> None:
        self.start_server()
        if not self._wait_for_server():
            raise RuntimeError("LMS server did not start in time.")

        api = DesktopApi()

        window = webview.create_window(
            "LMS Desktop",
            URL,
            width=1280,
            height=820,
            min_size=(980, 640),
            js_api=api,
        )

        def on_closed() -> None:
            self.stop_server()

        window.events.closed += on_closed
        webview.start()


def main() -> None:
    app = LMSDesktopApp()
    app.run()


if __name__ == "__main__":
    main()
