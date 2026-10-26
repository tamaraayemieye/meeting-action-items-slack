"""Slice 1 acceptance tests (no API calls required)."""

import unittest

from validation import MAX_TRANSCRIPT_CHARS, validate_transcript


class TranscriptValidationTests(unittest.TestCase):
    def test_empty_input_is_rejected(self):
        self.assertFalse(validate_transcript("")[0])

    def test_whitespace_input_is_rejected(self):
        self.assertFalse(validate_transcript(" \n\t ")[0])

    def test_real_transcript_is_accepted(self):
        self.assertTrue(validate_transcript("Alex: I will send the proposal.")[0])

    def test_at_character_limit_is_accepted(self):
        self.assertTrue(validate_transcript("x" * MAX_TRANSCRIPT_CHARS)[0])

    def test_over_character_limit_is_rejected(self):
        self.assertFalse(validate_transcript("x" * (MAX_TRANSCRIPT_CHARS + 1))[0])

    def test_non_string_is_rejected(self):
        self.assertFalse(validate_transcript(None)[0])


if __name__ == "__main__":
    unittest.main()
