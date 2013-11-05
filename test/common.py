import inspect
import math
import os
import shutil
import sys
import tempfile
import time


HOUDINI_PATH = os.path.join(os.path.dirname(__file__), os.pardir,
                            'houdini.py')


class TestCase(object):
    def __init__(self):
        self._testdir = tempfile.mkdtemp()

    def run(self):
        sys.path.append(self._testdir)
        shutil.copy2(HOUDINI_PATH, self._testdir_join(['houdini.py']))
        os.chdir(self._testdir)
        self._run()
        print

    def check(self, f):
        if f():
            sys.stdout.write(':-) ')
            sys.stdout.flush()
        else:
            print '$$$ FAILURE $$$'
            print '$$$ FAILURE $$$'
            print '$$$ FAILURE $$$'
            raise Exception('test %s failed!' % str(f))

    def create_module(self, name, src):
        return TestPyModule(self, name, src)

    def _testdir_join(self, names):
        return os.path.join(*([self._testdir] + names))


class TestPyModule(object):
    def __init__(self, test_case, name, src):
        self._testdir_join = test_case._testdir_join
        self._name_segs = name.split('.')
        self._mod_name = self._testdir_join(self._name_segs) + '.py'

        self._create_dirs()
        self._write_src(src)

    def _create_dirs(self):
        for i in range(1, len(self._name_segs)):
            dir_name = self._testdir_join(self._name_segs[:i])
            os.mkdir(dir_name)
            init_name = os.path.join(dir_name, '__init__.py')
            with open(init_name, 'w') as f:
                f.write('# hmm?')

    def _write_src(self, src):
        with open(self._mod_name, 'w') as f:
            src_lines = [x for x in src.split('\n') if x.strip() != '']
            indent = min(len(x) - len(x.lstrip()) for x in src_lines)
            src_lines_just = [x[indent:] for x in src_lines]
            src_just = '\n'.join(src_lines_just)
            f.write(src_just)

    def edit(self, edit_fn):
        mtime = lambda: math.floor(os.path.getmtime(self._mod_name))
        mtime_pre = mtime()

        with open(self._mod_name, 'r') as f:
            old_data = f.read()

        while mtime() == mtime_pre:
            self._write_src(edit_fn(old_data))
            time.sleep(0.1)


def verbatim_sub(p, r):
    def inner(s):
        ss = s.replace(p, r)
        return ss
    return inner
