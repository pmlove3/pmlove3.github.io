# Paul Max Love III

Website

[https://pmlove3.github.io](https://pmlove3.github.io)

## Development

### Accessibility Auditing

To ensure the site continues to meet WCAG 2.2 AA standards, you can run a local accessibility audit. The audit uses Playwright and `axe-core` to scan the generated `docs/` HTML.

First, render the Quarto site:
```bash
quarto render
```

Then run the audit script:
```bash
npm install
npm run audit
```