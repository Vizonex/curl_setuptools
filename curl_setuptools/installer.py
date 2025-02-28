"""
Assists in installing sperate libraries from github 
without additional dependencies, except for urllib3
"""

import io
import logging
import random
import re
import typing
from dataclasses import dataclass
from functools import cache
import os
from pathlib import Path
import tarfile
from typing import cast



import certifi

try:
    from tqdm import tqdm
    USE_PROGRESS_BAR = True
except ModuleNotFoundError:
    USE_PROGRESS_BAR = False

import urllib3





# Inspired by pyppeteer's chromium downloader

# From pyppeteer chromium downloader
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(fmt=logging.Formatter(fmt="[{levelname}] {msg}", style="{"))
handler.setLevel(logging.INFO)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/116.0.0.",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.",
    "Mozilla/5.0 (Windows NT 6.1; rv:109.0) Gecko/20100101 Firefox/115.",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 OPR/95.0.0.",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.",
]

def random_ua():
    return random.choice(USER_AGENTS)



def download_file(url:str):
    logger.info(f"starting download of {url}")
    with urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()) as http:
        # Urllib3 lacks typehinting in older versions...
        # Some sites we download from are unfriendly so obfuscating the user-agent is a must
        resp = cast(urllib3.HTTPResponse, http.request("GET", url, preload_content=False, headers={"User-Agent": random_ua()}))
        if resp.status >= 400:
            raise OSError(f"Could not download from {url}: Received \"{resp.data.decode()}\".\n")
        
        _data = io.BytesIO()
        if not USE_PROGRESS_BAR:
            for chunk in resp.stream(10240):
                _data.write(chunk)
        else:
            try:
                total_length = int(resp.headers['content-length'])
            except (KeyError, ValueError, AttributeError):
                total_length = 0
            with tqdm(total=total_length, unit_scale=True, unit='b') as progress_bar:
                for chunk in resp.stream(10240):
                    _data.write(chunk)
                    progress_bar.update(len(chunk))
    
    return _data


def download_as_gzip(path:Path, url:str, temporary_gz_file:str, name:str, remove_after_download:bool = True):
    b_io = download_file(url)

    with open(path / temporary_gz_file, "wb") as gzip_file:
        gzip_file.write(b_io.getvalue())

    logger.info(f"extracing {temporary_gz_file}")    
    with tarfile.open(path / temporary_gz_file, 'r:gz') as tar:
        if not USE_PROGRESS_BAR:
            tar.extractall(path / name) 
        else:
            # SEE: https://stackoverflow.com/a/53405055
            for member in tqdm(iterable=tar.getmembers(), total=len(tar.getmembers())):
                tar.extract(member=member, path=path / name)
    
    if remove_after_download:
        logger.info(f"Removing {temporary_gz_file}")
        os.remove(path / temporary_gz_file)
    
    return path / name
    

def download_curl(path:Path, version:str, name:str = ".curl-temp", remove_after_download:bool=True) -> Path:
    """Downloads curl-{version} to the root path chosen""" 
    return download_as_gzip(path, 
            f"https://curl.se/download/curl-{version}.tar.gz",
            f"__curl-{version}.tar.gz",
            name, 
            remove_after_download
    ) / f"curl-{version}"
  
    
    


def download_nghttp2(path:Path, version:str, name:str = ".nghttp2-temp", remove_gz_after_download:bool=True):
    return download_as_gzip(
        path,
        f"https://github.com/nghttp2/nghttp2/releases/download/v1.64.0/nghttp2-{version}.tar.gz",
        f"__nghttp2-{version}.tar.gz",
        name, 
        remove_gz_after_download
    )