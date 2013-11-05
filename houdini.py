import logging
import os
import re
import sys
import time
from inspect import isfunction, getmodule, getsourcefile, getsourcelines


def hotswap(f):
    """
    Enable hotswapping for a function or method.

    The provided function must either be a top level function, or it must
    be a method belonging to a class at top level.
    """
    if not isfunction(f):
        raise HotswapException('@hotswap is not supported for %s' % str(f))

    mod, f_file, f_lines = _resolve_fn(f)
    hotswap_path = _find_hotswap_path(f, f_file, f_lines)

    def proxy(*nkw, **kw):
        should_reload = os.path.getmtime(f_file) >= mod._last_load_time
        if should_reload:
            reload(mod)
        latest_f = _find_latest_f(mod, hotswap_path)
        return latest_f(*nkw, **kw)

    proxy._latest_f = f
    mod._last_load_time = time.time()

    return proxy


class HotswapException(Exception):
    pass


def _resolve_fn(f):
    return getmodule(f), getsourcefile(f), getsourcelines(f)


def _find_latest_f(mod, hotswap_path):
    x = mod
    for n in hotswap_path:
        x = getattr(x, n)
    return x._latest_f


def _find_hotswap_path(f, f_file, f_lines):
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
            m = _CLASS_NAME_RE.match(lines[i])
            if m:
                return m.group(1)

    raise HotswapException('could not find class before (assumed) method '
                           'at line %d in file %s' % (before_line, file_name,))


_CLASS_NAME_RE = re.compile(r'^class\s+([^\(:]+).*$')
