import os
import struct
import tempfile
import unittest

from .video_utils import moov_at_front


def box(typ, payload=b''):
    return struct.pack('>I', 8 + len(payload)) + typ + payload


def write_temp(data):
    fd, path = tempfile.mkstemp(suffix='.mp4')
    with os.fdopen(fd, 'wb') as f:
        f.write(data)
    return path


class MoovDetectorTest(unittest.TestCase):
    def test_moov_before_mdat_is_front(self):
        path = write_temp(box(b'ftyp', b'mmp42') + box(b'moov', b'x' * 100) + struct.pack('>I', 8) + b'mdat')
        try:
            self.assertTrue(moov_at_front(path))
        finally:
            os.remove(path)

    def test_moov_after_mdat_is_not_front(self):
        path = write_temp(box(b'ftyp', b'mmp42') + struct.pack('>I', 8) + b'mdat' + box(b'moov', b'x' * 100))
        try:
            self.assertFalse(moov_at_front(path))
        finally:
            os.remove(path)

    def test_no_moov_returns_false(self):
        path = write_temp(box(b'ftyp', b'mmp42') + struct.pack('>I', 8) + b'mdat')
        try:
            self.assertFalse(moov_at_front(path))
        finally:
            os.remove(path)

    def test_missing_file_returns_false(self):
        self.assertFalse(moov_at_front('/nonexistent/video.mp4'))
