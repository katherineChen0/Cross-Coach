# CrossCoach Frontend

A modern React application built with TypeScript, TailwindCSS, and Recharts for tracking personal development across multiple domains.

## Features

### Authentication
- **Login/Register Pages**: Clean, modern authentication forms with email/password
- **JWT Token Management**: Secure token storage in localStorage with automatic API header injection
- **Protected Routes**: Automatic redirection for authenticated/unauthenticated users

### Dashboard
- **Log Entry Form**: Comprehensive form with domain dropdown, metric selection, value input, and notes
- **Journal Entry**: Free-form textarea for daily reflections and thoughts
- **Chart Visualizations**: Multiple chart types using Recharts:
  - Line charts for progress over time
  - Pie charts for activity distribution
  - Bar charts for recent activity
- **Insights Feed**: AI-powered insights and correlation analysis displayed in cards
- **Recent Activity Table**: Clean table view of recent logs

### Design
- **Clean Grid Layout**: Responsive grid-based design with proper spacing
- **Rounded Cards**: Modern card design with soft shadows
- **TailwindCSS**: Utility-first CSS framework for consistent styling
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Tech Stack

- **React 18** with TypeScript
- **React Router DOM** for navigation
- **TailwindCSS** for styling
- **Recharts** for data visualization
- **Axios** for API communication
- **Vite** for build tooling

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## API Integration

The app integrates with the CrossCoach backend API:

- **Authentication**: `/api/auth/login`, `/api/auth/register`, `/api/auth/me`
- **Logs**: `/api/logs` (GET, POST)
- **Insights**: `/api/insights` (GET)

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Project Structure

```
src/
├── components/
│   ├── AuthContext.tsx      # Authentication context and JWT management
│   ├── LogEntryForm.tsx     # Form for logging entries
│   ├── JournalEntry.tsx     # Journal entry component
│   ├── Charts.tsx          # Chart visualizations
│   └── InsightsFeed.tsx    # Insights and correlations display
├── pages/
│   ├── LoginPage.tsx       # Login form
│   ├── RegisterPage.tsx    # Registration form
│   └── DashboardPage.tsx   # Main dashboard
├── App.tsx                 # Main app with routing
└── main.tsx               # App entry point
```

## Features in Detail

### Log Entry Form
- Domain selection (fitness, climbing, coding, mood, sleep, etc.)
- Dynamic metric names based on selected domain
- Numeric value input with validation
- Optional notes field
- Real-time form validation

### Charts
- **Progress Over Time**: Line chart showing trends across domains
- **Activity Distribution**: Pie chart showing domain breakdown
- **Recent Activity**: Bar chart of recent log entries
- Responsive design that adapts to screen size

### Insights Feed
- **AI Coach Insights**: Personalized recommendations based on data patterns
- **Correlation Analysis**: Statistical correlations between different metrics
- **Weekly Summaries**: AI-generated summaries of weekly progress
- **Quick Stats**: Overview of analyzed data and patterns

### Authentication Flow
- JWT tokens stored in localStorage
- Automatic token refresh and validation
- Protected routes with loading states
- Clean login/register forms with error handling

## Development

The app uses modern React patterns:
- Functional components with hooks
- TypeScript for type safety
- Context API for state management
- Custom hooks for reusable logic
- Responsive design principles 