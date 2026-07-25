# Saint Frontend (Archived Compatibility Surface)

The terminal application is now Saint's primary product and deployment target. This frontend is retained for historical reference and compatibility only; new product work should target the Python CLI and Saint Core.

The frontend owns user interaction, goal input, intent selection, goal visualization, contextual path visualization, and Learn / Explore / Act experiences.

The frontend prototype uses React, Next.js, TypeScript, Tailwind, and CSS.

Run from this directory:

```powershell
npm install
npm run dev
```

Then open:

```text
http://127.0.0.1:5173
```

The frontend uses `http://127.0.0.1:8000` by default for the backend. Override it when needed:

```powershell
$env:NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
npm run dev
```

## Vercel deployment

Set the Vercel project root directory to `frontend`, then add this environment variable:

```text
NEXT_PUBLIC_API_BASE_URL=https://<your-render-service>.onrender.com
```

Deploy with the existing Next.js defaults. The backend must allow the deployed Vercel origin through its `FRONTEND_ORIGIN` environment variable.
