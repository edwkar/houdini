import os
import re
import sys
import time
from inspect import (isfunction, getmodule, getsourcefile, getsourcelines,)


def hotswap(f):
    if not isfunction(f):
        raise Exception('@hotswap is not supported for %s' % str(f))

    mod, f_file, f_lines = _lookup(f)

    def proxy(*nkw, **kw):
        should_reload = os.path.getmtime(f_file) > mod._last_load_time
        if should_reload:
            reload(mod)
        x = mod
        for n in f._hotswap_path:
            x = getattr(x, n)
        return x._wrapped(*nkw, **kw)

    f._hotswap_path = _build_hotswap_path(f, f_file, f_lines)
    proxy._wrapped = f

    mod._last_load_time = time.time()

    return proxy


def _lookup(f):
    return getmodule(f), getsourcefile(f), getsourcelines(f)


def _build_hotswap_path(f, f_file, f_lines):
    is_method = f_lines[0][0][0].isspace()
    if is_method:
        class_name = _find_last_class_name(f_file, f_lines[1])
        return (class_name, f.func_name,)
    else:
        return (f.func_name,)


def _find_last_class_name(file_name, before_line):
    with open(file_name) as f:
        lines = f.readlines()
        for i in range(before_line, -1, -1):
            m = _class_name_re.match(lines[i])
            if m:
                return m.group(1)

    raise Exception('could not find last class name before (assumed) method '
                    'at line %d in file %s' % (before_line, file_name,))


_class_name_re = re.compile(r'^class\s+([^\(:]+).*$')
