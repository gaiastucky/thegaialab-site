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
- Galleries are collages of rectangles in different sizes. No uniform grids.

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
- Set up the preview site on GitHub Pages and later switch the domain.
- Mars globe for the Resources page with planetary DEMs. Caption wording and resolution to confirm with Gaia (she wrote 18 m/px, MOLA is about 463 m/px).
- Home page section "Follow us on LinkedIn" with the latest lab post. Needs the post link or embed code and which profile to link.
- Summary for the Tibetan lakes (endorheic) paper. Needs text from Gaia.
- Year of Deepali Singh's visit.
- CV link. Current link points to the 2022 PDF. Proposed approach is a public version from Overleaf with a `\newif\ifpublic` switch, published at a fixed `cv.pdf` path.
- Funding sheet. The Contact page ("Postdoctoral research" bubble) links to Gaia's Google Sheet of funding sources. Confirm it is shared as "anyone with the link can view".
- Mauricio is listed as a postdoc for 2025–2026 and will move to alumni when Gaia says so.
