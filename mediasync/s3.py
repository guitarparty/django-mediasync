from boto.s3.connection import S3Connection
from boto.s3.key import Key
from django.conf import settings
from mediasync.utils import compress, cssmin, jsmin
import base64
import cStringIO
import datetime
import gzip
import hashlib

TYPES_TO_COMPRESS = (
    "application/javascript",
    "application/x-javascript",
    "application/xml",
    "text/css",
    "text/html",
    "text/plain",
)

EXPIRATION_DAYS = getattr(settings, "MEDIASYNC_EXPIRATION_DAYS", 365)

class Client(object):
    
    def __init__(self, key, secret, bucket_name, prefix=''):
        self._conn = S3Connection(key, secret)
        self._bucket = self._conn.create_bucket(bucket_name)
        self._prefix = prefix
                
        self._entries = { }
        for entry in self._bucket.list(self._prefix):
            self._entries[entry.key] = entry.etag.strip('"')
    
    def put(self, filedata, content_type, remote_path, force=False):
        
        now = datetime.datetime.utcnow()
        then = now + datetime.timedelta(EXPIRATION_DAYS)
        expires = then.strftime("%a, %d %b %Y %H:%M:%S UTC")
        
        # check to see if cssmin or jsmin should be run
        if content_type == "text/css":
            filedata = cssmin.cssmin(filedata)
        elif content_type == "text/javascript":    
            filedata = jsmin.jsmin(filedata)
        
        # create initial set of headers
        headers = {
            "x-amz-acl": "public-read",
            "Content-Type": content_type,
            "Expires": expires,
        }
        
        # check to see if file should be gzipped based on content_type
        if content_type in TYPES_TO_COMPRESS:
            filedata = compress(filedata)
            headers["Content-Encoding"] = "gzip"  
        
        # calculate md5 digest of filedata
        checksum = hashlib.md5(filedata)
        hexdigest = checksum.hexdigest()
        b64digest = base64.b64encode(checksum.digest())

        # check to see if local file has changed from what is on S3
        etag = self._entries.get(remote_path, '')
        if force or etag != hexdigest:
        
            # upload file
            key = Key(self._bucket)
            key.key = remote_path
            key.set_contents_from_string(filedata, headers=headers, md5=(hexdigest, b64digest))
        
            self._entries[remote_path] = etag

            return True
        