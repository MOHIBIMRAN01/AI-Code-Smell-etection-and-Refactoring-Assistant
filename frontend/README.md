# Code Smell Detector - Frontend

Modern Next.js frontend for the AI-powered Code Smell Detection and Refactoring Assistant.

## Features

✨ **Modern UI/UX**
- Clean, responsive design with Tailwind CSS
- Dark mode support ready
- Smooth animations and transitions

🎯 **Core Features**
- Repository analysis form with validation
- Real-time analysis status
- Detailed findings with severity levels
- Refactoring suggestions
- Download reports (JSON & PDF)
- Analysis history with localStorage
- Interactive findings table with filtering and sorting

⚡ **Performance**
- Server-side rendering with Next.js
- Optimized bundle size
- Efficient state management
- Type-safe with TypeScript

## Prerequisites

- Node.js 18+ or newer
- npm or yarn
- Backend API running (default: http://localhost:8000)

## Installation

### 1. Install Dependencies

```bash
cd Frontend
npm install
```

Or with yarn:
```bash
yarn install
```

### 2. Setup Environment Variables

Copy `.env.example` to `.env.local` and update if needed:

```bash
cp .env.example .env.local
```

Configure the backend URL:
```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_REQUEST_TIMEOUT=120000
```

## Development

### Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Development Features
- Hot module reloading
- Fast refresh for instant updates
- TypeScript checking
- ESLint validation

## Project Structure

```
Frontend/
├── app/                      # Next.js app router
│   ├── page.tsx             # Home page
│   ├── analyze/             # Analysis page
│   ├── results/[id]/        # Results page
│   ├── layout.tsx           # Root layout
│   ├── globals.css          # Global styles
│   └── not-found.tsx        # 404 page
├── components/              # React components
│   ├── Button.tsx           # Button component
│   ├── Card.tsx             # Card layout component
│   ├── Badge.tsx            # Badge component
│   ├── Alert.tsx            # Alert component
│   ├── Loading.tsx          # Loading states
│   ├── Header.tsx           # App header
│   ├── Footer.tsx           # App footer
│   ├── RepositoryForm.tsx   # Analysis form
│   ├── FindingsTable.tsx    # Findings display
│   ├── FindingDetail.tsx    # Finding details
│   ├── StatCard.tsx         # Statistics card
│   ├── SeverityChart.tsx    # Severity distribution
│   ├── ErrorNotification.tsx# Error display
│   └── index.ts             # Component exports
├── context/                 # React Context
│   ├── AnalysisContext.tsx  # Analysis state
│   ├── ErrorContext.tsx     # Error handling
│   └── index.ts             # Context exports
├── lib/                     # Utility functions
│   ├── api.ts               # API client
│   ├── utils.ts             # Helper functions
│   └── hooks/               # Custom React hooks
│       ├── useAnalysis.ts   # Analysis hook
│       ├── useHealthCheck.ts# Health check hook
│       ├── useLocalStorage.ts# Storage hook
│       └── index.ts         # Hook exports
├── types/                   # TypeScript definitions
│   └── index.ts             # Type exports
├── package.json             # Dependencies
├── tsconfig.json           # TypeScript config
├── tailwind.config.ts      # Tailwind CSS config
├── postcss.config.js       # PostCSS config
├── next.config.js          # Next.js config
├── .eslintrc.json          # ESLint config
├── .env.example            # Environment template
└── .env.local              # Environment variables (local)
```

## API Integration

### Health Check
```typescript
await apiClient.healthCheck()
```

### Analyze Repository
```typescript
await apiClient.analyzeRepository({
  repository_url: 'https://github.com/user/repo',
  branch: 'main',
  analysis_label: 'v1.0'
})
```

### Download Reports
```typescript
await apiClient.downloadJsonReport(analysisId)
await apiClient.downloadPdfReport(analysisId)
```

## Custom Hooks

### useAnalysis
Manages analysis state and API calls
```typescript
const { data, loading, error, analyze, reset } = useAnalysis()
```

### useHealthCheck
Monitors backend health status
```typescript
const { isHealthy, checked, error } = useHealthCheck()
```

### useLocalStorage
Persists data to browser storage
```typescript
const [value, setValue] = useLocalStorage('key', initialValue)
```

## Context Providers

### AnalysisContext
Manages current analysis and history
```typescript
const {
  currentAnalysis,
  setCurrentAnalysis,
  analysisHistory,
  addToHistory,
  clearHistory,
  removeFromHistory
} = useAnalysisContext()
```

### ErrorContext
Handles global error notifications
```typescript
const { errors, addError, removeError, clearErrors } = useErrorContext()
```

## Building for Production

### Build
```bash
npm run build
```

### Start Production Server
```bash
npm start
```

### Optimize
The build process automatically:
- Minifies JavaScript and CSS
- Generates optimized images
- Creates source maps for debugging
- Optimizes React for production

## Deployment

### Vercel (Recommended)
```bash
npm install -g vercel
vercel
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Environment Variables for Production
- Set `NEXT_PUBLIC_BACKEND_URL` to your production backend
- Ensure CORS is configured on backend
- Use HTTPS in production

## Performance Optimization

### Code Splitting
- Automatic route-based code splitting
- Dynamic imports for heavy components

### Image Optimization
- Next.js Image component for optimization
- Automatic format conversion

### Caching
- Browser caching via headers
- localStorage for analysis history
- API response caching

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari 13+, Chrome Android latest

## Troubleshooting

### Backend Connection Issues
1. Verify backend URL in `.env.local`
2. Check if backend is running
3. Ensure CORS headers are set correctly
4. Check browser console for errors

### Build Errors
1. Clear `.next` directory: `rm -rf .next`
2. Clear node_modules: `rm -rf node_modules`
3. Reinstall: `npm install`
4. Rebuild: `npm run build`

### TypeScript Errors
1. Run type check: `npx tsc --noEmit`
2. Check `tsconfig.json` configuration
3. Ensure all types are properly imported

## Contributing

1. Follow the existing code style
2. Use TypeScript for type safety
3. Add comments for complex logic
4. Test components with different states
5. Follow the component structure patterns

## Performance Tips

- Use `React.memo` for expensive components
- Implement virtual scrolling for large lists
- Lazy load images and components
- Monitor bundle size with `npm run build`
- Use Next.js built-in optimizations

## Security

- All API calls use HTTPS in production
- Input validation on forms
- XSS protection via React
- CSRF protection via API design
- No sensitive data stored in localStorage

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
1. Check the backend API documentation
2. Review component prop types
3. Check browser console for errors
4. Verify environment configuration

## Future Enhancements

- [ ] Dark mode theme
- [ ] Advanced filtering and search
- [ ] Export to multiple formats
- [ ] Real-time analysis progress
- [ ] Comparison of multiple analyses
- [ ] Custom report templates
- [ ] Team collaboration features
- [ ] API key management
