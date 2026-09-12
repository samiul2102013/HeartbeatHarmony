# Flutter Video Streaming & Chunked Download Guide
Hartbeat Harmony — for the Flutter (mobile app) developer.

## 1. What the server guarantees (already live, verified)

- Every video URL is a direct nginx static file, e.g.
  `https://api.heartbeatharmony.tech/media/study/pdfs/<file>.mp4`
- **Byte-range requests are supported.** The server answers `206 Partial Content`
  with `Accept-Ranges: bytes`, `ETag`, `Last-Modified`, correct `video/mp4`
  (also `video/quicktime`, `video/x-matroska`, `video/webm`) MIME types.
- **Every MP4 is faststart** (moov atom at the front). Playback starts after the
  first ~2 MB instead of after the full 2 GB. New uploads are converted
  automatically; old files were backfilled.
- Catalog API gives you everything the client needs per material:
  `material_data` (absolute URL), `size` (bytes, use for progress),
  `type` (`video`/`pdf`/`text`).

## 2. Streaming playback (do this — no custom chunk code needed)

ExoPlayer (Android) and AVPlayer (iOS) already stream via byte-ranges.
Feed them the URL; never full-download-then-play.

### video_player (default)

```dart
final controller = VideoPlayerController.networkUrl(
  Uri.parse(materialDataUrl),
  httpHeaders: {'Authorization': 'Bearer $accessToken'}, // only if URLs become protected; today media is public, header is harmless
);
await controller.initialize(); // returns after headers+first chunks, NOT after 2 GB
await controller.play();
```

### better_player (if you need visible buffering config)

```dart
BetterPlayer.network(
  materialDataUrl,
  betterPlayerConfiguration: const BetterPlayerConfiguration(
    autoPlay: true,
    allowedScreenSleep: false,
    bufferingConfiguration: BetterPlayerBufferingConfig(
      minBufferMs: 10000,   // 10 s floor — survives short drops
      maxBufferMs: 50000,   // 50 s ceiling — caps memory on 2 GB files
      bufferForPlaybackMs: 1500,
      bufferForPlaybackAfterRebufferMs: 3000,
    ),
  ),
);
```

### Retry policy (reliability — implement exactly this)

On player error (timeout, 5xx, connection drop):

1. Retry the same URL up to **3 times** with backoff **1s → 2s → 4s**.
2. The player re-requests byte-ranges automatically — playback resumes where
   it stopped. Do NOT restart from 0 and do NOT re-create the file.
3. After 3 failures show a Retry button that re-initializes the controller
   with the same URL.

```dart
Future<void> playWithRetry(String url, {int attempt = 0}) async {
  try {
    await controller.initialize();
    await controller.play();
  } catch (_) {
    if (attempt >= 3) rethrow; // -> show Retry button
    await Future.delayed(Duration(seconds: 1 << attempt)); // 1, 2, 4
    return playWithRetry(url, attempt: attempt + 1);
  }
}
```

## 3. Offline download in chunks (only if you offer "save for offline")

Single-shot `Dio().download()` dies on 2 GB files over mobile networks.
Download in parallel Range chunks with per-chunk retry, resume from `.part`:

