# MeetingAssassin - AI Productivity Agent

A modern Next.js 15 application showcasing an AI-powered productivity agent designed for meeting optimization and calendar management. Built for hackathon demonstration with impressive visuals and cutting-edge frontend technology.

## 🚀 Features

### Core Functionality
- **Real-time Dashboard** - Overview of productivity metrics and AI insights
- **Calendar Optimizer** - AI-powered calendar optimization with visual scheduling
- **Meeting Analysis** - Deep insights into meeting effectiveness and recommendations
- **AI Avatar Control** - Manage AI assistant capabilities and personality settings
- **Productivity Analytics** - Advanced charts and metrics with animated visualizations
- **Time Tracking** - Monitor time allocation and productivity patterns

### Technical Highlights
- **Next.js 15** with App Router and React Server Components
- **TypeScript** for type safety
- **Tailwind CSS** for styling with custom animations and glassmorphism effects
- **shadcn/ui** components for consistent, modern UI
- **Framer Motion** for smooth animations and micro-interactions
- **Recharts** for interactive data visualizations
- **WebSocket integration** for real-time updates
- **Responsive design** optimized for all devices

## 🎨 Visual Design

The application features a modern design system with:
- **Glassmorphism effects** with backdrop blur and transparency
- **Gradient backgrounds** and animated elements
- **Smooth animations** and transitions using Framer Motion
- **Dark/Light mode** support
- **Interactive charts** with hover effects and tooltips
- **Responsive sidebar** navigation
- **Floating action buttons** and micro-interactions

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js 15 App Router pages
│   │   ├── avatar/             # AI Avatar management page
│   │   ├── calendar/           # Calendar optimization page
│   │   ├── meetings/           # Meeting analysis page
│   │   ├── productivity/       # Productivity dashboard page
│   │   ├── time/              # Time tracking page
│   │   └── layout.tsx         # Root layout
│   ├── components/            # React components
│   │   ├── avatar/           # AI avatar control components
│   │   ├── calendar/         # Calendar optimization components
│   │   ├── dashboard/        # Dashboard overview components
│   │   ├── layout/           # Layout components (sidebar, header)
│   │   ├── meetings/         # Meeting analysis components
│   │   ├── productivity/     # Productivity metrics components
│   │   └── ui/              # shadcn/ui components
│   ├── contexts/             # React contexts
│   │   └── socket-context.tsx # WebSocket context
│   └── lib/                  # Utilities and configurations
│       ├── socket.ts         # WebSocket client
│       └── utils.ts          # Utility functions
└── package.json
```

## 🛠 Technologies Used

### Frontend Framework
- **Next.js 15** - React framework with App Router
- **React 19** - Latest React features and concurrent rendering
- **TypeScript** - Type safety and developer experience

### Styling & UI
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Modern React components
- **Framer Motion** - Animation library
- **Custom CSS** - Glassmorphism and advanced animations

### Data Visualization
- **Recharts** - React charting library
- **Custom Charts** - Productivity metrics and analytics
- **Interactive Elements** - Hover effects and tooltips

### Real-time Features
- **Socket.io Client** - WebSocket connection for live updates
- **React Context** - State management for real-time data

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd meeting-assassin/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Open in browser**
   ```
   http://localhost:3000
   ```

## 📊 Demo Features

### Dashboard Overview
- Real-time productivity metrics
- AI activity feed
- Quick action buttons
- Today's optimized schedule
- System status indicators

### Calendar Optimizer
- Visual calendar grid with time slots
- Drag-and-drop meeting scheduling
- AI optimization suggestions
- Conflict resolution
- Settings panel for preferences

### Meeting Analysis
- Meeting effectiveness scores
- Engagement metrics
- AI-powered recommendations
- Trend analysis over time
- Interactive charts and graphs

### AI Avatar Control
- Personality customization sliders
- Capability toggles
- Performance monitoring
- System resource usage
- Real-time status updates

### Productivity Dashboard
- Weekly productivity trends
- Time distribution charts
- Performance radar
- Goal tracking with progress bars
- AI insights and recommendations

## 🎯 Hackathon Demo Points

1. **Visual Impact** - Modern glassmorphism design with smooth animations
2. **Technical Sophistication** - Next.js 15, TypeScript, advanced React patterns
3. **Real-time Features** - WebSocket integration for live updates
4. **Data Visualization** - Interactive charts and productivity analytics
5. **Mobile Responsive** - Works perfectly on all devices
6. **Performance** - Optimized for speed with modern build tools

## 🔧 Development

### Build for Production
```bash
npm run build
```

### Lint Code
```bash
npm run lint
```

### Type Check
```bash
npx tsc --noEmit
```

## 📈 Future Enhancements

- Integration with calendar APIs (Google Calendar, Outlook)
- Machine learning models for meeting analysis
- Voice commands and natural language processing
- Advanced time tracking with project categorization
- Team collaboration features
- Mobile app companion

## 🏆 Hackathon Ready

This application is designed to impress hackathon judges with:
- **Cutting-edge technology stack**
- **Beautiful, modern UI design**
- **Smooth animations and interactions**
- **Comprehensive feature set**
- **Professional code organization**
- **Responsive and accessible design**

Perfect for demonstrating modern frontend development skills and innovative AI-powered productivity solutions.