import json
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class JsonLdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.documents = []
        self._capturing = False
        self._parts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "script" and attributes.get("type") == "application/ld+json":
            self._capturing = True
            self._parts = []

    def handle_data(self, data):
        if self._capturing:
            self._parts.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._capturing:
            self.documents.append(json.loads("".join(self._parts)))
            self._capturing = False
            self._parts = []


def json_ld_documents(relative_html_path):
    parser = JsonLdParser()
    parser.feed((ROOT / "docs" / relative_html_path).read_text(encoding="utf-8"))
    return parser.documents


def schema_documents(relative_html_path, schema_type):
    documents = []
    for document in json_ld_documents(relative_html_path):
        if document.get("@type") == schema_type:
            documents.append(document)
        for graph_item in document.get("@graph", []):
            if graph_item.get("@type") == schema_type:
                documents.append(graph_item)
    return documents


class PageDescriptionTests(unittest.TestCase):
    def test_research_and_teaching_have_distinct_descriptions(self):
        research = (ROOT / "research" / "index.qmd").read_text(encoding="utf-8")
        teaching = (ROOT / "teaching" / "index.qmd").read_text(encoding="utf-8")

        self.assertIn(
            'description: "Research by Paul Max Love III on European strategic culture, digital sovereignty, Arctic security, and international relations."',
            research,
        )
        self.assertIn(
            'description: "Courses, teaching resources, guest lectures, and professional training from Paul Max Love III at NYU Abu Dhabi."',
            teaching,
        )


class ResearchContentTests(unittest.TestCase):
    def test_advancement_exam_uses_phd_capitalization_and_date_only(self):
        research = (ROOT / "research" / "index.qmd").read_text(encoding="utf-8")

        self.assertIn("## PhD Advancement Exam", research)
        self.assertIn("Date: 4 June 2020", research)
        self.assertNotIn("## PHD Advancement Exam", research)
        self.assertNotIn("11:00 am to 1:00 pm", research)


class NewsSchemaTests(unittest.TestCase):
    NEWS_POSTS = {
        "news/2025-07-29-isa-virtual-2025.html": {
            "headline": "ISA Virtual 2025",
            "datePublished": "2025-07-29",
            "description": "Notes and a multidimensional plot from the ISA Virtual 2025 presentation.",
        },
        "news/2026-09-02-fall-2026-courses.html": {
            "headline": "Fall 2026: teaching International Security",
            "datePublished": "2026-09-02",
            "description": "Course materials for Fall 2026 International Security are now up.",
        },
        "news/2026-09-13-cv-update.html": {
            "headline": "CV updated",
            "datePublished": "2026-09-13",
            "description": "A refreshed CV is posted, covering recent teaching and research activity.",
        },
    }

    def test_news_posts_emit_blog_posting_schema(self):
        author = {
            "@type": "Person",
            "@id": "https://paulmaxlove.com/#person",
            "name": "Paul Max Love III",
            "url": "https://paulmaxlove.com/",
        }

        for relative_path, expected in self.NEWS_POSTS.items():
            with self.subTest(page=relative_path):
                documents = schema_documents(relative_path, "BlogPosting")
                self.assertEqual(len(documents), 1)
                document = documents[0]
                self.assertEqual(document["@context"], "https://schema.org")
                self.assertEqual(document["headline"], expected["headline"])
                self.assertEqual(document["datePublished"], expected["datePublished"])
                self.assertEqual(document["description"], expected["description"])
                self.assertEqual(
                    document["url"], f"https://paulmaxlove.com/{relative_path}"
                )
                self.assertEqual(document["author"], author)


