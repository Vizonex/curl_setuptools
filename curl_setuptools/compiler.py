"""
compiler
----------------

Provides OS support for compiling libcurl statically

"""

import logging
from pathlib import Path
from typing import Optional

from setuptools import Extension
from setuptools.command.build_ext import build_ext
from .installer import download_curl, download_nghttp2

from enum import IntFlag, auto

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(fmt=logging.Formatter(fmt="[{levelname}] {msg}", style="{"))
handler.setLevel(logging.INFO)
logger.setLevel(logging.INFO)
logger.addHandler(handler)




class InstallFlags(IntFlag):
    NONE = 0
    NTLM = 0b1
    HTTP2 = 0b10
    SPNEGO = 0b100
    


class WindowsCurlInstaller:
    """Used for installing and finding curl"""
    
    curl_path:Optional[Path]
    nghttp2_path:Optional[Path]

    curl_version:str
    def __init__(self, root:Path, curl_version:str = "", nghttp2_version:str = "1.64.0"):
        self.curl_version = curl_version
        self.nghttp2_version = nghttp2_version
        self._root = root
        self.curl_path = None
        self.nghttp2_path = None

    def install(self):
        """Installs and downloads curl source files using `urllib3` if `curl_path` was not previously set"""
        if not self.curl_path:
            self.curl_path = download_curl(self._root, self.curl_version)
    
    def install_nghttp2(self):
        """Optional install that is executed when InstallFlags HTTP2 is set"""
        if not self.nghttp2_path:
            self.nghttp2_path = download_nghttp2(self._root, self.nghttp2_version)

    def create_compilation_list(self, ext:Extension, flags:InstallFlags):
        """Creates a compile list for a certain extension, this also runs the `install()` function"""
        self.install()

        

        

        # SEE: rust's curl-sys library for reference
        # URL: https://github.com/alexcrichton/curl-rust/blob/main/curl-sys/build.rs

        # NOTE: For anyone who doesn't understand how including curl works be sure
        # To write it as #include <curl/curl.h>
        # NOT: <curl.h> , <include/curl/curl.h>, etc...
        # You will have errors if you do that. Believe me, I learned that the hard way.
        # And neither should you. - Vizonex

        # libpath will be used multiple times...
        LIB = self.curl_path / "lib"

        ext.include_dirs.append(str(self.curl_path / "include"))
        ext.include_dirs.append(str(LIB))


        ext.sources += list(map(str, [
            (LIB / "asyn-thread.c"),
            (LIB / "altsvc.c"),
            (LIB / "base64.c"),
            (LIB / "bufq.c"),
            (LIB / "bufref.c"),
            (LIB / "cfilters.c"),
            (LIB / "cf-h1-proxy.c"),
            (LIB / "cf-haproxy.c"),
            (LIB / "cf-https-connect.c"),
            (LIB / "cf-socket.c"),
            (LIB / "conncache.c"),
            (LIB / "connect.c"),
            (LIB / "content_encoding.c"),
            (LIB / "cookie.c"),
            (LIB / "curl_addrinfo.c"),
            (LIB / "curl_get_line.c"),
            (LIB / "curl_memrchr.c"),
            (LIB / "curl_range.c"),
            (LIB / "curl_sha512_256.c"),
            (LIB / "curl_threads.c"),
            (LIB / "curl_trc.c"),
            (LIB / "cw-out.c"),
            (LIB / "doh.c"),
            (LIB / "dynbuf.c"),
            (LIB / "dynhds.c"),
            (LIB / "easy.c"),
            (LIB / "escape.c"),
            (LIB / "file.c"),
            (LIB / "fileinfo.c"),
            (LIB / "fopen.c"),
            (LIB / "formdata.c"),
            (LIB / "getenv.c"),
            (LIB / "getinfo.c"),
            (LIB / "hash.c"),
            (LIB / "headers.c"),
            (LIB / "hmac.c"),
            (LIB / "hostasyn.c"),
            (LIB / "hostip.c"),
            (LIB / "hostip6.c"),
            (LIB / "hsts.c"),
            (LIB / "http.c"),
            (LIB / "http1.c"),
            (LIB / "http_aws_sigv4.c"),
            (LIB / "http_chunks.c"),
            (LIB / "http_digest.c"),
            (LIB / "http_proxy.c"),
            (LIB / "idn.c"),
            (LIB / "if2ip.c"),
            (LIB / "inet_ntop.c"),
            (LIB / "inet_pton.c"),
            (LIB / "llist.c"),
            (LIB / "md5.c"),
            (LIB / "mime.c"),
            (LIB / "macos.c"),
            (LIB / "mprintf.c"),
            (LIB / "mqtt.c"),
            (LIB / "multi.c"),
            (LIB / "netrc.c"),
            (LIB / "nonblock.c"),
            (LIB / "noproxy.c"),
            (LIB / "parsedate.c"),
            (LIB / "progress.c"),
            (LIB / "rand.c"),
            (LIB / "rename.c"),
            (LIB / "request.c"),
            (LIB / "select.c"),
            (LIB / "sendf.c"),
            (LIB / "setopt.c"),
            (LIB / "sha256.c"),
            (LIB / "share.c"),
            (LIB / "slist.c"),
            (LIB / "socks.c"),
            (LIB / "socketpair.c"),
            (LIB / "speedcheck.c"),
            (LIB / "splay.c"),
            (LIB / "strcase.c"),
            (LIB / "strdup.c"),
            (LIB / "strerror.c"),
            (LIB / "strparse.c"),
            (LIB / "strtok.c"),
            (LIB / "strtoofft.c"),
            (LIB / "timeval.c"),
            (LIB / "transfer.c"),
            (LIB / "url.c"),
            (LIB / "urlapi.c"),
            (LIB / "version.c"),
            (LIB / "vauth/digest.c"),
            (LIB / "vauth/vauth.c"),
            (LIB / "vquic/curl_msh3.c"),
            (LIB / "vquic/curl_ngtcp2.c"),
            (LIB / "vquic/curl_osslq.c"),
            (LIB / "vquic/curl_quiche.c"),
            (LIB / "vquic/vquic.c"),
            (LIB / "vquic/vquic-tls.c"),
            (LIB / "vtls/hostcheck.c"),
            (LIB / "vtls/keylog.c"),
            (LIB / "vtls/vtls.c"),
            (LIB / "vtls/vtls_scache.c"),
            (LIB / "warnless.c"),
            (LIB / "timediff.c"),
            (LIB / "ws.c")
        ]))

        if flags & InstallFlags.NTLM:
            ext.sources.apped(str(LIB / "curl_des.c"))
            ext.sources.apped(str(LIB / "curl_endian.c"))
            ext.sources.apped(str(LIB / "curl_gethostname.c"))
            ext.sources.apped(str(LIB / "curl_ntlm_core.c"))
            ext.sources.apped(str(LIB / "http_ntlm.c"))
            ext.sources.apped(str(LIB / "md4.c"))
            ext.sources.apped(str(LIB / "vauth/ntlm.c"))
            ext.sources.apped(str(LIB / "vauth/ntlm_sspi.c"))
        else:
            ext.define_macros.append(
                ('CURL_DISABLE_NTLM', None)
            )
        
        if flags & InstallFlags.HTTP2:
            self.install_nghttp2()
            
        
        if flags & InstallFlags.SPNEGO:
            ext.sources.extend([str(LIB / "http_negotiate.c"), str(LIB / "vauth" / "vauth.c")])
            ext.define_macros.append(("USE_SPNEGO", None))
        






