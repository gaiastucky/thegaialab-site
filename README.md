# thegaialab.com

Static website for the Gaia Lab (MIT EAPS). A single Python script builds every page from four JSON files. No framework and no database.

## Build

```
python3 build.py              # live site, one folder per page (team/index.html etc.)
python3 build.py --preview    # flat copy in preview/ with CSS and JS inlined
python3 build.py --pane       # flat copy in pane/ for checks in a browser on thegaialab.com
```

Only the live build is published. `preview/` and `pane/` are scratch output and can be deleted.

## Where things live

| Path | Contents |
|---|---|
| `build.py` | All page templates and the build logic |
| `data/people.json` | Team members, alumni, mascot. Bios, project titles, photos, dates |
| `data/publications.json` | Papers by year, with journal, authors, summary, DOI and figure URLs |
| `data/themes.json` | Research themes and their numbered questions |
| `data/misc.json` | Courses, press items, fieldwork trips and photos, resources, CV link, banner images |
| `assets/style.css` | All styling. Later blocks override earlier ones |
| `assets/site.js` | Scroll effects, rivers, theme lines, globe, figure mosaic, lightbox, email button |
| `assets/logo*.webp` | Lab logo (header mark and full logo) |
| `assets/people/` | Member photos that are not hosted on WordPress |

## Common edits

- New member or alumni move. Edit `data/people.json`. Alumni use a `project` field in place of a bio. Tiers are set by the role text (postdoc, graduate, visiting, undergraduate).
- New paper. Add an entry under its year in `data/publications.json`. Figures are a list of image URLs. More than four figures show a "+N" tag.
- New fieldwork trip. Run `python3 add_trip.py "Place" YEAR <photo folder> [--kind "Field trip"]`. It stores the photos in `assets/fieldwork/<slug>/` and adds the trip to `misc.fieldwork`. Then add its coordinates to `FIELD_SITES` and its text to `FIELD_TEXT` in `build.py`. Every trip album is drawn as a packed collage by `collage()`; keep it that way.
- New course or press item. Edit `misc.courses` or `misc.press`.

Run `python3 build.py` after every edit.

## Rules

- The email address is never written out in HTML. `data-m` holds the address reversed and base64 encoded, and `site.js` assembles it on click.
- No em dashes and no double hyphens in any text.
- Wording on the site is Gaia's own. Do not add generated copy.
- No pending grants, salaries or other sensitive CV content.

## Images

About 200 images still load from `thegaialab.files.wordpress.com`, plus figures from `ars.els-cdn.com` and the logo from Google Drive. They must be copied into `assets/` and the URLs in the JSON files updated before the WordPress site is closed.
