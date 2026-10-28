"""Build the portfolio from reviewed content and a pinned analytics repository."""
from pathlib import Path
import argparse, csv, hashlib, html, json, re, shutil, zipfile
from copy_refinement import refine_visitor_text

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
esc = html.escape
BASE = 'https://github.com/Pratattack/analytics-portfolio/tree/main/'

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--projects-source', type=Path, required=True)
    args = parser.parse_args()
    repo = args.projects_source.resolve()
    records = json.loads((ROOT / 'content/projects.json').read_text())
    registry = json.loads((repo / 'portfolio_registry.json').read_text())
    assert {p['path'] for p in registry}.issubset({p['path'] for p in records})
    assert all((repo / p['path'] / 'README.md').exists() for p in records)
    homepage = (DIST / 'index.html').read_text()
    header = re.search(r'<header>.*?</header>', homepage, re.S).group()
    header = header.replace('href="#main"', 'href="/"').replace('href="#work"', 'href="/#work"').replace('href="#about"', 'href="/#about"').replace('href="#contact"', 'href="/#contact"').replace('src="assets/', 'src="/assets/')
    header = header.replace('<a href="/#work">Work</a>', '<a href="/#work">Work</a><a href="/projects/">Library</a>')
    footer = re.search(r'<footer\b[^>]*>.*?</footer>', homepage, re.S).group().replace('href="assets/', 'href="/assets/').replace('href="#main"', 'href="#main"')
    def shell(title, description, canonical, body, extra=''):
        return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Prathamesh Singh</title><meta name="description" content="{esc(description, quote=True)}"><meta name="theme-color" content="#090f17"><link rel="canonical" href="https://prathameshsingh.com{canonical}"><meta property="og:title" content="{esc(title, quote=True)} | Prathamesh Singh"><meta property="og:description" content="{esc(description, quote=True)}"><meta property="og:type" content="website"><link rel="icon" href="/assets/mark.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css"></head><body><a class="skip" href="#main">Skip to content</a>{header}<main id="main">{body}</main>{footer}{extra}</body></html>'''
    for p in records:
        slug = p['slug']
        src = repo / p['path']
        dest = DIST / 'demos' / slug
        # Keep the original reports and scripts intact, including linked CSV evidence.
        if p.get('externalDemo'):
            shutil.copytree(src, dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '*.sqlite', '*.db', '.gitignore'))
        else:
            shutil.copytree(src / 'outputs', dest / 'outputs', dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns('*.sqlite', '*.db', '__pycache__'))
        for doc in src.glob('*.md'):
            shutil.copy2(doc, dest / doc.name)
        # Older reports contain two links to files absent from the repository snapshot.
        # Adapt navigation only; retain every analytical value and application script.
        report_file = dest / 'outputs/report.html'
        report_text = report_file.read_text() if report_file.exists() else ''
        if slug == 'bank-deposit-cost-attribution':
            report_text = report_text.replace('href="bank_cost_bridge.csv">Bank bridges', 'href="review_queue.csv">Bank review queue')
        if slug == 'airline-delay-intervention-screen':
            report_text = report_text.replace('href="source_audited_peer_rows.csv.gz">Source lineage and peers', 'href="' + BASE + p['path'] + '">Source data and methods on GitHub')
        if report_text:
            report_file.write_text(report_text)
        for hosted in dest.rglob('*'):
            if hosted.suffix in {'.html', '.js', '.svg', '.md', '.txt'}:
                original = hosted.read_text()
                revised = refine_visitor_text(original)
                if revised != original:
                    hosted.write_text(revised)
        (DIST / 'downloads').mkdir(exist_ok=True)
        package = DIST / 'downloads' / f'{slug}.zip'
        with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED) as z:
            for file in sorted(dest.rglob('*')):
                if file.is_file():
                    z.write(file, f'{slug}/' + str(file.relative_to(dest)))
        screenshot = next(iter((src / 'screenshots').glob('desktop-app.*')), None)
        p['screenshot'] = None
        if screenshot:
            name = slug + screenshot.suffix
            shutil.copy2(screenshot, DIST / 'assets' / name)
            p['screenshot'] = '/assets/' + name
        app = 'app.html' if (dest / 'outputs/app.html').exists() else ('workbench.html' if (dest / 'outputs/workbench.html').exists() else None)
        p['demo'] = p.get('externalDemo') or (f'/demos/{slug}/outputs/{app}' if app else None)
        p['report'] = BASE + p['path'] + '/docs/executive_memo.md' if p.get('externalDemo') else f'/demos/{slug}/outputs/report.html'
        p['download'] = f'/downloads/{slug}.zip'
        p['url'] = f'/projects/{slug}/'
        p['repository'] = BASE + p['path']
        p['delivery'] = 'External dashboard' if p.get('externalDemo') else ('Interactive workbench' if app else 'Analytical report')
        sections = [('Finding', p['findings']), ('Why it matters', p['implications']),
                    ('Who could use this', p['audience']), ('Data and scope', p['data'])]
        overview = ''.join(f'<section class="case-section" id="section-{i}"><h2>{esc(label)}</h2><p>{esc(text)}</p></section>' for i, (label,text) in enumerate(sections))
        overview += f'<details class="case-methods"><summary>How the analysis works</summary><p>{esc(p["methods"])}</p></details>'
        overview += f'<section class="case-section case-limits"><h2>Limits of the evidence</h2><p>{esc(p["limitations"])}</p></section>'
        demo = f'<a class="button" href="{p["demo"]}" target="_blank" rel="noopener">Open {"external dashboard" if p.get("externalDemo") else "workbench"} <span aria-hidden="true">↗</span></a>' if p['demo'] else f'<a class="button" href="{p["report"]}" target="_blank" rel="noopener">Open analytical report <span aria-hidden="true">↗</span></a>'
        image = f'<figure class="case-screenshot"><img src="{p["screenshot"]}" alt="Published desktop screenshot of the {esc(p["shortTitle"], quote=True)} research workbench" loading="lazy"><figcaption>Original project screenshot. The workbench link opens the interactive version.</figcaption></figure>' if p['screenshot'] else ''
        related = [x for x in records if x['slug'] != slug and x['category'] == p['category']][:2]
        related_links = ''.join(f'<a href="/projects/{x["slug"]}/">{esc(x["shortTitle"])} <span aria-hidden="true">↗</span></a>' for x in related)
        body = f'''<div class="wrap case-page"><a class="backlink" href="/projects/">← All projects</a><div class="case-heading"><p class="eyebrow">{esc(p['category'])} · {esc(p['dataKind'])}</p><h1>{esc(p['question'])}</h1><p class="case-lead">{esc(p['summary'])}</p><p class="case-subtitle">{esc(p['title'])} · Added {p['date']}</p><div class="case-actions">{demo}<a class="textlink" href="{p['repository']}" target="_blank" rel="noopener">Code & source documentation ↗</a></div><p class="delivery-note">Independent portfolio research. {'A interactive workbench runs in your browser using the project’s pinned data.' if app else 'This project includes an analytical report rather than an interactive application.'} Scenario assumptions are separate from observed results.</p></div><div class="case-grid"><article>{overview}{image}</article><aside class="case-aside"><p class="eyebrow">Project files</p><a href="{p['report']}" target="_blank" rel="noopener">Original analytical report ↗</a><a href="{p['repository']}" target="_blank" rel="noopener">Code and documentation ↗</a><a href="{p['download']}" download>Download {'workbench & report' if app else 'report & outputs'} ↓</a><p>Extract the ZIP before opening the HTML. For Python reproduction, clone the full repository so shared toolkits are retained.</p><p class="eyebrow aside-label">Tools & approach</p><div class="skills"><span>Python</span><span>SQL</span><span>{esc(p['category'])}</span></div><p class="eyebrow aside-label">Related work</p>{related_links}</aside></div><div class="case-bottom"><a class="textlink" href="/projects/">Explore the complete library ↗</a><a class="textlink" href="/#contact">Get in touch ↗</a></div></div>'''
        if p.get('externalDemo'):
            body = body.replace('This project includes an analytical report rather than an interactive application.', 'The Python dashboard is hosted on Render and may take time to start. Its current availability is not verified. Download the source to run it locally.')
            body = body.replace('Download report & outputs', 'Download Python dashboard source')
            body = body.replace('Extract the ZIP before opening the HTML.', 'Extract the ZIP and follow the project README to run the Python dashboard.')
            body = body.replace('Original analytical report', 'Original executive memo')
        write(DIST / 'projects' / slug / 'index.html', shell(p['shortTitle'], p['question'], p['url'], body))
    def row(p, i):
        return f'''<article class="library-row" data-slug="{p['slug']}"><span class="row-marker" aria-hidden="true">↗</span><div><p class="eyebrow">{esc(p['category'])} <span>/</span> {esc(p['dataKind'])}</p><h2><a href="{p['url']}">{esc(p['shortTitle'])} <span aria-hidden="true">↗</span></a></h2><p class="row-question">{esc(p['summary'])}</p></div><div class="row-meta"><span>{p['delivery']}</span><time datetime="{p['date']}">{p['date']}</time></div></article>'''
    rows = ''.join(row(p,i) for i,p in enumerate(records))
    library = f'''<section class="wrap library-page"><div class="library-heading"><p class="eyebrow">Economics, finance and operations</p><h1>Project library</h1><p>{len(records)} independent projects. Browse the findings, inspect the code or open a workbench. Public records and simulated data are labeled separately.</p></div><form class="filters" id="filters" role="search"><div class="search-field"><label for="search">Search projects</label><input type="search" id="search" name="search" placeholder="Try mortgages, forecasting or Python" autocomplete="off"></div><div><label for="category">Subject</label><select id="category" name="category"><option value="all">All areas</option><option>Finance</option><option>Research</option><option>Forecasting</option><option>Operations</option></select></div><div><label for="data-kind">Data</label><select id="data-kind" name="data"><option value="all">All data types</option><option>Public data</option><option>Public + assumptions</option><option>Simulation</option></select></div><button class="filter-reset" type="reset">Reset filters</button></form><noscript><p>All projects are shown below. Enable JavaScript to use search and filters.</p></noscript><div class="result-line"><p id="result-count" role="status" aria-live="polite" aria-atomic="true">{len(records)} projects</p><p>Public sources and simulations are labeled separately.</p></div><div id="project-results">{rows}</div><div class="no-results" id="no-results" hidden><h2>No projects match those filters.</h2><p>Try a broader term or clear the filters.</p><button id="clear-search" class="button" type="button">Show all projects</button></div></section>'''
    write(DIST / 'projects/index.html', shell('Project library', 'Explore independent research projects in economics, finance, forecasting and operations.', '/projects/', library, '<script src="/assets/projects-data.js"></script><script src="/assets/library.js"></script>'))
    write(DIST / 'assets/projects-data.js', 'const portfolioProjects = ' + json.dumps(records,ensure_ascii=False) + ';\n')
    write(ROOT / 'content/published-projects.json', json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    # Homepage keeps the approved composition, now linking to standalone case studies.
    homepage = re.sub(r'<p class="preview-note">.*?</p>', '', homepage)
    mapping = {'utility':'utility-reliability-due-diligence','mortgage':'houston-mortgage-price-comparability','mobility':'02-bike-share-forecast-planning','credit':'credit-spread-recession-audit'}
    for key, slug in mapping.items():
        homepage = re.sub(r'<button class="case-button" data-case="'+key+r'">(.*?)</button>',r'<a class="case-button" href="/projects/'+slug+r'/">\1</a>',homepage)
    homepage = re.sub(r'<div class="library">.*?</details></div>', '<div class="library"><p>More questions across banking, insurance, real estate and operations.</p><a class="textlink" href="/projects/">Explore all 18 projects <span class="arrow" aria-hidden="true">↗</span></a></div>', homepage, flags=re.S)
    homepage = re.sub(r'<dialog.*?</dialog>', '', homepage, flags=re.S)
    homepage = re.sub(r'<script src="assets/content.js"></script>\s*<script>.*?</script>', '', homepage, flags=re.S)
    if 'href="/projects/">Library' not in homepage:
        homepage = homepage.replace('<a href="#work">Work</a>', '<a href="#work">Work</a><a href="/projects/">Library</a>')
    if 'rel="canonical"' not in homepage:
        homepage = homepage.replace('</head>', '<link rel="canonical" href="https://prathameshsingh.com/"><meta property="og:title" content="Prathamesh Singh | Economics & Business Analysis"><meta property="og:description" content="Independent research on business costs, financial risk, forecasting and the limits of public data."><meta property="og:type" content="website"></head>')
    homepage = re.sub(r'Explore all \d+ projects', f'Explore all {len(records)} projects', homepage)
    write(DIST / 'index.html', homepage)
    write(DIST / '404.html', shell('Page not found', 'This page could not be found.', '/404.html', '<section class="wrap missing"><p class="eyebrow">404 / Page not found</p><h1>This page could not be found.</h1><p>This address may have changed.</p><a class="button" href="/projects/">Explore projects ↗</a></section>'))
    paths = ['/', '/projects/'] + [p['url'] for p in records]
    write(DIST / 'sitemap.xml','<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://prathameshsingh.com'+x+'</loc></url>' for x in paths)+'</urlset>')
    write(DIST / 'robots.txt', 'User-agent: *\nAllow: /\nDisallow: /demos/\nDisallow: /downloads/\nSitemap: https://prathameshsingh.com/sitemap.xml\n')
    (DIST/'assets/content.js').unlink(missing_ok=True)
    (ROOT/'inline-script-check.js').unlink(missing_ok=True)
    print(json.dumps({'case_studies':len(records),'interactive_workbenches':sum(bool(p['demo']) for p in records),'reports':len(records),'download_packages':len(records)}))

if __name__ == '__main__':
    main()
