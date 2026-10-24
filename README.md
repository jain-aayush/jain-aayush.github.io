# Aayush Jain — professional portfolio

A deliberately small, photo-free, work-led static site. Semantic HTML, shared CSS,
and a local optional print-button script; no build, framework, package install,
external JavaScript, analytics, or network fonts. `/alfred` is a separate existing
site and must remain unchanged.

## Local preview

From this repository:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/` and `http://127.0.0.1:8000/resume.html`.
The homepage and native technical-details disclosures work without JavaScript.
The résumé supports browser Print / Save as PDF with or without JavaScript.
For a clean PDF, disable browser-generated headers/footers in the print dialog.
Do not upload the source résumé PDFs: they can contain private phone details.

## Tests

```sh
python3 -m unittest discover -s tests -v
```

Python standard library only. Checks current career content, metric qualifiers,
semantic landmarks, every HTML local href/src and fragment target, CSS url()
references (including fonts), same-origin canonical/social file targets, PNG
dimensions and social metadata, mobile heading spacing, print support, privacy,
and original SHA-256 digests for the two `/alfred` pages. Tests do not prove
visual quality or audit all browser/accessibility behavior.

## Maintain

- `index.html`: primary story, three flagship work rows, supporting systems,
  career progression, toolkit, writing, recognition, education, contact.
- `resume.html`: clean, phone-free print résumé. Keep its claims and dates in sync
  with the home page, preserving comparisons and attribution qualifiers.
- `static/css/style.css`: shared warm-paper/charcoal theme, responsive and print
  layouts. `#2A78D6` is decorative; darker `#17599f` is used for readable links.
- System SF Pro on Apple platforms via `-apple-system` / `BlinkMacSystemFont`;
  existing bundled HK Grotesk is a WOFF fallback, not a downloaded dependency.
- `static/images/social.png`: rendered 1200×630 social preview used by Open Graph
  and Twitter metadata; `social.svg` remains the editable source. Keep the PNG
  and its dimensions/type metadata synchronized after editing the SVG.
  `favicon.svg` is the authored text-led favicon. Check actual platform previews
  before publication; local checks do not verify crawler rendering.
- Existing unused legacy images/fonts remain unreferenced to avoid unrelated churn.
- No deploy automation or framework configuration is needed for static hosting.

## Publication checklist — required before merge

- [ ] Owner confirms all employer metrics and their publication permission **before merge**,
  especially scale, baselines, attribution, and confidential business figures.
- [ ] Preserve qualifiers: last-click ROAS is not causal incrementality; monthly GMV
  is supported, not generated; precision is at 10% recall; treatment changes are
  percentage points, not percent. Do not imply three direct reports.
- [ ] Owner confirms role titles/dates, email, education, recognition wording, and
  that historical Kaggle ranks are not presented as current.
- [ ] Confirm canonical origin `https://jain-aayush.github.io/` and social previews.
- [ ] Run tests. Check desktop and 320/375px mobile views, 200% zoom, keyboard
  navigation, visible focus, skip link, native disclosures, and no-JS rendering.
- [ ] Preview résumé printing on A4 and Letter; ensure nothing is clipped and
  browser-added URLs do not expose unwanted details. No source PDF/phone published.
- [ ] Confirm `git diff -- alfred` is empty. Review changed files for private data.
- [ ] Obtain explicit owner approval before merging. A PR branch does not deploy.
  Merging `master` automatically publishes via the existing GitHub Pages
  configuration, so approval must cover publication as well as the code changes.
