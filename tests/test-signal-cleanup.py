#!/usr/bin/env python3
"""封装层回归：真实子进程、精确时序注入；不改镜像中的生产实现。"""
import importlib.machinery
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

source = Path(sys.argv.pop(1)) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'docker'
sys.path.insert(0, str(source))
import taf_repeatmasker_runtime as runtime
launcher = importlib.machinery.SourceFileLoader('launcher', str(source / 'RepeatMasker')).load_module()
installer_path = source / ('taf-repeatmasker-dfam' if (source / 'taf-repeatmasker-dfam').exists() else 'taf-repeatmasker-dfam.py')
installer = importlib.machinery.SourceFileLoader('installer', str(installer_path)).load_module()


class Cleanup(unittest.TestCase):
    def test_child_windows(self):
        real_popen = subprocess.Popen
        for owner in ('launcher', 'installer'):
            for phase in ('before-return', 'after-assignment', 'waiting', 'repeated-cleanup'):
                for sig in runtime.SIGNALS:
                    with self.subTest(owner=owner, phase=phase, signal=sig.name):
                        children = []
                        previous = {s: signal.getsignal(s) for s in runtime.SIGNALS}
                        fired = False
                        def inject():
                            nonlocal fired
                            if not fired:
                                fired = True
                                os.kill(os.getpid(), sig)
                        def spawn(*args, **kwargs):
                            child = real_popen(*args, **kwargs)
                            children.append(child)
                            if phase in ('before-return', 'repeated-cleanup'):
                                inject()
                            elif phase == 'waiting':
                                wait = child.wait
                                def interrupted_wait(*args, **kwargs):
                                    inject()
                                    return wait(*args, **kwargs)
                                child.wait = interrupted_wait
                            return child
                        def trace(frame, event, arg):
                            if phase == 'after-assignment' and event == 'line' and frame.f_code is runtime.run_owned.__code__:
                                if frame.f_locals.get('child') is not None:
                                    inject()
                            return trace
                        killpg = os.killpg
                        def kill(group, signum):
                            if phase == 'repeated-cleanup':
                                os.kill(os.getpid(), signal.SIGINT)
                                os.kill(os.getpid(), signal.SIGTERM)
                            return killpg(group, signum)
                        try:
                            with patch.object(subprocess, 'Popen', spawn), patch.object(os, 'killpg', kill):
                                sys.settrace(trace)
                                with self.assertRaises(SystemExit) as result:
                                    argv = [sys.executable, '-c', 'import time; time.sleep(30)']
                                    if owner == 'launcher':
                                        launcher.run(argv, dict(os.environ))
                                    else:
                                        installer.run_child(argv)
                                self.assertEqual(result.exception.code, 128 + sig)
                        finally:
                            sys.settrace(None)
                            for child in children:
                                if child.poll() is None:
                                    os.killpg(child.pid, signal.SIGKILL)
                                    child.wait()
                                    self.fail('owned child survived cleanup')
                        self.assertTrue(fired)
                        self.assertEqual(len(children), 1)
                        self.assertEqual(previous, {s: signal.getsignal(s) for s in runtime.SIGNALS})

    def test_directory_allocation_windows(self):
        real_mkdtemp = tempfile.mkdtemp
        for sig in runtime.SIGNALS:
            for phase in ('allocation', 'body', 'cleanup'):
                with self.subTest(signal=sig.name, phase=phase), tempfile.TemporaryDirectory() as parent:
                    made = []
                    def make(**kwargs):
                        name = real_mkdtemp(**kwargs)
                        made.append(Path(name))
                        if phase == 'allocation':
                            os.kill(os.getpid(), sig)
                        return name
                    remove = runtime.shutil.rmtree
                    def cleanup(path):
                        if phase == 'cleanup':
                            os.kill(os.getpid(), sig)
                        return remove(path)
                    previous = {s: signal.signal(s, launcher.interrupted) for s in runtime.SIGNALS}
                    try:
                        with patch.object(tempfile, 'mkdtemp', make), patch.object(runtime.shutil, 'rmtree', cleanup):
                            with self.assertRaises(SystemExit) as result:
                                with runtime.private_directory(dir=parent) as owned:
                                    (owned / 'owned').write_text('fixture')
                                    if phase == 'body':
                                        os.kill(os.getpid(), sig)
                            self.assertEqual(result.exception.code, 128 + sig)
                        self.assertEqual(len(made), 1)
                        self.assertFalse(made[0].exists())
                    finally:
                        for s, handler in previous.items():
                            signal.signal(s, handler)

    def test_return_codes_and_spawn_failure(self):
        self.assertEqual(launcher.run([sys.executable, '-c', 'raise SystemExit(7)'], dict(os.environ)), 7)
        with self.assertRaises(subprocess.CalledProcessError) as result:
            installer.run_child([sys.executable, '-c', 'raise SystemExit(9)'])
        self.assertEqual(result.exception.returncode, 9)
        with self.assertRaises(FileNotFoundError):
            runtime.run_owned(['/nonexistent/taffish-test-command'])

    def test_term_resistant_child(self):
        real_popen = subprocess.Popen
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / 'ready'
            children = []
            def spawn(*args, **kwargs):
                child = real_popen(*args, **kwargs)
                children.append(child)
                deadline = time.monotonic() + 10
                while not marker.exists():
                    self.assertLess(time.monotonic(), deadline)
                    time.sleep(.02)
                os.kill(os.getpid(), signal.SIGTERM)
                return child
            start = time.monotonic()
            with patch.object(subprocess, 'Popen', spawn), self.assertRaises(SystemExit) as result:
                runtime.run_owned([sys.executable, '-c', 'import signal,time,pathlib; signal.signal(signal.SIGTERM,signal.SIG_IGN); pathlib.Path('+repr(str(marker))+').touch(); time.sleep(30)'])
            self.assertEqual(result.exception.code, 143)
            self.assertEqual(children[0].returncode, -signal.SIGKILL)
            self.assertLess(time.monotonic() - start, 8)


unittest.main(verbosity=2)
