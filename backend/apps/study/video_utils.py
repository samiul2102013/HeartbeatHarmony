"""MP4 faststart helpers. No Django imports — testable standalone."""
import logging
import os
import struct
import subprocess

log = logging.getLogger(__name__)
MAX_BOXES = 64


def moov_at_front(path):
    """True iff the top-level 'moov' box starts before the first 'mdat' box."""
    moov_off, mdat_off = None, None
    try:
        with open(path, 'rb') as f:
            for _ in range(MAX_BOXES):
                off = f.tell()
                header = f.read(8)
                if len(header) < 8:
                    break
                size, typ = struct.unpack('>I4s', header)
                if size == 1:
                    ext = f.read(8)
                    if len(ext) < 8:
                        break
                    size = struct.unpack('>Q', ext)[0]
                    header_len = 16
                elif size == 0:
                    break  # box runs to EOF; nothing after it can matter
                else:
                    header_len = 8
                if typ == b'moov':
                    moov_off = off
                elif typ == b'mdat' and mdat_off is None:
                    mdat_off = off
                if moov_off is not None and mdat_off is not None:
                    break
                f.seek(off + size if size >= header_len else off + header_len)
    except OSError:
        log.exception('moov probe failed for %s', path)
        return False
    if moov_off is None:
        return False
    if mdat_off is None:
        return True
    return moov_off < mdat_off


def run_faststart(src, dst, timeout=600):
    """Remux src -> dst with moov at front. Copy codec (no re-encode). Raises on failure."""
    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    tmp = dst + '.faststart.tmp'
    cmd = [exe, '-y', '-i', src, '-c', 'copy', '-movflags', '+faststart', tmp]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                   timeout=timeout, check=True)
    if not moov_at_front(tmp) or os.path.getsize(tmp) == 0:
        raise RuntimeError('faststart output failed verification')
    os.replace(tmp, dst)
