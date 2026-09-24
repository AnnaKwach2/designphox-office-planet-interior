# Office Planet Interior — QA and performance audit

## Executive summary

- Overall status: Ready with minor limitations
- Critical: 0
- High: 0
- Medium: 4 fixed
- Low: 3 fixed
- Primary business risk addressed: stale brand metadata and a 1.36 MB logo loaded repeatedly could weaken link sharing and slow every page.
- Recommended next action: publish this revision, validate the production social card, then migrate the verified build to GitHub and Vercel.

## Scope and environment

- Repository: static HTML/CSS/JavaScript site in `output/site-publish`
- Pages tested: homepage, services index, project form, and all six service pages
- Viewports: 390 × 844 and 1440 × 900 in the Codex in-app Chromium browser
- Critical journeys: primary navigation, service navigation, mobile menu, project form validation, WhatsApp links, and all local image/style/script references
- Exclusions: no real WhatsApp message was sent; external social accounts were not supplied; Vercel migration has not started

## Verification results

| Area | Result | Evidence |
| --- | --- | --- |
| Build and static integrity | Pass | 9 pages parsed; no missing local links, scripts, styles or images |
| User journeys | Pass | Mobile menu opened/closed; empty project form exposed both required-field messages |
| Responsive and visual | Pass | All 9 pages checked at 390px and 1440px; no horizontal overflow or broken images |
| Accessibility | Pass with manual scope | One H1 per page, labelled controls, skip links, alt text, focus styles and reduced-motion support verified |
| Performance | Improved | Repeated logo reduced from 1,357 KB to 12 KB; displayed photos reduced from 2,966 KB to 2,138 KB; responsive 720px sources added; icon-font dependency removed |
| SEO and sharing | Fixed | Correct Office Planet brand metadata, unique club-page metadata, canonical URLs, 1200 × 630 social card, favicon set |
| Production reliability | Pending publish verification | Local browser console showed no errors or warnings |
| Defensive security | Pass for static scope | No secrets, authentication logic, storage or backend endpoints in this static build |

## Findings

### [Medium] Stale company name in metadata

- Status: Fixed
- Affected pages: all pages
- Impact: WhatsApp/search previews identified the business as “Elegants Fittings.”
- Fix: replaced stale page titles, descriptions, Open Graph site name and social titles with Office Planet Interior.
- Verification: repository-wide search found no remaining stale brand reference.

### [Medium] Oversized repeated logo

- Status: Fixed
- Affected pages: all headers and footers
- Impact: a 1,357 KB source image was fetched to render a 58px logo.
- Fix: generated a 160px WebP derivative at 12 KB and updated every repeated brand image.
- Verification: all 9 pages load the optimized file with no broken images.

### [Medium] Weak WhatsApp preview asset

- Status: Fixed
- Affected pages: all shareable URLs
- Impact: a square logo was used instead of a landscape project preview, and Twitter requested a small summary card.
- Fix: created a 1200 × 630, 127 KB project card; added its absolute Open Graph and Twitter metadata; set `summary_large_image`.
- Verification: dimensions and metadata are present on every page.

### [Medium] Service hero images could shift the layout

- Status: Fixed
- Affected pages: all six service pages
- Impact: missing intrinsic dimensions could cause cumulative layout shift while images decoded.
- Fix: added correct width and height attributes and high fetch priority to service hero images.
- Verification: static audit reports no images without dimensions.

### [Low] Wrong service count in metadata

- Status: Fixed
- Affected page: services index
- Fix: changed “five specialist services” to six.

### [Low] Duplicate club-page metadata

- Status: Fixed
- Affected page: Club & Entertainment Spaces
- Fix: replaced restaurant fit-out metadata with club-specific title and description.

### [Low] Placeholder social links and render-blocking icon font

- Status: Fixed
- Affected pages: all footers
- Impact: Facebook, Instagram and X links opened generic network homepages; Font Awesome added an external CSS/font dependency only for those icons.
- Fix: retained the verified WhatsApp contact as text and removed the generic links and Font Awesome request.

### [Medium] Oversized mobile image downloads

- Status: Fixed
- Affected pages: homepage, services index, project form and all service pages
- Impact: phones could receive desktop-scale images even when the display area was much smaller.
- Fix: recompressed displayed WebP photographs without cropping, preserved every original aspect ratio, and added 720px responsive sources for larger images.
- Verification: displayed source images fell from 2,966 KB to 2,138 KB in aggregate. Representative mobile service hero files now range from 18.5 KB to 36 KB, down from 59 KB to 122 KB for their desktop sources.

## Remaining risks

- WhatsApp may cache an older preview for a previously shared exact URL. A new query string or the final Vercel domain will trigger a fresh fetch.
- Actual Facebook, Instagram and X business profile URLs were not provided, so they are intentionally omitted.
- Automated Lighthouse lab scoring was unavailable in the local browser integration; the critical static payload and browser console were inspected directly.
- The requested Vercel production deployment will be publicly accessible without a password. Preview protection can remain separate if desired.
