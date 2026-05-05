import logging
import os
import signal
import subprocess

log = logging.getLogger("docit")

LOG_PATH = "/tmp/docit_watcher.log"


class LiveWatcher:
    def __init__(self, script_path, watch_dir):
        self.script_path = script_path
        self.watch_dir = watch_dir
        self.proc = None

    @property
    def is_running(self):
        return self.proc is not None and self.proc.poll() is None

    def _kill_orphans(self):
        try:
            result = subprocess.run(
                ["pkill", "-f", self.script_path],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            if result.returncode == 0:
                log.info("Killed orphan watcher(s) before starting")
        except Exception:
            log.exception("Failed to clean up orphan watchers")

    def start(self):
        if self.is_running:
            return
        if not os.path.isfile(self.script_path):
            log.error("Watcher script not found: %s", self.script_path)
            return
        self._kill_orphans()
        env = os.environ.copy()
        env["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + env.get("PATH", "")
        log_file = open(LOG_PATH, "a")
        self.proc = subprocess.Popen(
            ["bash", self.script_path, self.watch_dir, "0.5"],
            env=env,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        log.info("Live watcher started (pid=%s)", self.proc.pid)

    def stop(self):
        if self.proc is None:
            return
        if self.proc.poll() is None:
            try:
                os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
                self.proc.wait(timeout=3)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass
        log.info("Live watcher stopped")
        self.proc = None
