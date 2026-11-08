# Frontend

Angular app (standalone components, signals): web app, admin console and embeddable website widget.
Not scaffolded yet. CI skips the frontend job until `frontend/package.json` exists.

Scaffold with:
```bash
npx @angular/cli@latest new web --directory . --standalone --routing --style=scss --ssr=false
```
