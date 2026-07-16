# NPM Scripts Documentation

Complete reference for all available npm scripts in the frontend project.

## Development Scripts

### `npm run dev`
Starts the Next.js development server with hot reload.

**What it does:**
- Starts server on port 3000
- Enables fast refresh for code changes
- Provides source maps for debugging
- Shows compilation errors in browser

**Usage:**
```bash
npm run dev
# Visit http://localhost:3000
```

**Options:**
```bash
npm run dev -- -p 3001  # Run on different port
npm run dev -- -H 0.0.0.0  # Listen on all interfaces
```

---

## Production Scripts

### `npm run build`
Creates an optimized production build.

**What it does:**
- Compiles TypeScript to JavaScript
- Minifies and optimizes code
- Generates static files where possible
- Creates .next folder with build output
- Performs type checking

**Usage:**
```bash
npm run build
```

**Output:**
- `.next/` - Build output directory
- Build analysis in terminal output

**Troubleshooting:**
```bash
# Clear cache if build fails
rm -rf .next
npm run build
```

---

### `npm start`
Starts the production server (requires build first).

**What it does:**
- Starts Next.js server on port 3000
- Serves optimized production build
- Uses built-in compression
- Enables caching headers

**Usage:**
```bash
npm run build  # Build first
npm start      # Start server
# Visit http://localhost:3000
```

---

## Linting Scripts

### `npm run lint`
Runs ESLint to check code quality.

**What it does:**
- Checks JavaScript/TypeScript files
- Enforces Next.js best practices
- Reports style and error issues
- Can auto-fix some issues

**Usage:**
```bash
npm run lint
```

**Auto-fix issues:**
```bash
npx eslint --fix --ext .ts,.tsx components/ lib/ app/
```

---

## Advanced Scripts

### TypeScript Type Checking
```bash
# Check types without building
npx tsc --noEmit
```

### Bundle Analysis
```bash
# Analyze bundle size
npm run build
npx next-bundle-analyzer
```

### Performance Testing
```bash
# Test Lighthouse metrics
npx lighthouse http://localhost:3000
```

---

## Package Management

### Update Dependencies
```bash
# Check outdated packages
npm outdated

# Update packages
npm update

# Update specific package
npm install package-name@latest
```

### Add Dependencies
```bash
# Production dependency
npm install package-name

# Development dependency
npm install --save-dev package-name
```

---

## Docker Commands

### Build Docker Image
```bash
docker build -t code-smell-frontend .
```

### Run Docker Container
```bash
docker run -p 3000:3000 code-smell-frontend
```

---

## Useful Development Commands

### Clear Cache and Rebuild
```bash
npm run build && npm start
```

### Check Project Health
```bash
npm run lint && npm run build
```

### Development with debugging
```bash
NODE_OPTIONS='--inspect' npm run dev
```

---

## Environment-Specific Commands

### Development
```bash
npm run dev
```

### Staging
```bash
NEXT_PUBLIC_BACKEND_URL=https://staging-api.example.com npm run build
npm start
```

### Production
```bash
NEXT_PUBLIC_BACKEND_URL=https://api.example.com npm run build
npm start
```

---

## Continuous Integration

### GitHub Actions Example
```bash
# Install
npm ci

# Lint
npm run lint

# Build
npm run build

# (Optional) Run tests
npm test
```

---

## Quick Reference

| Command | Purpose | Environment |
|---------|---------|-------------|
| `npm run dev` | Development server | Dev |
| `npm run build` | Production build | All |
| `npm start` | Production server | Prod |
| `npm run lint` | Check code quality | Dev |

---

## Performance Tips

- Use `npm ci` instead of `npm install` in CI/CD for consistency
- Cache node_modules in CI/CD pipelines
- Use `.npmrc` for performance tweaks
- Consider using pnpm for faster installations

---

## Troubleshooting

### Port 3000 Already in Use
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :3000
kill -9 <PID>
```

### Module Not Found
```bash
rm -rf node_modules package-lock.json
npm install
```

### Build Cache Issues
```bash
rm -rf .next
npm run build
```

---

## Additional Resources

- [Next.js CLI Reference](https://nextjs.org/docs/app/api-reference/next-cli)
- [NPM Scripts Documentation](https://docs.npmjs.com/cli/run-script)
- [ESLint Configuration](https://eslint.org/docs/user-guide/configuring)

---

## Notes

- All scripts assume you're in the `frontend-nextjs` directory
- Development server runs on port 3000 (configurable)
- Production server also uses port 3000 by default
- Environment variables must be prefixed with `NEXT_PUBLIC_` to be accessible in browser
