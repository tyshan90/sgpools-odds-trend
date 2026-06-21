import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from sgpools_trend.config import Settings, load_env_file


class ConfigTests(unittest.TestCase):
    def test_settings_accepts_lowercase_linkup_alias(self):
        settings = Settings.from_mapping(
            {
                "linkup": "link-key",
                "TELEGRAM_BOT_TOKEN": "tg-token",
                "DATABASE_PATH": "custom.sqlite",
            }
        )

        self.assertEqual(settings.linkup_api_key, "link-key")
        self.assertEqual(settings.telegram_bot_token, "tg-token")
        self.assertEqual(settings.database_path, Path("custom.sqlite"))

    def test_settings_prefers_standard_linkup_api_key(self):
        settings = Settings.from_mapping(
            {
                "LINKUP_API_KEY": "standard-key",
                "linkup": "lower-key",
            }
        )

        self.assertEqual(settings.linkup_api_key, "standard-key")

    def test_load_env_file_parses_simple_dotenv_without_exporting_secrets(self):
        with TemporaryDirectory() as tmp_dir:
            env_path = Path(tmp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "linkup=link-key",
                        'TELEGRAM_BOT_TOKEN="tg-token"',
                        "IGNORED_LINE",
                    ]
                ),
                encoding="utf-8",
            )

            values = load_env_file(env_path)

        self.assertEqual(values["linkup"], "link-key")
        self.assertEqual(values["TELEGRAM_BOT_TOKEN"], "tg-token")
        self.assertNotIn("IGNORED_LINE", values)


if __name__ == "__main__":
    unittest.main()
