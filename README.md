# Ahmed Marzouk — Engineering & Design Educator

GitHub Pages export of the current local WordPress portfolio. The website is in `docs/`. WordPress remains the editing source.

Website: https://amarzoukportfolio.github.io/

Repository: https://github.com/amarzoukportfolio/amarzoukportfolio.github.io

## GitHub Pages configuration

The public repository belongs to the `amarzoukportfolio` organization. Pages publishes from branch **main**, folder **/docs**, with HTTPS enabled. Keep the repository name `amarzoukportfolio.github.io` to retain the website address.

In GitHub Desktop, choose **File → Add Local Repository** and select this folder if it is not already listed. The local repository’s origin points to the organization repository above.

## Update the website

1. Start `ahmed-portfolio` in the Local app.
2. Edit and publish your changes in WordPress, including the CV download when ready.
3. Double-click **Refresh portfolio.command** in this folder. It exports published pages and the public assets they reference, then checks links.
4. In GitHub Desktop, review the changes, enter a summary, choose **Commit to main**, then **Push origin**. GitHub Pages publishes the pushed update.

WordPress changes need this refresh and push to appear on GitHub Pages. GitHub cannot reach the WordPress site running on your Mac.

## Command-line checks

```sh
python3 scripts/export_site.py
python3 scripts/check_site.py
python3 -m http.server 8080 --directory docs
```

Open http://localhost:8080 for a local preview. The exporter needs Python 3 and a running local WordPress site, with no extra Python packages.

The export includes the current CV and portfolio PDF exactly as linked by WordPress. It excludes WordPress administration, configuration, databases, unused media, and the sample page. The former robot URL redirects to the student collection.
