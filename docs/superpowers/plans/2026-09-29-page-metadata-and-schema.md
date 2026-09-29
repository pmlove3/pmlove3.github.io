# Page Metadata and Schema Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superjawn:subagent-driven-development (recommended) or superjawn:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add useful page descriptions and valid, page-specific JSON-LD to news posts and NYU Abu Dhabi course pages.

**Architecture:** A focused Quarto Lua filter reads explicit `schema-type` metadata and inserts JSON-LD into each eligible page head. Page source files retain human-readable title, date, description, and course identity; generated HTML is parsed in integration tests to verify the public output.

**Tech Stack:** Quarto, Pandoc Lua filters, YAML front matter, Python `unittest`, HTML parsing with the Python standard library.

---

### Task 1: Page descriptions

**Files:**
- Modify: `research/index.qmd`
- Modify: `teaching/index.qmd`
- Test: `tests/test_structured_data.py`

- [ ] **Step 1: Write the failing description test**

Create a test that reads both source files and asserts these exact, distinct descriptions:

```python
def test_research_and_teaching_have_distinct_descriptions(self):
    research = (ROOT / "research/index.qmd").read_text(encoding="utf-8")
    teaching = (ROOT / "teaching/index.qmd").read_text(encoding="utf-8")
    self.assertIn(
        'description: "Research by Paul Max Love III on European strategic culture, digital sovereignty, Arctic security, and international relations."',
        research,
    )
    self.assertIn(
        'description: "Courses, teaching resources, guest lectures, and professional training from Paul Max Love III at NYU Abu Dhabi."',
        teaching,
    )
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python3 -m unittest tests.test_structured_data.PageDescriptionTests -v`

Expected: FAIL because neither description exists yet.

- [ ] **Step 3: Add the two descriptions**

Add the exact tested `description` values to the YAML front matter of `research/index.qmd` and `teaching/index.qmd`.

- [ ] **Step 4: Run the description test**

Run: `python3 -m unittest tests.test_structured_data.PageDescriptionTests -v`

Expected: PASS.

### Task 2: Reusable JSON-LD filter and news schema

**Files:**
- Create: `_extensions/site-schema/site-schema.lua`
- Create: `_extensions/site-schema/_extension.yml`
- Modify: `_quarto.yml`
- Modify: `news/2025-07-29-isa-virtual-2025.qmd`
- Modify: `news/2026-09-02-fall-2026-courses.qmd`
- Modify: `news/2026-09-13-cv-update.qmd`
- Test: `tests/test_structured_data.py`

- [ ] **Step 1: Write failing generated-output tests**

Add helpers that use `html.parser.HTMLParser` to collect `<script type="application/ld+json">` contents and `json.loads` to parse them. Assert that each generated news page contains one `BlogPosting` object with:

```python
{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": expected_title,
    "datePublished": expected_date,
    "description": expected_description,
    "url": expected_canonical_url,
    "author": {
        "@type": "Person",
        "@id": "https://paulmaxlove.com/#person",
        "name": "Paul Max Love III",
        "url": "https://paulmaxlove.com/",
    },
}
```

- [ ] **Step 2: Render and verify the news tests fail**

Run: `quarto render && python3 -m unittest tests.test_structured_data.NewsSchemaTests -v`

Expected: FAIL because no news page currently contains JSON-LD.

- [ ] **Step 3: Add the extension and project filter**

Register the extension in `_extensions/site-schema/_extension.yml`:

```yaml
title: Site Schema
author: Paul Max Love III
version: 1.0.0
quarto-required: ">=1.4.0"
contributes:
  filters:
    - site-schema.lua
```

Add `site-schema` to the project `filters` list in `_quarto.yml`. In `site-schema.lua`, stringify metadata safely, JSON-escape string values, construct only the selected schema type, and insert it with:

```lua
quarto.doc.include_text(
  "in-header",
  '<script type="application/ld+json">\n' .. json .. '\n</script>'
)
```

- [ ] **Step 4: Mark the news posts**

Add this metadata to each of the three news posts:

```yaml
author: "Paul Max Love III"
schema-type: blog-posting
```

The author field supplies a visible byline. The filter will derive title, author, date, description, and canonical URL from page metadata and the page path.

- [ ] **Step 5: Render and run the news schema tests**

Run: `quarto render && python3 -m unittest tests.test_structured_data.NewsSchemaTests -v`

Expected: PASS with three valid `BlogPosting` objects.

### Task 3: NYU Abu Dhabi course schema

