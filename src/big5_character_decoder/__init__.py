"""Big5 character decoder and encoder.

This package provides decoding and encoding for the Big5 Traditional Chinese
character encoding using only the Python standard library. Python's built-in
codecs already understand Big5; this library adds disciplined error handling
and a small, explicit API so callers can distinguish the byte errors that
matter (invalid sequences, unmapped code points) from ordinary success.
"""

from .core import (
    Big5DecodeError,
    Big5EncodeError,
    decode,
    encode,
)

__all__ = [
    "Big5DecodeError",
    "Big5EncodeError",
    "decode",
    "encode",
]
