"""Own packaging subprocesses and temporary directories across catchable signals."""
from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile

SIGNALS = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)


@contextmanager
def deferred_signals():
    # Do not block OS signals: a spawned program must inherit normal masks.
    # Record the first signal instead of raising inside Popen/mkdtemp, where
    # ownership may not yet have been returned to Python. Check at safe points.
    pending = []
    previous = {}

    def remember(signum, frame):
        if not pending:
            pending.append(signum)

    def check():
        if pending:
            raise SystemExit(128 + pending[0])

    try:
        for sig in SIGNALS:
            previous[sig] = signal.signal(sig, remember)
        yield check
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)
        check()


def run_owned(argv, env=None):
    """Reap the owned session before returning or propagating an interruption."""
    with deferred_signals() as check:
        child = None
        try:
            child = subprocess.Popen(argv, env=env, start_new_session=True)
            while True:
                check()
                try:
                    rc = child.wait(timeout=0.1)
                    return rc if rc >= 0 else 128 - rc
                except subprocess.TimeoutExpired:
                    pass
        finally:
            if child is not None:
                # The session is ours, even if its leader has already exited.
                # Never let repeated signals interrupt this bounded cleanup.
                try:
                    os.killpg(child.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    pass
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                child.wait()


@contextmanager
def private_directory(**kwargs):
    """Register the exact new directory before honoring allocation-time signals."""
    path = None
    try:
        with deferred_signals():
            path = Path(tempfile.mkdtemp(**kwargs))
        yield path
    finally:
        with deferred_signals():
            if path is not None and path.exists():
                shutil.rmtree(path)