**Files:**
- Modify: `teaching/courses/2023-fall-stats.qmd`
- Modify: `teaching/courses/2024-spring-stats.qmd`
- Modify: `teaching/courses/2024-summer-boundaries.qmd`
- Modify: `teaching/courses/2024-fall-stats.qmd`
- Modify: `teaching/courses/2025-spring-da.qmd`
- Modify: `teaching/courses/2025-spring-stats.qmd`
- Modify: `teaching/courses/2025-fall-da.qmd`
- Modify: `teaching/courses/2025-2026-capstone.qmd`
- Modify: `teaching/courses/2026-jterm-politics.qmd`
- Modify: `teaching/courses/2026-spring-da.qmd`
- Modify: `teaching/courses/2026-fall-is.qmd`
- Modify: `_extensions/site-schema/site-schema.lua`
- Test: `tests/test_structured_data.py`

- [ ] **Step 1: Write failing course-schema tests**

For each selected page, assert that the generated HTML contains one `Course` object with its expected name, description, canonical URL, and these common values:

```python
{
    "provider": {
        "@type": "CollegeOrUniversity",
        "name": "New York University Abu Dhabi",
        "url": "https://nyuad.nyu.edu/",
    },
    "instructor": {
        "@type": "Person",
        "@id": "https://paulmaxlove.com/#person",
        "name": "Paul Max Love III",
        "url": "https://paulmaxlove.com/",
    },
}
```

Also assert that `2018-fall-american-government.html` and `2021-spring-vpm.html` do not contain a `Course` object.

- [ ] **Step 2: Render and verify the course tests fail**

Run: `quarto render && python3 -m unittest tests.test_structured_data.CourseSchemaTests -v`

Expected: FAIL because no course page currently contains `Course` JSON-LD.

- [ ] **Step 3: Add explicit course metadata**

Add a concise `description`, a matching introductory sentence in the visible page body, and these fields to each selected NYU Abu Dhabi course file:

```yaml
schema-type: course
course-name: "Course name without the semester suffix"
```

The metadata descriptions and visible introductions will identify the course materials, course name, institution, semester, and Paul Max Love III as the instructor without claiming that private Brightspace or Drive content is publicly available.

- [ ] **Step 4: Generate `Course` JSON-LD**

Extend `site-schema.lua` so `schema-type: course` emits the tested object using `course-name`, `description`, and the canonical page URL plus the common provider and instructor objects.

- [ ] **Step 5: Render and run the course-schema tests**

Run: `quarto render && python3 -m unittest tests.test_structured_data.CourseSchemaTests -v`

Expected: PASS for all eleven NYU Abu Dhabi pages and both excluded UC Irvine pages.

### Task 4: Course-list schema

**Files:**
- Modify: `teaching/courses/index.qmd`
- Modify: `_extensions/site-schema/site-schema.lua`
- Test: `tests/test_structured_data.py`

- [ ] **Step 1: Write the failing course-list test**

Assert that `docs/teaching/courses/index.html` contains an `ItemList` object with eleven sequential `ListItem` entries. Each entry must contain `position` and the canonical URL of a marked-up NYU Abu Dhabi course page in the same order in which that course appears on the visible index.

- [ ] **Step 2: Render and verify the course-list test fails**

Run: `quarto render && python3 -m unittest tests.test_structured_data.CourseListSchemaTests -v`

Expected: FAIL because the index does not contain `ItemList` JSON-LD.

- [ ] **Step 3: Add course-list metadata and generation**

Add `schema-type: course-list` and an ordered `course-list` sequence of eleven relative course URLs to the index front matter. Extend the filter to emit:

```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "url": "https://paulmaxlove.com/teaching/courses/2026-fall-is.html"
    }
  ]
}
```

with all eleven entries.

- [ ] **Step 4: Render and run the course-list test**

Run: `quarto render && python3 -m unittest tests.test_structured_data.CourseListSchemaTests -v`

Expected: PASS.

### Task 5: Full verification

**Files:**
- Test: `tests/test_homepage.py`
- Test: `tests/test_structured_data.py`

- [ ] **Step 1: Run the complete render and test suite**

Run: `quarto render && python3 -m unittest discover -s tests -v`

Expected: the complete site renders and every test passes.

- [ ] **Step 2: Check source formatting and changed files**

Run: `git diff --check && git status --short`

Expected: no whitespace errors; status lists only the intended source, test, extension, and existing user changes.

- [ ] **Step 3: Inspect generated JSON-LD**

Parse every generated `application/ld+json` script with Python `json.loads`. Confirm there are no invalid JSON documents and that the expected schema types are present only on their intended pages.