class CourseSchemaTests(unittest.TestCase):
    COURSES = {
        "teaching/courses/2023-fall-stats.html": (
            "Statistics for Social and Behavioral Sciences",
            "Course materials for Statistics for Social and Behavioral Sciences, taught by Paul Max Love III at NYU Abu Dhabi in Fall 2023.",
        ),
        "teaching/courses/2024-spring-stats.html": (
            "Statistics for Social and Behavioral Sciences",
            "Course materials for Statistics for Social and Behavioral Sciences, taught by Paul Max Love III at NYU Abu Dhabi in Spring 2024.",
        ),
        "teaching/courses/2024-summer-boundaries.html": (
            "Boundaries",
            "Course materials for Boundaries, taught by Paul Max Love III at NYU Abu Dhabi in Summer 2024.",
        ),
        "teaching/courses/2024-fall-stats.html": (
            "Statistics for Social and Behavioral Sciences",
            "Course materials for Statistics for Social and Behavioral Sciences, taught by Paul Max Love III at NYU Abu Dhabi in Fall 2024.",
        ),
        "teaching/courses/2025-spring-da.html": (
            "Data Analysis",
            "Course materials for Data Analysis, taught by Paul Max Love III at NYU Abu Dhabi in Spring 2025.",
        ),
        "teaching/courses/2025-spring-stats.html": (
            "Statistics for Social and Behavioral Sciences",
            "Course materials for Statistics for Social and Behavioral Sciences, taught by Paul Max Love III at NYU Abu Dhabi in Spring 2025.",
        ),
        "teaching/courses/2025-fall-da.html": (
            "Data Analysis: Political Science",
            "Course materials for Data Analysis: Political Science, taught by Paul Max Love III at NYU Abu Dhabi in Fall 2025.",
        ),
        "teaching/courses/2025-2026-capstone.html": (
            "Capstone Seminar",
            "Course materials for the Capstone Seminar, taught by Paul Max Love III at NYU Abu Dhabi during 2025–2026.",
        ),
        "teaching/courses/2026-jterm-politics.html": (
            "Practising Politics and Government in the Age of Disruption",
            "Course materials for Practising Politics and Government in the Age of Disruption, co-taught by Paul Max Love III at NYU Abu Dhabi in January 2026.",
        ),
        "teaching/courses/2026-spring-da.html": (
            "Data Analysis: Political Science",
            "Course materials for Data Analysis: Political Science, taught by Paul Max Love III at NYU Abu Dhabi in Spring 2026.",
        ),
        "teaching/courses/2026-fall-is.html": (
            "International Security",
            "Course materials for International Security, taught by Paul Max Love III at NYU Abu Dhabi in Fall 2026.",
        ),
    }

    def test_nyu_abu_dhabi_courses_emit_course_schema(self):
        provider = {
            "@type": "CollegeOrUniversity",
            "name": "New York University Abu Dhabi",
            "url": "https://nyuad.nyu.edu/",
        }
        instructor = {
            "@type": "Person",
            "@id": "https://paulmaxlove.com/#person",
            "name": "Paul Max Love III",
            "url": "https://paulmaxlove.com/",
        }

        for relative_path, (name, description) in self.COURSES.items():
            with self.subTest(page=relative_path):
                documents = schema_documents(relative_path, "Course")
                self.assertEqual(len(documents), 1)
                document = documents[0]
                self.assertEqual(document["@context"], "https://schema.org")
                self.assertEqual(document["name"], name)
                self.assertEqual(document["description"], description)
                self.assertEqual(
                    document["url"], f"https://paulmaxlove.com/{relative_path}"
                )
                self.assertEqual(document["provider"], provider)
                self.assertNotIn("instructor", document)
                self.assertEqual(
                    document["hasCourseInstance"],
                    {"@type": "CourseInstance", "instructor": instructor},
                )

    def test_uc_irvine_archives_do_not_emit_course_schema(self):
        for relative_path in (
            "teaching/courses/2018-fall-american-government.html",
            "teaching/courses/2021-spring-vpm.html",
        ):
            with self.subTest(page=relative_path):
                self.assertEqual(schema_documents(relative_path, "Course"), [])


class CourseListSchemaTests(unittest.TestCase):
    COURSE_URLS = [
        "https://paulmaxlove.com/teaching/courses/2026-fall-is.html",
        "https://paulmaxlove.com/teaching/courses/2026-spring-da.html",
        "https://paulmaxlove.com/teaching/courses/2026-jterm-politics.html",
        "https://paulmaxlove.com/teaching/courses/2025-2026-capstone.html",
        "https://paulmaxlove.com/teaching/courses/2025-fall-da.html",
        "https://paulmaxlove.com/teaching/courses/2025-spring-da.html",
        "https://paulmaxlove.com/teaching/courses/2025-spring-stats.html",
        "https://paulmaxlove.com/teaching/courses/2024-fall-stats.html",
        "https://paulmaxlove.com/teaching/courses/2024-summer-boundaries.html",
        "https://paulmaxlove.com/teaching/courses/2024-spring-stats.html",
        "https://paulmaxlove.com/teaching/courses/2023-fall-stats.html",
    ]

    def test_course_index_emits_ordered_item_list_schema(self):
        documents = schema_documents("teaching/courses/index.html", "ItemList")
        self.assertEqual(len(documents), 1)
        document = documents[0]
        self.assertEqual(document["@context"], "https://schema.org")
        self.assertEqual(
            document["itemListElement"],
            [
                {"@type": "ListItem", "position": position, "url": url}
                for position, url in enumerate(self.COURSE_URLS, start=1)
            ],
        )


if __name__ == "__main__":
    unittest.main()
