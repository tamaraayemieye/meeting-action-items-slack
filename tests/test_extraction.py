"""Unit tests for AI extraction; no real API calls or credentials."""
import io
import json
import os
import unittest
from unittest.mock import patch

from extraction import ExtractionError, extract_action_items, parse_action_items


class ExtractionTests(unittest.TestCase):
    def test_valid_items(self):
        raw = json.dumps({"action_items": [{"task": "Send proposal", "owner": "Alex", "due_date": "Friday"}]})
        self.assertEqual(parse_action_items(raw)[0]["owner"], "Alex")

    def test_missing_fields_default(self):
        items = parse_action_items('{"action_items":[{"task":"Send notes"}]}')
        self.assertEqual(items[0]["owner"], "Unassigned")
        self.assertEqual(items[0]["due_date"], "Not specified")

    def test_empty_result(self):
        self.assertEqual(parse_action_items('{"action_items":[]}'), [])

    def test_invalid_json(self):
        with self.assertRaises(ExtractionError):
            parse_action_items("not json")

    def test_missing_task(self):
        with self.assertRaises(ExtractionError):
            parse_action_items('{"action_items":[{"owner":"Alex"}]}')

    def test_wrong_shape(self):
        with self.assertRaises(ExtractionError):
            parse_action_items('{"tasks":[]}')

    def test_missing_credentials(self):
        with patch.dict(os.environ, {"AI_API_KEY": "", "AI_MODEL": ""}):
            with self.assertRaisesRegex(ExtractionError, "Configure"):
                extract_action_items("Test")

    def test_insecure_url(self):
        with patch.dict(os.environ, {"AI_API_KEY": "fake", "AI_MODEL": "fake", "AI_BASE_URL": "http://example.com/v1"}):
            with self.assertRaisesRegex(ExtractionError, "HTTPS"):
                extract_action_items("Test")

    def test_mocked_api_response(self):
        response = io.BytesIO(json.dumps({
            "choices": [{"message": {"content": '{"action_items":[{"task":"Review draft","owner":"Sam","due_date":"Monday"}]}'}}]
        }).encode())
        with patch.dict(os.environ, {"AI_API_KEY": "fake", "AI_MODEL": "fake", "AI_BASE_URL": "https://example.com/v1"}):
            with patch("extraction.request.urlopen", return_value=response) as mocked:
                items = extract_action_items("Sam will review the draft Monday.")
        self.assertEqual(items[0]["task"], "Review draft")
        self.assertTrue(mocked.called)


if __name__ == "__main__":
    unittest.main()
