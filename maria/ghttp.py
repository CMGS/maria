import re
import time
import os
import select
from os import access
from os.path import join, exists, getmtime, getsize
from urllib import unquote
from libs.git import Git


# Weekday and month names for HTTP date/time formatting; always English!
_weekdayname = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_monthname = [None, # Dummy so we can use 1-based month numbers
              "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def format_date_time(timestamp):
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    return "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
        _weekdayname[wd], day, _monthname[month], year, hh, mm, ss
    )


def callback(p):
    ofd = p.stdout.fileno()
    efd = p.stderr.fileno()
    while True:
        r_ready, w_ready, x_ready = select.select([ofd, efd], [], [], 30)

        if ofd in r_ready:
            data = os.read(ofd, 8192)
            if not data:
                break
            yield data

        if efd in r_ready:
            data = os.read(efd, 8192)
            yield data
            break

    output, err = p.communicate()
    if output:
        yield output
        if err:
            yield err


class GHTTPServer(object):

    VALID_SERVICE_TYPES = ['upload-pack', 'receive-pack']

    SERVICES = [
      ["POST", 'service_rpc',      re.compile("(.*?)/git-upload-pack$"),  'upload-pack'],
      ["POST", 'service_rpc',      re.compile("(.*?)/git-receive-pack$"), 'receive-pack'],

      ["GET",  'get_info_refs',    re.compile("(.*?)/info/refs$")],
      ["GET",  'get_text_file',    re.compile("(.*?)/HEAD$")],
      ["GET",  'get_text_file',    re.compile("(.*?)/objects/info/alternates$")],
      ["GET",  'get_text_file',    re.compile("(.*?)/objects/info/http-alternates$")],
      ["GET",  'get_info_packs',   re.compile("(.*?)/objects/info/packs$")],
      ["GET",  'get_text_file',    re.compile("(.*?)/objects/info/[^/]*$")],
      ["GET",  'get_loose_object', re.compile("(.*?)/objects/[0-9a-f]{2}/[0-9a-f]{38}$")],
      ["GET",  'get_pack_file',    re.compile("(.*?)/objects/pack/pack-[0-9a-f]{40}\\.pack$")],
      ["GET",  'get_idx_file',     re.compile("(.*?)/objects/pack/pack-[0-9a-f]{40}\\.idx$")],
    ]

    def __init__(self, config=None):
        self.headers = {}
        self.set_config(config)
        self.git = Git("/Users/xtao/gentoo/usr/bin/git")
        self.RE_SERVICES = []

    def set_config(self, config):
        self.config = config or {}

    def set_config_setting(self, key, value):
        self.config[key] = value

    def __call__(self, environ, start_response):
        self.env = environ
        body = self.call()
        start_response(self.status, self.headers.items())
        return body

    def call(self):
        match = self.match_routing(self.env["PATH_INFO"].lstrip('/'), self.env["REQUEST_METHOD"])
        if not match:
            return self.render_not_found()
        cmd, path, reqfile, rpc = match
        self.rpc = rpc
        self.reqfile = reqfile
        if cmd == "not_allowed":
            return self.render_method_not_allowed()
        self.dir = self.get_git_dir(path)
        if not self.dir:
            return self.render_not_found()
        func = getattr(self, cmd)
        return func()

    def service_rpc(self):
        if not self.has_access(self.rpc, True):
            return self.render_no_access()
        input = self.read_body
        git_cmd = "upload_pack" if self.rpc == "upload-pack" else "receive_pack"
        self.status = "200"
        self.headers["Content-Type"] = "application/x-git-%s-result" % self.rpc
        return getattr(self.git, git_cmd)(self.dir, {"msg": input}, callback)

    def get_info_refs(self):
        service_name = self.get_service_type()
        if self.has_access(service_name):
            git_cmd = "upload_pack" if service_name == "upload-pack" else "receive_pack"
            refs = getattr(self.git, git_cmd)(self.dir, {"advertise_refs": True})
            self.status = "200"
            self.headers["Content-Type"] = "application/x-git-%s-advertisement" % service_name
            self.hdr_nocache()
            def read_file():
                yield self.pkt_write("# service=git-%s\n" % service_name)
                yield self.pkt_flush
                yield refs
            return read_file()
        else:
            return self.dumb_info_refs()

    def get_text_file(self):
        return self.send_file(self.reqfile, "text/plain")

    def dumb_info_refs(self):
        self.update_server_info()
        return self.send_file(self.reqfile, "text/plain; charset=utf-8")

    def get_info_packs(self):
        # objects/info/packs
        return self.send_file(self.reqfile, "text/plain; charset=utf-8")

    def get_loose_object(self):
        return self.send_file(self.reqfile, "application/x-git-loose-object", cached=True)

    def get_pack_file(self):
        return self.send_file(self.reqfile, "application/x-git-packed-objects", cached=True)

    def get_idx_file(self):
        return self.send_file(self.reqfile, "application/x-git-packed-objects-toc", cached=True)

    def get_service_type(self):
        def get_param():
            for query in self.env["QUERY_STRING"].split('&'):
                param = tuple(query.split('='))
                if param and param[0] == "service":
                    return param[1]
        service_type = get_param()
        if not service_type:
            return False
        if service_type[0:4] != 'git-':
            return False
        return service_type.replace('git-', '')

    @classmethod
    def match_routing(cls, path_info, request_method):
        for service in cls.SERVICES:
            rpc = None
            if len(service) == 4:
                method, handler, re_match, rpc = service
            elif len(service) == 3:
                method, handler, re_match = service
            m = re_match.match(path_info)
            if m:
                if method != request_method:
                    return ["not_allowed", None, None, None]
                cmd = handler
                path = m.group(1)
                file = path_info.replace(path + '/', '')
                return [cmd, path, file, rpc]
        return None


    def send_file(self, reqfile, content_type, cached=False):
        reqfile = join(self.dir, reqfile)
        if not self.is_subpath(reqfile, self.dir):
            return self.render_no_access()
        if not exists(reqfile) or not access(reqfile, os.R_OK):
            return self.render_not_found()

        self.status = "200"
        self.headers["Content-Type"] = content_type
        self.headers["Last-Modified"] = format_date_time(getmtime(reqfile))

        if cached:
            self.hdr_cache_forenver()
        else:
            self.hdr_nocache()

        size = getsize(reqfile)
        if size:
            self.headers["Content-Length"] = size
            def read_file():
                with open(reqfile, "rb") as f:
                    while True:
                        part = f.read(8192)
                        if not part:
                            break
                        yield part
            return read_file()
        else:
            with open(reqfile, "rb") as f:
                part = f.read()
                self.headers["Content-Length"] = str(len(part))
            return [part]


    def update_server_info(self):
        self.git.update_server_info(self.dir)

    @property
    def read_body(self):
        input = self.env["wsgi.input"]
        return input.read()

    # ------------------------------
    # packet-line handling functions
    # ------------------------------

    @property
    def pkt_flush(self):
        return '0000'

    def pkt_write(self, str):
        # TODO: use zfill
        PKT_FORMAT = "{0:{fill}{align}{width}{base}}{1}"
        return PKT_FORMAT.format(len(str) + 4,
                                 str,
                                 base='x',
                                 width=4,
                                 fill='0',
                                 align='>')

    # ------------------------
    # header writing functions
    # ------------------------

    def hdr_nocache(self):
        self.headers["Expires"] = "Fri, 01 Jan 1980 00:00:00 GMT"
        self.headers["Pragma"] = "no-cache"
        self.headers["Cache-Control"] = "no-cache, max-age=0, must-revalidate"

    def hdr_cache_forenver(self):
        now = int(time.time())
        self.headers["Date"] = str(now)
        self.headers["Expires"] = str(now + 31536000)
        self.headers["Cache-Control"] = "public, max-age=31536000"

    # --------------------------------------
    # HTTP error response handling functions
    # --------------------------------------

    def render_method_not_allowed(self):
        env = []
        if env["SERVER_PROTOCOL"] == "HTTP/1.1":
            self.status = "405"
            self.headers["Content-Type"] = "text/plain"
            return ["Method Not Allowed"]
        else:
            self.status = "400"
            self.headers["Content-Type"] = "text/plain"
            return ["Bad Request"]

    def render_not_found(self):
        self.status = "404"
        self.headers["Content-Type"] = "text/plain"
        return ["Not Found"]

    def render_no_access(self):
        self.status = "403"
        self.headers["Content-Type"] = "text/plain"
        return ["Forbidden"]

    def has_access(self, rpc, check_content_type=False):
        if check_content_type:
            if self.env["CONTENT_TYPE"] != "application/x-git-%s-request" % rpc:
                return False
        if rpc not in self.VALID_SERVICE_TYPES:
            return False
        if rpc == 'receive-pack':
            if "receive_pack" in self.config:
                return self.config.get("receive_pack")
        if rpc == 'upload-pack':
            if "upload_pack" in self.config:
                return self.config.get("upload_pack")
        return self.get_config_setting(rpc)

    def get_config_setting(self, service_name):
      service_name = service_name.replace('-', '')
      setting = self.git.get_config_setting(self.dir, "http.%s" % service_name)
      if service_name == 'uploadpack':
        return setting != 'false'
      else:
        return setting == 'true'

    def get_git_dir(self, path):
        root = self.get_project_root()
        path = join(root, path)
        if not self.is_subpath(path, root):
            return False
        if exists(path): # TODO: check is a valid git directory
            return path
        return False

    def get_project_root(self):
        root = self.config.get("project_root") or os.getcwd()
        return root

    def is_subpath(self, path, checkpath):
        path = unquote(path)
        checkpath = unquote(checkpath)
        # Remove trailing slashes from filepath
        checkpath = checkpath.replace("\/+$",'')
        if re.match("^%s(\/|$)" % checkpath, path):
           return True
