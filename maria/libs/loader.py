#!/usr/local/bin/python2.7
#coding:utf-8

import inspect
import traceback
import pkg_resources

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
            raise RuntimeError("class uri %r invalid or not found: \n\n[%s]" % (uri,
                exc))
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
                raise RuntimeError("class uri %r invalid or not found: \n\n[%s]" % (uri,
                    exc))

        klass = components.pop(-1)
        try:
            mod = __import__('.'.join(components))
        except:
            exc = traceback.format_exc()
            raise RuntimeError("class uri %r invalid or not found: \n\n[%s]" % (uri,
                exc))

        for comp in components[1:]:
            mod = getattr(mod, comp)
        return getattr(mod, klass)

