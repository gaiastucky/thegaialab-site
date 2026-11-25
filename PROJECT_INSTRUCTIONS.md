# Gaia Lab website project

This project maintains thegaialab.com, the website of the Gaia Lab at MIT EAPS, led by Gaia Stucky de Quay. The site is a hand-built static site that replaces the old WordPress.com site.

## Source of truth

The code lives in the GitHub repository gaiastucky/thegaialab-site. At the start of any session that changes the site, attach the repository, clone it, make the change, run `python3 build.py`, check the result in the browser, then commit and push. Read README.md in the repository first. It explains the file layout and the build.

Content lives in four JSON files under `data/`. Most updates are edits to those files and need no change to `build.py`.

## Keep every new entry in the existing format

This rule matters more than any other. When Gaia gives something to add (a person, a paper, a trip, a course, a press item), copy the structure of the existing entries of the same kind exactly.

- Use the same fields, field order, group name and file conventions as the existing sibling entries. Do not add, drop or rename fields.
- Photos for people go in `assets/people/<firstname>-1.jpg` (main) and `-2.jpg` (second), 800 x 800 px JPEG, as for the other members.
- Do not change templates, CSS or page structure to fit a new entry. If the new content does not fit the existing format, ask Gaia first.
- Never publish a placeholder or a partial entry (for example a member with no bio). Ask for the missing text and publish the entry when it is complete.
- After the build, compare the new entry with an existing one on desktop and at iPhone width (393 px). Photo sizes, headings and text layout must match.
- `build.py` checks `people.json` against the allowed fields and stops if an entry differs from the format or has an empty bio. Team section headings come from `TEAM_GROUPS` by group name.

## How Gaia works

- Make the requested change directly and show it. Ask only when the request is ambiguous and a wrong guess is costly.
- Report each change in one or two plain sentences. No recaps.
- She often sends several small requests in a row. Handle every one and confirm each by name, so none is missed.
- Show changes in the browser pane after building. Take a screenshot to confirm before reporting.

## Writing rules for site text

- Use Gaia's own wording. When she gives text, use it verbatim apart from typos. Never invent bios, summaries or intros. Ask her for missing text.
- No em dashes and no double hyphens anywhere.
- Plain, direct prose. No marketing tone and no AI-sounding phrases.

## Design language

- White pages, pastel palette with a rusty Mars red accent (`--maroon #b5654a`), river blue `#9cc8ea` and pale rose `#f3e0d4`.
- Circles everywhere. Round photos, round map, numbered circles.
- Scroll effects. Banners move on scroll, rivers draw between sections, elements reveal as they enter.
- Rule for every trip album, existing and future: a packed collage. `collage_layout` in build.py splits one rectangle into nested rectangles of mixed sizes and shapes, keeps the photo order, and ends flush at the bottom. Phones get their own narrower layout. No grids, rows or columns. Gaia approved this look on 15 Nov 2026.
- New albums: Gaia exports about 20 photos per trip from Apple Photos to a Desktop folder (JPEG, location unticked). Run `python3 add_trip.py "Place" YEAR <folder>`, add the pin and her text in build.py, build, check.
- Every inner page opens with a banner of exactly one height (`BANNER_H` in build.py, 60vh), enforced in CSS with a fixed height so content cannot stretch it. Gallery's globe band uses the same height. Gaia has asked for this more than once; check banner heights on every page after any banner change. Home keeps its taller welcome hero, with a silent looping drone video of Fogo (2025) in `assets/video/` (1920 px desktop, 960 px phone, poster image as fallback). All banner photos and video get the same muted, faded earthy grade; match it when adding a new one. Research Themes uses Jökulsá á Fjöllum (2017), positioned to show the sky. Contact has no banner. Gallery's banner is the light grey globe band; clicking a pin opens that trip's photos below on the same page.
- Each section has one big h2 heading and no small label above it. Small blocks inside a section (Office, CV, alumni tiers) use `h3.sub`. Rivers (`dots()`) go only between the main sections of a page, never inside one.
- The Data & code banner is a live wireframe of real MOLA topography of Jezero crater (`assets/mars-mesh.json`).

- Teaching: courses Gaia no longer teaches are retired. Mark them `"retired": true` in `misc.json` courses. Retired courses show no image or video and sit two per row at the bottom of the Teaching section (as 12.S593 and 12.002).

## Pages

Home, Team, Research (Themes, Publications, Resources), Engagement (teaching, outreach videos, media timeline), Gallery (spinning globe with pins that open trip collages below it), Contact.

## Constraints

- Never write the email address in plain text. Use the `data-m` pattern described in the README.
- No sensitive CV content such as pending grants or money.
- Do not download images to Gaia's computer without asking.
- The live domain stays on WordPress until Gaia approves the switch. DNS changes only after her explicit approval.
- The site is public and indexed (NOINDEX = False, robots.txt allows all) since going live on 2026-11-15.

## Open items

- Copy the roughly 200 hotlinked WordPress images, the Elsevier figures and the logo into `assets/` before the WordPress site closes.
- Live at https://thegaialab.com (GitHub Pages, main branch root, CNAME file in the repo). Gaia approved the switch on 2026-11-15. DNS is managed at WordPress.com: apex A/AAAA records point to GitHub Pages, www is a CNAME to gaiastucky.github.io, buildingmars is a CNAME to building-mars.netlify.app (keep it). The old WordPress site still exists at thegaialab.wordpress.com.
- Mars globe on Resources (done). Texture `assets/mars-mola.jpg` is MOLA MEGDR downsampled to 1024x512 (via SPECFEM3D_GLOBE's 4 arcmin grid), coloured in the site palette with hillshade. Caption wording is a draft for Gaia to confirm.
- Home page "Follow us on LinkedIn" section links to the lab page https://www.linkedin.com/company/136993897/ (done). Shows the three latest lab posts as official LinkedIn embeds; their URNs are in `misc.linkedin_posts` (newest first). To update, take the URNs from the lab page's admin posts list (Gaia signs in to LinkedIn in the browser pane). The header LinkedIn icon also points to the lab page. Gaia wants the lab page used for every LinkedIn link on the site.
- Tibetan lakes paper summary drafted by Claude at Gaia's request. Awaiting her approval or edits.
- CV link (done). The Contact page links to `assets/cv.pdf`, the public CV built in the CV Project (no funding amounts, no pending grants, no phone). To update it, rebuild `cv-public.pdf` there and copy it over `assets/cv.pdf`. The CV source is kept out of this public repository.
- Mauricio is listed as a postdoc for 2025–2026 and will move to alumni when Gaia says so.

## Image storage
- Full-size originals of every image from the old WordPress site: `~/MIT Dropbox/Gaia Quay/Gaia_Lab_Website/media_originals/` (200 files, same YYYY/MM/name paths).
- Web copies (max 2400 px) live in the repo under `media/`. build.py serves `media/YYYY/MM/name` and no longer loads anything from WordPress.
