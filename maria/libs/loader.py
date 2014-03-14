#!/usr/bin/python
#coding:utf-8

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

def load_class(uri, default="GSSHServer", section="maria.gssh"):
    if inspect.isclass(uri):
        return uri
    if uri.startswith("egg:"):
        # uses entry points
        entry_str = uri.split("egg:")[1]
        try:
            dist, name = entry_str.rsplit("#", 1)
        except ValueError:
            dist = entry_str
            name = default

        try:
            return pkg_resources.load_entry_point(dist, section, name)
        except:
            exc = traceback.format_exc()
            raise RuntimeError("class uri %r invalid "
                               "or not found: \n\n[%s]" % (uri,
                                                           exc))
    elif uri.startswith("file:"):
        path, klass = uri.split('file:')[1].rsplit('#')
        path = os.path.realpath(path)
        module = path.rsplit('/',1)[-1].strip('.py')
        mod = imp.load_source('%s.%s' % (module, klass), path)
        return getattr(mod, klass)
    else:
        components = uri.split('.')
        if len(components) == 1:
            try:
                if uri.startswith("#"):
                    uri = uri[1:]

                return pkg_resources.load_entry_point("maria",
                                                      section, uri)
            except:
                exc = traceback.format_exc()
                raise RuntimeError("class uri %r invalid "
                                   "or not found: \n\n[%s]" % (uri,
                                                               exc))

        klass = components.pop(-1)
        try:
            mod = import_module('.'.join(components))
        except:
            exc = traceback.format_exc()
            raise RuntimeError("class uri %r invalid "
                               "or not found: \n\n[%s]" % (uri,
                                                           exc))

        return getattr(mod, klass)
