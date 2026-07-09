# SolarFlow - Solar Simulation Frontend

A professional React frontend for the Solar Simulation & Intelligence Platform with a **Railway System Concept** design.

## 🚆 Design Concept

The UI is inspired by railway/metro system maps:
- Each solar component = a "station/node"
- Energy flow = "railway track"
- System behavior = "moving flow"
- Failures = "alerts on the track"

## ✨ Features

### Pages

1. **Dashboard** (`/`)
   - System health overview
   - Quick actions
   - Recent simulations
   - System alerts

2. **Products** (`/products`)
   - Product catalog with filtering
   - Grid and list view modes
   - Verified badge display
   - Spec previews

3. **Simulation Builder** (`/simulate`)
   - Interactive railway visualization
   - Component selection
   - Configuration sliders
   - Real-time parameter updates

4. **Simulation Results** (`/simulate/results`)
   - Summary cards with key metrics
   - Energy production/consumption charts
   - Battery health timeline
   - Event feed
   - Recommendations
   - AI chat panel

5. **History** (`/history`)
   - Past simulation results
   - Filtering and search
   - Statistics overview

### Components

- **RailwayNode** - Interactive system component nodes
- **RailwayFlow** - Animated energy flow visualization
- **AIChatPanel** - AI assistant for explanations
- **EventFeed** - Timeline of simulation events
- **ProductCard** - Product display cards

## 🛠️ Tech Stack

- **React 18** with TypeScript
- **Vite** for build tooling
- **TailwindCSS** for styling
- **Framer Motion** for animations
- **React Router** for navigation
- **Zustand** for state management
- **TanStack Query** for API calls
- **Recharts** for data visualization
- **Lucide React** for icons

## 🎨 Design System

### Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Background | `#0B0F14` | Main background |
| Primary | `#3B82F6` | Electric Blue |
| Solar | `#F59E0B` | Solar Yellow |
| Success | `#10B981` | Green |
| Warning | `#F97316` | Orange |
| Danger | `#EF4444` | Red |

### Node States

- **Normal** (blue) - Default operating state
- **Optimal** (green) - Performing above expectations
- **Warning** (orange) - Attention needed
- **Failure** (red) - Critical issue detected

## 📦 Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## 🔌 API Integration

The frontend connects to the backend at `/api`:

- `GET /products` - Fetch product catalog
- `POST /simulate/` - Run simulation
- `POST /ai/explain` - Get AI explanation
- `POST /ai/diagnose` - Get system diagnosis
- `POST /ai/recommend` - Get recommendations

## 🎥 Animations

The UI uses Framer Motion for:
- Page transitions
- Component hover effects
- Energy flow particles
- Node status indicators
- Chat message animations

## 📱 Responsive

The design is fully responsive and works on:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (320px - 767px)

## 🚀 Future Enhancements

- [ ] React Flow integration for custom railway layouts
- [ ] Real-time simulation updates
- [ ] 3D system visualization
- [ ] Voice assistant integration
- [ ] Export to PDF reports
