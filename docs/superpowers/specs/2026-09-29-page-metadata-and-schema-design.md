# Page Metadata and Schema Design

## Goal

Improve search-engine understanding of the site without duplicating irrelevant structured data or making claims that are not visible on the corresponding page.

## Scope

1. Add concise, distinct descriptions to the Research and Teaching landing pages.
2. Add `BlogPosting` JSON-LD to every news post.
3. Add `Course` JSON-LD to NYU Abu Dhabi course pages only.
4. Add an `ItemList` of the marked-up NYU Abu Dhabi courses to the course index.
5. Leave archived UC Irvine teaching-assistant pages without `Course` schema because their provider and instructional role differ from the NYU Abu Dhabi pages.

## Architecture

A small Quarto Lua filter will generate JSON-LD from explicit page metadata. News and course source files will declare only their page-specific data; the filter will handle JSON encoding and HTML insertion consistently. The existing hand-authored homepage and CV schemas will remain unchanged.

News posts will provide their existing title, date, and description to a `BlogPosting` object. The author will reference the existing canonical person identifier at `https://paulmaxlove.com/#person`.

NYU Abu Dhabi course pages will declare a schema course name and description. The generated `Course` object will identify New York University Abu Dhabi as the provider and Paul Max Love III as the instructor. The visible page will also carry a matching description so the structured data reflects readable content.

The course index will contain an `ItemList` whose entries point to each eligible course page. It will not include unlinked course names or UC Irvine teaching-assistant pages.

## Data and validation

Tests will first assert that:

- Research and Teaching have distinct descriptions.
- Every news post emits valid `BlogPosting` JSON-LD with headline, date, description, URL, and author.
- Every selected NYU Abu Dhabi course emits valid `Course` JSON-LD with name, description, provider, instructor, and URL.
- The course index emits a valid `ItemList` containing the eligible course URLs in visible order.
- UC Irvine teaching-assistant pages do not emit `Course` schema.

After implementation, the complete Quarto site will be rendered. Tests will parse JSON-LD from the generated HTML rather than relying only on source-text matching.

## Research notes

- Google recommends JSON-LD and requires structured data to represent visible page content: https://developers.google.com/search/docs/appearance/structured-data/sd-policies
- Google supports `Article`, `NewsArticle`, and `BlogPosting` for article pages and recommends author identity, headline, dates, and images where available: https://developers.google.com/search/docs/appearance/structured-data/article
- Google course-list eligibility requires at least three courses, individual course names and descriptions, provider data, and `ItemList` carousel markup: https://developers.google.com/search/docs/appearance/structured-data/course
- The repository currently hand-authors JSON-LD on the homepage and CV page only; no reusable schema filter exists.
- All three news posts already contain title, date, and description metadata. The NYU Abu Dhabi course pages require descriptions and explicit schema metadata.

## Alternatives considered

- Hand-author JSON-LD in every page: simple initially, but repetitive and prone to inconsistent URLs or malformed JSON.
- Apply `Person` or generic `WebPage` schema everywhere: little search benefit and risks describing content that is not the main subject of each page.
- Mark up every historical course page: rejected because the archived teaching-assistant pages have a different provider and instructional relationship.

## Out of scope

- Breadcrumb schema or visible breadcrumb navigation.
- Schema for training, research publications, or presentations.
- Adding images solely to satisfy optional article-schema recommendations.
