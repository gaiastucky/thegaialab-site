# Gaia Lab website project

This project maintains thegaialab.com, the website of the Gaia Lab at MIT EAPS, led by Gaia Stucky de Quay. The site is a hand-built static site that replaces the old WordPress.com site.

## Source of truth

The code lives in the GitHub repository gaiastucky/thegaialab-site. At the start of any session that changes the site, attach the repository, clone it, make the change, run `python3 build.py`, check the result in the browser, then commit and push. Read README.md in the repository first. It explains the file layout and the build.

Content lives in four JSON files under `data/`. Most updates are edits to those files and need no change to `build.py`.

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
- Every inner page opens with a banner of exactly one height (`BANNER_H` in build.py, 60vh), enforced in CSS with a fixed height so content cannot stretch it. Gallery's globe band uses the same height. Gaia has asked for this more than once; check banner heights on every page after any banner change. Home keeps its taller welcome hero. Contact has no banner. Gallery's banner is the light grey globe band; clicking a pin opens that trip's photos below on the same page.
- Each section has one big h2 heading and no small label above it. Small blocks inside a section (Office, CV, alumni tiers) use `h3.sub`. Rivers (`dots()`) go only between the main sections of a page, never inside one.
- The Data & code banner is a live wireframe of real MOLA topography of Jezero crater (`assets/mars-mesh.json`).

## Pages

Home, Team, Research (Themes, Publications, Resources), Engagement (teaching, outreach videos, media timeline), Gallery (spinning globe with pins that open trip collages below it), Contact.

## Constraints

- Never write the email address in plain text. Use the `data-m` pattern described in the README.
- No sensitive CV content such as pending grants or money.
- Do not download images to Gaia's computer without asking.
- The live domain stays on WordPress until Gaia approves the switch. DNS changes only after her explicit approval.
- The preview site, once set up, must stay hidden from search engines (noindex and robots.txt).

## Open items

- Copy the roughly 200 hotlinked WordPress images, the Elsevier figures and the logo into `assets/` before the WordPress site closes.
- Preview site is live at https://gaiastucky.github.io/thegaialab-site/ (GitHub Pages, main branch root, noindex via `NOINDEX` in build.py plus robots.txt). Images still load from WordPress until copied into `media/`. Domain switch waits for Gaia's approval.
- Mars globe on Resources (done). Texture `assets/mars-mola.jpg` is MOLA MEGDR downsampled to 1024x512 (via SPECFEM3D_GLOBE's 4 arcmin grid), coloured in the site palette with hillshade. Caption wording is a draft for Gaia to confirm.
- Home page "Follow us on LinkedIn" section links to the lab page https://www.linkedin.com/company/136993897/ (done). Shows the three latest lab posts as official LinkedIn embeds; their URNs are in `misc.linkedin_posts` (newest first). To update, take the URNs from the lab page's admin posts list (Gaia signs in to LinkedIn in the browser pane). The header LinkedIn icon still points to Gaia's personal profile.
- Tibetan lakes paper summary drafted by Claude at Gaia's request. Awaiting her approval or edits.
- CV link (done). The Contact page links to `assets/cv.pdf`, the public CV built in the CV Project (no funding amounts, no pending grants, no phone). To update it, rebuild `cv-public.pdf` there and copy it over `assets/cv.pdf`. The CV source is kept out of this public repository.
- Mauricio is listed as a postdoc for 2025–2026 and will move to alumni when Gaia says so.
