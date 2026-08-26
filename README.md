# Bin Butler

Installable iPhone web app for the existing Elmbridge bin-reminder system.

Refresh its schedule from the workspace root:

```powershell
node scripts/elmbridge-bin-reminder.mjs --json | Set-Content -Encoding utf8 bin-app/data/schedule.json
```

Preview locally:

```powershell
python -m http.server 8080 --directory bin-app
```

The app must be served over HTTPS before installation on an iPhone.
