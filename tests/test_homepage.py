import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HomepageContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.home = (ROOT / "index.qmd").read_text(encoding="utf-8")
        cls.cv = (ROOT / "cv.qmd").read_text(encoding="utf-8")
        cls.teaching = (ROOT / "teaching" / "index.qmd").read_text(encoding="utf-8")
        cls.config = (ROOT / "_quarto.yml").read_text(encoding="utf-8")
        cls.styles = (ROOT / "styles.css").read_text(encoding="utf-8")
        cls.head_include = (ROOT / "_head-include.html").read_text(encoding="utf-8")

    def test_homepage_has_search_metadata_without_article_date(self):
        self.assertIn(
            'pagetitle: "Political Scientist at NYU Abu Dhabi"',
            self.home,
        )
        self.assertIn('title: "Paul Max Love III | Political Scientist at NYU Abu Dhabi"', self.home)
        self.assertIn(
            'description: "Paul is a Full Instructor of Social Science/Academic Specialist at NYU Abu Dhabi who teaches quantitative methods and researches European strategic culture, digital sovereignty, and Arctic security."',
            self.home,
        )
        self.assertIn("#title-block-header .description", self.home)
        self.assertIn("display: none", self.home)
        self.assertNotIn("date:", self.home)

    def test_current_position_title_precedes_former_title(self):
        title = "Full Instructor of Social Science/Academic Specialist"
        self.assertIn(title, self.home)
        self.assertIn(title, self.cv)
        self.assertIn(title, self.teaching)
        self.assertIn(title, self.config)

    def test_homepage_keeps_only_unique_external_profile_links(self):
        for destination in (
            "https://nyuad.nyu.edu/en/academics/divisions/social-science/instructors/paul-love.html",
            "https://github.com/pmlove3",
            "https://www.linkedin.com/in/paulmaxlove3/",
        ):
            self.assertIn(destination, self.home)
        for duplicate_destination in (
            'href="research/index.html"',
            'href="teaching/index.html"',
            'href="cv.html"',
            "news/index.html",
        ):
            self.assertNotIn(duplicate_destination, self.home)

    def test_city_follows_role_title(self):
        hero = self.home.split("::: {.home-hero}", 1)[1]
        self.assertLess(
            hero.index("::: {.home-role}"),
            hero.index("::: {.hero-eyebrow}"),
        )

    def test_homepage_uses_single_column_without_actions_or_map(self):
        self.assertIn("max-width: 680px", self.styles)
        self.assertNotIn("home-actions", self.home)
        self.assertNotIn("home-news-link", self.home)
        self.assertNotIn("hero-worldmap", self.home)
        self.assertNotIn("abu-dhabi-world-dotmap", self.home)

    def test_homepage_has_website_and_person_structured_data(self):
        self.assertIn('type="application/ld+json"', self.home)
        self.assertIn('"@type": "WebSite"', self.home)
        self.assertIn('"@type": "Person"', self.home)
        self.assertIn('"jobTitle": "Full Instructor of Social Science/Academic Specialist"', self.home)

    def test_cv_page_has_profile_page_structured_data(self):
        self.assertIn('type="application/ld+json"', self.cv)
        self.assertIn('"@type": "ProfilePage"', self.cv)
        self.assertIn('"mainEntity"', self.cv)
        self.assertIn('"@id": "https://paulmaxlove.com/#person"', self.cv)
        self.assertIn('"jobTitle": "Full Instructor of Social Science/Academic Specialist"', self.cv)

    def test_cv_visible_profile_uses_first_person(self):
        body = self.cv.split("---", 2)[2]
        self.assertIn(
            "I am a Full Instructor of Social Science/Academic Specialist",
            body,
        )
        self.assertNotIn("Paul ", body)
        self.assertNotIn("He ", body)

    def test_decorative_map_is_removed(self):
        self.assertNotIn('alt="" aria-hidden="true"', self.home)

    def test_social_metadata_and_accessible_link_sizes_are_enabled(self):
        self.assertIn("open-graph: true", self.config)
        self.assertIn("twitter-card: true", self.config)
        self.assertIn("min-height: 44px", self.styles)
        self.assertIn("min-width: 44px", self.styles)

    def test_home_icon_link_receives_accessible_name(self):
        self.assertIn('homeLink.setAttribute("aria-label", "Home")', self.head_include)
        self.assertIn('homeIcon.setAttribute("aria-hidden", "true")', self.head_include)

    def test_fenced_div_markers_are_balanced(self):
        lines = [line.strip() for line in self.home.splitlines()]
        openings = sum(line.startswith("::: {") for line in lines)
        closings = sum(line == ":::" for line in lines)
        self.assertEqual(openings, closings)


if __name__ == "__main__":
    unittest.main()
