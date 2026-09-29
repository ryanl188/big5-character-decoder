import unittest

from big5_character_decoder import (
    Big5DecodeError,
    Big5EncodeError,
    decode,
    encode,
)


class TestDecode(unittest.TestCase):
    def test_ascii_round_trips(self):
        # ASCII is a strict subset of Big5, so 7-bit bytes decode as themselves.
        self.assertEqual(decode(b"Hello, world!"), "Hello, world!")

    def test_empty_input(self):
        self.assertEqual(decode(b""), "")

    def test_traditional_chinese_decodes(self):
        # "\xa4\xa4" is the Big5 encoding of 中 (U+4E2D), a central
        # Traditional Chinese character. Round-tripping it through encode
        # confirms the bytes are genuinely Big5 and not just any bytes.
        original = encode("中文")
        self.assertEqual(decode(original), "中文")

    def test_bytearray_accepted(self):
        # decode() explicitly accepts bytearray; this guards against a regression
        # that would only accept bytes.
        self.assertEqual(decode(bytearray(b"abc")), "abc")

    def test_memoryview_accepted(self):
        self.assertEqual(decode(memoryview(b"abc")), "abc")

    def test_invalid_byte_raises_decode_error(self):
        # 0xFF is not a valid lead byte in Big5 and not a valid trailing byte
        # after a lead byte either; the codec rejects it outright.
        with self.assertRaises(Big5DecodeError) as ctx:
            decode(b"\xff")
        self.assertIn("offset 0", str(ctx.exception))
        self.assertIsInstance(ctx.exception.__cause__, UnicodeDecodeError)

    def test_truncated_lead_byte_raises(self):
        # 0xA4 is a valid lead byte (start of a two-byte Big5 character) but
        # here it has no trailing byte. The codec must reject this.
        with self.assertRaises(Big5DecodeError):
            decode(b"\xa4")

    def test_decode_error_is_value_error(self):
        # Big5DecodeError subclasses ValueError so broad handlers still catch it.
        try:
            decode(b"\xff")
        except ValueError:
            pass
        else:
            self.fail("Big5DecodeError did not behave as a ValueError")

    def test_non_bytes_input_raises_type_error(self):
        with self.assertRaises(TypeError):
            decode("not bytes")  # type: ignore[arg-type]


class TestEncode(unittest.TestCase):
    def test_ascii_encodes_as_itself(self):
        self.assertEqual(encode("Hello"), b"Hello")

    def test_empty_string(self):
        self.assertEqual(encode(""), b"")

    def test_traditional_chinese_encodes(self):
        # 中 (U+4E2D) encodes to the two-byte sequence A4 A4 in Big5.
        self.assertEqual(encode("中"), b"\xa4\xa4")

    def test_unencodable_character_raises(self):
        # \U0001F600 (😀) is far outside Big5's repertoire. Strict encoding
        # must reject it rather than substituting a fallback.
        with self.assertRaises(Big5EncodeError) as ctx:
            encode("a\U0001F600b")
        self.assertIn("index 1", str(ctx.exception))
        self.assertIsInstance(ctx.exception.__cause__, UnicodeEncodeError)

    def test_encode_error_is_value_error(self):
        try:
            encode("\U0001F600")
        except ValueError:
            pass
        else:
            self.fail("Big5EncodeError did not behave as a ValueError")

    def test_non_str_input_raises_type_error(self):
        with self.assertRaises(TypeError):
            encode(b"not a str")  # type: ignore[arg-type]


class TestRoundTrip(unittest.TestCase):
    def test_round_trip_preserves_text(self):
        sample = "中文測試繁體字"
        self.assertEqual(decode(encode(sample)), sample)

    def test_round_trip_mixed_ascii_and_chinese(self):
        sample = "Big5 是繁體中文編碼。"
        self.assertEqual(decode(encode(sample)), sample)


if __name__ == "__main__":
    unittest.main()
