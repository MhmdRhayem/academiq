# AcademiQ Frontend

React-based frontend for the AcademiQ grade prediction system.

## Local Development

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create a `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

3. Update `VITE_API_URL` in `.env` to point to your backend:
   ```
   VITE_API_URL=http://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000)

## Build for Production

```bash
npm run build
```

This creates a `dist/` folder with optimized static files ready for deployment.

## Deployment

### Deploy to Vercel

1. Push this code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import your repository
4. Vercel will auto-detect Vite configuration
5. Add environment variable: `VITE_API_URL=https://your-koyeb-backend.koyeb.app`
6. Deploy

### Deploy to Netlify

1. Push this code to GitHub
2. Go to [netlify.com](https://netlify.com)
3. Import your repository
4. Build command: `npm run build`
5. Publish directory: `dist`
6. Add environment variable: `VITE_API_URL=https://your-koyeb-backend.koyeb.app`
7. Deploy