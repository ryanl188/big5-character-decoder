# Big5 Character Decoder

Decode and encode Traditional Chinese text using the Big5 character encoding, with strict error handling and zero third-party dependencies.

```python
from big5_character_decoder import decode, encode, Big5DecodeError, Big5EncodeError

try:
    text = decode(b"\xa4\xa4\xa4\xe5")  # b'\xa4\xa4\xa4\xe5' is "中文" in Big5
    print(text)  # 中文
except Big5DecodeError as exc:
    print("bad bytes:", exc)

try:
    raw = encode("中文")
    print(raw)  # b'\xa4\xa4\xa4\xe5'
except Big5EncodeError as exc:
    print("unencodable:", exc)
```

## Why this exists

Python already understands Big5 through its built-in `codecs` module, so the
mapping table is not the problem. The problem is that the built-in API surfaces
generic `UnicodeDecodeError` / `UnicodeEncodeError` exceptions and offers a
suite of error-handling modes (`strict`, `replace`, `ignore`, …) that are easy
to reach for by accident. `replace` quietly turns invalid bytes into `?`, and
`ignore` silently drops them — both produce mojibake when the input is Chinese
text, where a single missing byte shifts the framing of everything that
follows.

This library pins the behaviour down: `decode` and `encode` always use strict
mode, and they raise `Big5DecodeError` / `Big5EncodeError` (both subclasses of
`ValueError`) so callers have one domain-specific exception to catch. The
underlying `Unicode*Error` is chained as `__cause__` for anyone who needs the
raw byte offsets.

## Edge cases you will hit

- **Invalid bytes.** A stray `0xFF` or a truncated lead byte (e.g. `b'\xa4'`
  with no trailing byte) raises `Big5DecodeError`. The library does not guess.
- **Unencodable characters.** Big5 covers Traditional Chinese plus ASCII and a
  small set of symbols. Emoji, Simplified Chinese, Korean, etc. are not
  representable and raise `Big5EncodeError`.
- **Bytearray and memoryview.** Both are accepted by `decode`; `bytes` is
  returned regardless.

## Exports

- `decode(data: bytes | bytearray | memoryview) -> str`
- `encode(text: str) -> bytes`
- `Big5DecodeError` (subclass of `ValueError`)
- `Big5EncodeError` (subclass of `ValueError`)
