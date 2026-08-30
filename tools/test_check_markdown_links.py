import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CHECKER = Path(__file__).with_name("check_markdown_links.py")


class MarkdownLinkCheckerCliTest(unittest.TestCase):
    def test_missing_input_path_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing = Path(temporary_directory) / "missing"

            result = subprocess.run(
                [sys.executable, str(CHECKER), str(missing)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn(f"input path does not exist: {missing}", result.stderr)

    def test_existing_local_target_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "docs").mkdir()
            (root / "README.md").write_text(
                "# Index\n\nSee [the result](docs/result.md#answer).\n",
                encoding="utf-8",
            )
            (root / "docs" / "result.md").write_text(
                "# Result\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(CHECKER), str(root)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_local_target_fails_with_source_location(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "# Index\n\nSee [the missing result](docs/missing.md).\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(CHECKER), str(root)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "README.md:3: missing local target: docs/missing.md",
                result.stdout,
            )

    def test_external_and_same_document_links_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "# Index\n\n"
                "See [the section](#details), "
                "[the website](https://example.com/missing.md), and "
                "[the author](mailto:author@example.com).\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(CHECKER), str(root)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout)

    def test_links_inside_fenced_examples_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "# Index\n\n"
                "```markdown\n"
                "[placeholder](not-a-real-file.md)\n"
                "```\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(CHECKER), str(root)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout)

    def test_links_inside_inline_code_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "# Index\n\nUse `[placeholder](not-a-real-file.md)` in examples.\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(CHECKER), str(root)],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
