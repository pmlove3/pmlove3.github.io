import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THEME_DIRS = [ROOT / "resources" / "r", ROOT / "resources" / "stata"]

MIN_LINKS = 8
MIN_INTRO_WORDS = 25
MIN_ANNOTATION_CHARS = 20

LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
TRACKING = re.compile(r"[?&](utm_[a-z]+|fbclid|gclid)=")
BLOCK_START = ("#", "-", "*", "|", ":", "`")


def theme_pages():
    return sorted(path for directory in THEME_DIRS for path in directory.glob("*.qmd"))


def parse(path):
    match = re.match(r"---\n(.*?)\n---\n(.*)", path.read_text(encoding="utf-8"), re.S)
    if not match:
        raise AssertionError(f"{path.name}: missing YAML front matter")
    return match.group(1), match.group(2)


def intro_words(body):
    intro = []
    for line in body.strip().splitlines():
        if line.strip().startswith(BLOCK_START):
            break
        intro.append(line)
    return len(re.findall(r"\w+", " ".join(intro)))


def link_lines(body):
    return [line for line in body.splitlines()
            if line.strip().startswith(("-", "*", "|")) and LINK.search(line)]


def annotation(line):
    rest = LINK.sub("", line).replace("|", " ")
    return " ".join(rest.strip(" -*—–\t").split())


class ResourceThemePageTests(unittest.TestCase):
    def test_theme_pages_exist(self):
        self.assertTrue(theme_pages(), "no theme pages found under resources/r or resources/stata")

    def test_pages_have_description_and_intro(self):
        for path in theme_pages():
            with self.subTest(page=path.name):
                front, body = parse(path)
                self.assertRegex(front, r"(?m)^description:\s*\S", "missing description")
                self.assertGreaterEqual(intro_words(body), MIN_INTRO_WORDS, "intro paragraph too short")

    def test_pages_are_not_thin(self):
        for path in theme_pages():
            with self.subTest(page=path.name):
                _, body = parse(path)
                self.assertGreaterEqual(len(LINK.findall(body)), MIN_LINKS, "fewer than 8 links")

    def test_every_link_is_annotated(self):
        for path in theme_pages():
            with self.subTest(page=path.name):
                _, body = parse(path)
                bare = [line.strip()[:80] for line in link_lines(body)
                        if len(annotation(line)) < MIN_ANNOTATION_CHARS]
                self.assertEqual(bare, [], "links without an annotation")

    def test_no_duplicate_or_tracked_urls(self):
        for path in theme_pages():
            with self.subTest(page=path.name):
                _, body = parse(path)
                urls = [url for _, url in LINK.findall(body)]
                self.assertEqual(len(urls), len(set(urls)), "duplicate URL on page")
                self.assertEqual([u for u in urls if TRACKING.search(u)], [], "tracking parameters in URL")


if __name__ == "__main__":
    unittest.main()
