# Bin Butler

Installable Elmbridge bin collection web app.

## Daily schedule refresh

The GitHub Actions workflow refreshes the council feed daily at 06:17 UTC and publishes the app through GitHub Pages. It can also be run manually from Actions.

1. In Settings → Secrets and variables → Actions, add a repository secret named `ELMBRIDGE_UPRN`, containing your council property reference.
2. In Settings → Pages, select **GitHub Actions** as the build and deployment source. Preserve the existing custom domain.
3. Run **Refresh and publish bin schedule** from Actions, and check that it succeeds.

The property reference is read only from the secret. It is never included in the schedule, source code, or normal logs. Public output contains dates and service types. Do not enable debug logging, publish raw council responses, or upload private fixtures.

The updater validates future dates before replacing the schedule. A failed refresh leaves the previous deployed app available; GitHub Actions records a failed run. Enable GitHub Actions failure notifications in your GitHub notification settings. Public repository scheduled workflows can be disabled after 60 days without repository activity; successful daily schedule commits keep this repository active.

Garden waste applies only if subscribed. This app does not send WhatsApp messages or verify any external reminder service.

## Preview

`python -m http.server 8080`

Serve over HTTPS for installation on an iPhone.
