"""Core Big5 decoding and encoding logic.

Python ships with a Big5 codec in the standard library. We use it rather than
re-implementing the 13,000+ code-point mapping table by hand — the codec is
well tested and authoritative. What this module adds is a deliberately small,
surface: explicit error types and functions whose return types make success
versus failure unmistakable, instead of relying on callers to catch the right
broad exception from the builtin codecs module.

The Big5 codec bundled with CPython is used directly. Not every Python build
includes every codec, but Big5 is part of the mandatory large-codec set shipped
on all tier-1 platforms, so we do not try to fall back to a hand-rolled table.
If the codec is genuinely unavailable the constructor-style import at the top
would raise; instead we look it up lazily so that importing this module never
fails, and the error surfaces only if someone actually tries to (en|de)code.
"""

from __future__ import annotations

import codecs


class Big5DecodeError(ValueError):
    """Raised when a byte sequence is not valid Big5.

    Subclasses ValueError so existing `except ValueError` handlers keep
    working, while still letting callers catch Big5 failures specifically.
    """


class Big5EncodeError(ValueError):
    """Raised when a character has no Big5 representation.

    Big5 cannot represent the full Unicode range — it covers Traditional
    Chinese plus ASCII and a handful of symbols. Any character outside that
    set is genuinely unencodable, and we report it rather than silently
dropping it or substituting a question mark.
    """


def _big5_codec() -> codecs.CodecInfo:
    """Return CPython's bundled Big5 codec info, looking it up lazily.

    Looking up lazily means importing this module never fails on a build that,
    for some reason, lacks the codec; the failure is deferred to actual use,
    which is where a user can do something about it.
    """
    info = codecs.lookup("big5")
    return info


def decode(data: bytes) -> str:
    """Decode Big5-encoded bytes into a Python `str`.

    Args:
        data: Raw bytes in Big5 encoding.

    Returns:
        The decoded Unicode string.

    Raises:
        Big5DecodeError: If *data* contains bytes that are not a valid Big5
            sequence. We translate the builtin `UnicodeDecodeError` into our
            own type so callers get a single, domain-specific exception to
            catch; the original error is preserved as ``__cause__``.
        TypeError: If *data* is not bytes-like.

    The builtin codec uses ``strict`` error handling, so the first invalid
    byte stops decoding. We keep that behaviour because silently skipping or
    replacing bad bytes in Chinese text tends to produce mojibake that is
    worse than a loud failure.
    """
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError(
            f"decode() expects bytes-like input, got {type(data).__name__}"
        )
    try:
        return _big5_codec().decode(bytes(data), "strict")[0]
    except UnicodeDecodeError as exc:
        raise Big5DecodeError(
            f"invalid Big5 byte sequence at offset {exc.start}: "
            f"{bytes(data[exc.start:exc.end]).hex()}"
        ) from exc


def encode(text: str) -> bytes:
    """Encode a Python `str` into Big5 bytes.

    Args:
        text: The Unicode string to encode.

    Returns:
        The Big5-encoded bytes.

    Raises:
        Big5EncodeError: If *text* contains a character that Big5 cannot
            represent. The builtin `UnicodeEncodeError` is translated so
            callers have one domain-specific exception to handle; the original
            error is preserved as ``__cause__``.
        TypeError: If *text* is not a `str`.

    Strict error handling is used on purpose. Big5 has no generic fallback
    character, and substituting ``b'?'`` for an unencodable Chinese character
    would silently corrupt data.
    """
    if not isinstance(text, str):
        raise TypeError(
            f"encode() expects str input, got {type(text).__name__}"
        )
    try:
        return _big5_codec().encode(text, "strict")[0]
    except UnicodeEncodeError as exc:
        raise Big5EncodeError(
            f"character at index {exc.start} has no Big5 representation: "
            f"{text[exc.start:exc.end]!r} (U+{ord(text[exc.start]):04X})"
        ) from exc
