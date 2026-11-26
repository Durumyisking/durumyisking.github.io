import json
from pathlib import Path
import tempfile
import unittest

from build import build


class EditorialBuildTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.content = root / "content"
        self.assets = root / "assets"
        self.output = root / "site"
        for directory in ("articles", "categories", "media"):
            (self.content / directory).mkdir(parents=True)
        self.assets.mkdir()
        (self.assets / "site.css").write_text("body {}", encoding="utf-8")
        (self.content / "media" / "sample.svg").write_text("<svg/>", encoding="utf-8")

    def category(self, name, title, parent=None, order=10):
        if parent:
            parent = f"content/categories/{parent}.json"
        category = {"title": title, "parent": parent, "order": order}
        (self.content / "categories" / f"{name}.json").write_text(
            json.dumps(category), encoding="utf-8"
        )

    def post(self, name, title, category, body, order=10):
        source = (
            f"---\ntitle: {json.dumps(title)}\ncategory: content/categories/{category}.json\n"
            f"order: {order}\n---\n\n{body}\n"
        )
        (self.content / "articles" / f"{name}.md").write_text(source, encoding="utf-8")

    def html(self, path):
        return (self.output / path).read_text(encoding="utf-8")

    def test_post_lifecycle_and_category_changes(self):
        self.category("first", "First")
        self.category("second", "Second", order=20)
        self.category("nested", "Nested", parent="first")
        self.post("a", "Before", "nested", "<details><summary>Example</summary>Old</details>")
        self.post("b", "Other", "second", "[Article A](a.md)")
        self.assertEqual(build(self.content, self.assets, self.output), 2)
        self.assertIn("<li>First</li><li>Nested</li>", self.html("notes/a.html"))
        self.assertIn("<details><summary>Example</summary>Old</details>", self.html("notes/a.html"))

        self.category("nested", "Renamed", parent="second", order=1)
        self.post("a", "Updated", "nested", "```cpp\nint a = 1;\n```\n\n![Example](/media/sample.svg)")
        self.post("c", "New", "nested", "New content", order=5)
        self.assertEqual(build(self.content, self.assets, self.output), 3)
        page = self.html("notes/a.html")
        self.assertIn("<h1>Updated</h1>", page)
        self.assertIn("<li>Second</li><li>Renamed</li>", page)
        self.assertIn('class="code-block"', page)
        self.assertIn('src="/media/sample.svg"', page)
        self.assertTrue((self.output / "media" / "sample.svg").is_file())
        self.assertLess(self.html("index.html").index("notes/c.html"), self.html("index.html").index("notes/a.html"))
        self.assertIn('href="a.html"', self.html("notes/b.html"))

        self.post("c", "New", "first", "Moved again")
        (self.content / "articles" / "a.md").unlink()
        self.assertEqual(build(self.content, self.assets, self.output), 2)
        self.assertIn("<li>First</li>", self.html("notes/c.html"))
        self.assertFalse((self.output / "notes" / "a.html").exists())
        self.assertNotIn("a.html", self.html("index.html"))
        self.assertNotIn('href="a.html"', self.html("notes/b.html"))

    def test_rejects_circular_categories_and_missing_references(self):
        self.category("first", "First", parent="second")
        self.category("second", "Second", parent="first")
        with self.assertRaisesRegex(ValueError, "Category cycle"):
            build(self.content, self.assets, self.output)

        self.category("first", "First")
        self.post("a", "Invalid", "missing", "Body")
        with self.assertRaisesRegex(ValueError, "Unknown category"):
            build(self.content, self.assets, self.output)
