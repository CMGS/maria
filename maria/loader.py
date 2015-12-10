# -*- coding: utf-8 -*-

import os
import sys
import imp
import inspect
import traceback
import pkg_resources

try:
    from importlib import import_module
except ImportError:
    def _resolve_name(name, package, level):
        """Return the absolute name of the module to be imported."""
        if not hasattr(package, 'rindex'):
            raise ValueError("'package' not set to a string")
        dot = len(package)
        for x in range(level, 1, -1):
            try:
                dot = package.rindex('.', 0, dot)
            except ValueError:
                raise ValueError("attempted relative import beyond top-level "
                                  "package")
        return "%s.%s" % (package[:dot], name)

    def import_module(name, package=None):
        """Import a module.

The 'package' argument is required when performing a relative import. It
specifies the package to use as the anchor point from which to resolve the
relative import to an absolute import.

"""
        if name.startswith('.'):
            if not package:
                raise TypeError("relative imports require the 'package' argument")
            level = 0
            for character in name:
                if character != '.':
                    break
                level += 1
            name = _resolve_name(name[level:], package, level)
        __import__(name)
        return sys.modules[name]

def load(uri):
    parts = uri.split(":", 1) #str.split([sep[, maxsplit]])
    if len(parts) == 1:
        return load_class(parts[0])
    elif len(parts) == 2:
        module, obj = parts[0], parts[1]
        return load_app(module, obj)
    else:
        raise Exception("load error: uri is invalid")

def load_class(uri, default="maria.worker.socket.SocketServer"):
    if inspect.isclass(uri):
        return uri
    else:
        components = uri.split('.')
        klass = components.pop(-1)
        try:
            mod = import_module('.'.join(components))
        except:
            exc = traceback.format_exc()
            raise RuntimeError("class uri %r invalid "
                               "or not found: \n\n[%s]" % (uri,
                                                           exc))

        return getattr(mod, klass)
    
def load_app(module, obj):
    sys.path.insert(0, os.getcwd())
    try: 
        __import__(module)
    except:
        raise ImportError("Failed to import application")

    mod = sys.modules[module]

    try:
        app = eval(obj, mod.__dict__)
    except NameError:
        raise Exception("Failed to find application: %r" % module)

    if app is None:
        raise Exception("Failed to find application object: %r" % obj)

    if not callable(app):
        raise Exception("Application object must be callable.")
    return app
