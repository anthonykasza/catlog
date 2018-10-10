import hashlib
import json
import re
import urllib.parse
import urllib.request
from typing import List, Tuple

from . import cert_encoding


def get_cert_ids_by_cn(common_name: str) -> List[str]:
    response_body = urllib.request.urlopen(
        "https://crt.sh/?{}".format(urllib.parse.urlencode({
            "CN": common_name,
            "output": "json"
        }))).read()
    decoder = json.JSONDecoder()
    ids = []
    while len(response_body) > 0:
        obj, n = decoder.raw_decode(response_body)
        ids.append(obj["min_cert_id"])
        response_body = response_body[n:]
    return ids


def get_leaf_hashes_by_cert_id(cert_id: str) -> List[Tuple[bytes, str]]:
    # Alas, crt.sh doesn't support JSON format for fetching full cert data. So let's do some HTML scraping...
    response_body = urllib.request.urlopen(
        "https://crt.sh/?{}".format(urllib.parse.urlencode({
            "id": cert_id
        }))).read().decode('utf-8')

    entry_ids = []
    for match in re.finditer(
            r'<TABLE class="options" style="margin-left:0px">\s*<TR>\s*<TH>Timestamp</TH>\s*<TH>Entry #</TH>\s*<TH>Log Operator</TH>\s*<TH>Log URL</TH>\s*</TR>\s*(.*?)\s*</TABLE>',
            response_body, re.DOTALL):
        rows = match.group(1)
        for row_match in re.finditer(
                "\s*<TR>\s*<TD>(.*?)</TD>\s*<TD>(.*?)</TD>\s*<TD>(.*?)</TD>\s*<TD>(.*?)</TD>\s*</TR>\s*", rows):
            ct_log_url = row_match.group(4)
            ct_log_entry_id = row_match.group(2)
            entry_ids.append((ct_log_url, ct_log_entry_id))

    # We could use the entry IDs directly, but there's a lot of code which operates on the basis of leaf hashes. So lookup
    # each entry and convert it back into a leaf hash
    leaf_hashes = []
    for entry_id in entry_ids:
        ct_log_url = entry_id[0]
        if not ct_log_url.endswith('/'):
            ct_log_url += '/'
        log_id = cert_encoding.lookup_ct_log_id_by_url(ct_log_url)
        if log_id is not None:
            leaf = cert_encoding.get_raw_leaf_by_entry_id(ct_log_url, entry_id[1])
            leaf_hash = hashlib.sha256(b"\x00" + leaf).digest()
            leaf_hashes.append((log_id, leaf_hash))

    return leaf_hashes