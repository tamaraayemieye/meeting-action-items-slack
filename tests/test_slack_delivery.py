"""Slack formatting and delivery tests; all network calls mocked."""
import io
import os
import unittest
from unittest.mock import patch

from slack_delivery import SlackDeliveryError, format_recap, post_to_slack


class SlackTests(unittest.TestCase):
    def setUp(self):
        self.items = [{"task": "Send proposal", "owner": "Alex", "due_date": "Friday"}]

    def test_recap(self):
        text = format_recap(self.items)
        self.assertIn("Alex", text)
        self.assertIn("Friday", text)

    def test_empty_recap_rejected(self):
        with self.assertRaises(SlackDeliveryError):
            format_recap([])

    def test_escaping(self):
        self.assertIn("&lt;!channel&gt;", format_recap([{"task": "<!channel>", "owner": "A", "due_date": ""}]))

    def test_missing_webhook(self):
        with patch.dict(os.environ, {"SLACK_WEBHOOK_URL": ""}):
            with self.assertRaises(SlackDeliveryError):
                post_to_slack(self.items)

    def test_wrong_webhook_host(self):
        with patch.dict(os.environ, {"SLACK_WEBHOOK_URL": "https://example.com/webhook"}):
            with self.assertRaises(SlackDeliveryError):
                post_to_slack(self.items)

    def test_successful_post_mocked(self):
        response = io.BytesIO(b"ok")
        response.status = 200
        with patch.dict(os.environ, {"SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/fake"}):
            with patch("slack_delivery.request.urlopen", return_value=response) as mocked:
                post_to_slack(self.items)
        self.assertTrue(mocked.called)

    def test_unconfirmed_post_is_error(self):
        response = io.BytesIO(b"invalid_payload")
        response.status = 200
        with patch.dict(os.environ, {"SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/fake"}):
            with patch("slack_delivery.request.urlopen", return_value=response):
                with self.assertRaises(SlackDeliveryError):
                    post_to_slack(self.items)


if __name__ == "__main__":
    unittest.main()
