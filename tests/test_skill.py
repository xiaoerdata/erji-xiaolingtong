import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def load(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

nav = load("nav", ROOT / "erji-xiaolingtong/scripts/compare_nav.py")
pack = load("pack", ROOT / "tools/package_skill.py")

class NavTests(unittest.TestCase):
    def compare(self, text):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "input.csv"
            file.write_text(text, encoding="utf-8")
            return nav.compare(file, "adjusted-nav")

    def test_known_drawdown(self):
        result = nav.compare(ROOT / "erji-xiaolingtong/assets/example-nav.csv", "reference-nav")
        self.assertTrue(result["approximate"])
        self.assertAlmostEqual(result["results"][0]["totalReturn"], .1)
        self.assertAlmostEqual(result["results"][0]["sampledMaxDrawdown"], -.05)
        self.assertIsNotNone(result["results"][0]["annualizedReturn"])

    def test_missing_dates_are_excluded_and_short_history_not_annualized(self):
        r = self.compare("product,date,nav\nA,2026-01-01,1\nA,2026-01-02,2\nA,2026-01-03,3\nB,2026-01-01,2\nB,2026-01-03,4\n")
        self.assertEqual(r["commonPoints"], 2)
        self.assertEqual(r["results"][0]["excludedNonCommonPoints"], 1)
        self.assertIsNone(r["results"][0]["annualizedReturn"])

    def test_bad_inputs_rejected(self):
        for values in ["A,2026-01-01,1\nA,2026-01-01,2\nB,2026-01-01,2", "A,2026-01-01,nan\nB,2026-01-01,2", "A,2026-01-01,1\nB,2026-01-02,2", "A,2026-01-01,\nB,2026-01-01,2", "A,2026-01-01,-1\nB,2026-01-01,2"]:
            with self.subTest(values=values), self.assertRaises(ValueError):
                self.compare("product,date,nav\n" + values + "\n")

class PackageTests(unittest.TestCase):
    def test_reproducible_allowlisted_archives(self):
        self.assertEqual(pack.archive(), pack.archive())
        with zipfile.ZipFile(io.BytesIO(pack.archive())) as z:
            self.assertEqual(len(z.namelist()), len(pack.FILES) + 1)
            for n in z.namelist():
                self.assertTrue(n.startswith(pack.SLUG + "/"))
                self.assertNotIn("..", Path(n).parts)
                self.assertNotIn("__pycache__", n)
            self.assertIsNone(z.testzip())
            for name in z.namelist():
                if name.endswith((".md", ".yaml")):
                    self.assertNotRegex(z.read(name).decode(), r"(?i)\b(?:core|vip)\b")
        with zipfile.ZipFile(io.BytesIO(pack.archive(True))) as z:
            skill = z.read(pack.SLUG + "/SKILL.md").decode()
            self.assertIn('display_name: "二级小灵通"', skill)
            self.assertIn(f'version: "{pack.VERSION}"', skill)
            self.assertNotRegex(skill, r"(?i)\b(?:core|vip)\b")
            self.assertNotIn("TODO", skill)

if __name__ == "__main__":
    unittest.main()
