# Ahmed Marzouk — Engineering & Design Educator

GitHub Pages export of the current local WordPress portfolio. The website is in `docs/`. WordPress remains the editing source.

## First publication using GitHub Desktop

1. Choose **File → Add Local Repository** and select this folder.
2. Choose **Publish repository**, name it `portfolio`, and turn off **Keep this code private** for free GitHub Pages hosting.
3. On the repository’s GitHub page, open **Settings → Pages**. Choose **Deploy from a branch**, branch **main**, folder **/docs**, then **Save**.
4. GitHub displays the live website URL after the deployment finishes.

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