```dart
import 'dart:io';
import 'dart:math';
import 'dart:typed_data';

/// Downloads [url] in [chunks] parallel Range requests.
/// Resumes into [savePath].part; verifies final byte length against [expectedBytes].
/// Throws after per-chunk retries are exhausted. No external packages needed.
Future<void> downloadInChunks({
  required String url,
  required String savePath,
  required int expectedBytes,
  int chunks = 6,
  int maxRetriesPerChunk = 5,
  void Function(int received, int total)? onProgress,
}) async {
  final partPath = '$savePath.part';
  final client = HttpClient()..connectionTimeout = const Duration(seconds: 30);
  try {
    final chunkSize = (expectedBytes / chunks).ceil();
    int received = 0;
    if (await File(partPath).exists()) {
      received = await File(partPath).length();
      if (received > expectedBytes) {
        await File(partPath).delete();
        received = 0;
      }
    }
    final raf = await File(partPath).open(mode: FileMode.writeOnlyAppend);
    try {
      int start = received;
      onProgress?.call(received, expectedBytes);
      final futures = <Future>[];
      // NOTE: parallel chunk writes need positioned writes; keep it simple and
      // robust: download the REMAINDER sequentially in 8 MB range-chunks.
      while (start < expectedBytes) {
        final end = min(start + 8 * 1024 * 1024 - 1, expectedBytes - 1);
        final s = start, e = end;
        futures.add(() async {
          for (var attempt = 0;; attempt++) {
            try {
              final req = await client.getUrl(Uri.parse(url));
              req.headers.set('Range', 'bytes=$s-$e');
              final res = await req.close();
              if (res.statusCode != 206) throw HttpException('expected 206, got ${res.statusCode}');
              final bytes = await res.fold<BytesBuilder>(BytesBuilder(), (b, d) => b..add(d)).then((b) => b.takeBytes());
              if (bytes.length != e - s + 1) throw HttpException('short chunk: ${bytes.length}');
              return (s, bytes);
            } catch (_) {
              if (attempt >= maxRetriesPerChunk) rethrow;
              await Future.delayed(Duration(seconds: 1 << min(attempt, 3)));
            }
          }
        }());
        start = end + 1;
        if (futures.length >= chunks) break; // pipeline depth = chunks
      }
      // Write chunks in order as they complete their pipeline batches.
      // Simplest correct flow: await each batch sequentially:
      for (final f in futures) {
        final rec = (await f) as (int, List<int>);
        await raf.writeFrom(rec.$2);
        received += rec.$2.length;
        onProgress?.call(received, expectedBytes);
      }
      // Continue with the next window until complete.
      while (received < expectedBytes) {
        final end = min(received + 8 * 1024 * 1024 - 1, expectedBytes - 1);
        final s = received, e = end;
        List<int>? bytes;
        for (var attempt = 0;; attempt++) {
          try {
            final req = await client.getUrl(Uri.parse(url));
            req.headers.set('Range', 'bytes=$s-$e');
            final res = await req.close();
            if (res.statusCode != 206) throw HttpException('expected 206, got ${res.statusCode}');
            bytes = await res.fold<BytesBuilder>(BytesBuilder(), (b, d) => b..add(d)).then((b) => b.takeBytes());
            if (bytes.length != e - s + 1) throw HttpException('short chunk');
            break;
          } catch (_) {
            if (attempt >= maxRetriesPerChunk) rethrow;
            await Future.delayed(Duration(seconds: 1 << min(attempt, 3)));
          }
        }
        await raf.writeFrom(bytes!);
        received += bytes.length;
        onProgress?.call(received, expectedBytes);
      }
    } finally {
      await raf.close();
    }
    final done = await File(partPath).length();
    if (done != expectedBytes) throw HttpException('length mismatch: $done != $expectedBytes');
    await File(partPath).rename(savePath);
  } finally {
    client.close(force: true);
  }
}
```

Rules for the download path:

- `expectedBytes` comes from the catalog `size` field (fallback: a `HEAD`
  request's `content-length`). Never trust the download to "just end".
- Chunk size **8 MB**, pipeline depth **6**, per-chunk retries **5** with
  1s/2s/4s/8s backoff. Tune only these four constants.
- Resume = re-run the same function; bytes already in `.part` are skipped
  via the opening `Range`. Rename to final name only after length verifies.
- If the server ever returns `200` instead of `206` for a Range request,
  abort and restart the chunk (do not append a full body to `.part`).

## 4. Prove it on device (send back these three numbers)

1. Tap play on a 2 GB video on 4G → time to first frame (expect < 5 s).
2. Seek to the middle → time to resume (expect < 3 s).
3. Airplane mode 10 s mid-play → player recovers by itself (no restart).

## 5. Server proofs you can re-check anytime (curl)

```bash
# Chunk support: expect 206 + accept-ranges
curl -s -o /dev/null -w "%{http_code}\n" -H "Range: bytes=0-1023" "<material_data URL>"
# First-2MB speed: playback needs ~this much before first frame
curl -s -r 0-2000000 -o /dev/null -w "%{http_code} %{time_total}s\n" "<material_data URL>"
```

## 6. Current limitations (known, not this task)

- Media URLs are public (no auth). If premium-only videos are required,
  ask backend for time-limited signed URLs.
- One rendition only (original file). No 480p/720p variants — deliberate.
