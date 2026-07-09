# SolarFlow - Solar Simulation Frontend

A professional **cinematic React frontend** for the Solar Simulation & Intelligence Platform with a **Railway System Concept** design. Features realistic energy flow visualization, cable temperature effects, and immersive sound design.

## 🚆 Design Concept

The UI is inspired by railway/metro system maps, SCADA systems, and flight simulators:
- Each solar component = a "station/node"
- Energy flow = "railway track" with animated particles
- System behavior = "moving flow" with dynamic responses
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
   - **Cinematic simulation canvas** with real-time visualization
   - **Energy flow particles** animated along cables
   - **Cable temperature visualization** (blue → orange → red)
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

### Cinematic Components

- **CinematicSimulationCanvas** - Main simulation visualization
  - Animated energy flow particles
  - Cable temperature/stress visualization
  - Node status indicators
  - Real-time metrics panel
  
- **SimulationAlertSystem** - Educational alert overlays
  - Warning explanations
  - Root cause analysis
  - Recommendations
  - Key learnings
  
- **SoundEngine** - Immersive audio
  - Ambient electrical hum
  - Energy flow sounds
  - Warning/critical alerts
  - Interaction sounds

## 🛠️ Tech Stack

- **React 18** with TypeScript
- **Vite** for build tooling
- **TailwindCSS** for styling
- **Framer Motion** for animations
- **React Three Fiber** (optional for 3D mode)
- **React Router** for navigation
- **Zustand** for state management
- **TanStack Query** for API calls
- **Recharts** for data visualization
- **Howler.js** for sound engine
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

### Cable States

- **Normal** (blue) - Operating within limits
- **Heating** (orange) - Approaching max capacity
- **Critical** (red) - Overloaded, may fail

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

## 🎥 Cinematic Features

### Energy Flow System
- Particles flow along cables based on current load
- Speed increases with power demand
- Instability visualization during overload

### Cable Temperature System
- Color shifts based on temperature
- Thickness reflects current rating
- Heat indicators on stressed cables

### Sound Design
- Ambient electrical hum
- Dynamic energy flow sounds
- Warning beeps for stress conditions
- Critical alerts for failures

### Educational Overlays
- Every alert includes explanation
- Root cause analysis
- Recommendations
- Key learnings for users

## 📱 Responsive

The design is fully responsive and works on:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (320px - 767px)

## 🚀 Future Enhancements

- [ ] React Flow integration for custom railway layouts
- [ ] 3D visualization mode
- [ ] Real-time WebSocket simulation updates
- [ ] Voice assistant integration
- [ ] Export to PDF reports
- [ ] Multi-system comparison view
