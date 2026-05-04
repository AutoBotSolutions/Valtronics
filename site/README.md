# Valtronics Website

This directory contains the static website for Valtronics, deployed to GitHub Pages.

## Structure

- `index.html` - Main landing page
- `api.html` - API documentation
- `contact.html` - Contact information
- `docs.html` - Documentation
- `examples.html` - Usage examples
- `firmware.html` - Firmware development
- `valtronics-*.html` - Project thesis documents
- `404.html` - Custom error page
- `favicon.svg` - Site icon

## Deployment

The website is automatically deployed to GitHub Pages using GitHub Actions when changes are pushed to the main branch.

### URL
https://autobotsolutions.github.io/Valtronics/

### Development

To test locally:
```bash
# Use any static server
python -m http.server 8000
# or
npx serve .
# then visit http://localhost:8000
```

### Build Process

The site is built as static HTML files with embedded CSS and JavaScript. No build step is required - just commit changes and they will be automatically deployed.
