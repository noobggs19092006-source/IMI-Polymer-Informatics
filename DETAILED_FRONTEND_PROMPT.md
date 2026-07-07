# 🔬 POLYMER INFORMATICS FRONTEND - DETAILED DEVELOPMENT PROMPT

**Project Level:** Internship  
**Status:** New Development (Replaces Streamlit Dashboard)  
**Target User:** Single-user research interface  
**Date Created:** 2026-06-01

---

## 📋 EXECUTIVE SUMMARY

You will build a **modern, interactive React-based frontend** for the Polymer Informatics pipeline that visualizes a complete scientific workflow: from combinatorial polymer generation through ANSYS simulations to ML model training and inverse design discovery. The interface will showcase the entire pipeline sequentially with sophisticated animations, real-time feedback mechanisms, and professional scientific visualizations.

**Key Differentiator:** This is NOT a real-time simulation monitor. Training/simulation is pre-completed. Users test pre-trained models, run inverse design searches, and explore optimized polymer candidates.

---

## 🎯 CORE FUNCTIONALITIES

### Phase 1: Pipeline Overview & Stepper Navigation
- **Sequential Phase Display** with animated stepper component
  - Phase 0: Environment Setup
  - Phase 1: ANSYS Maxwell 2D Simulation Campaign
  - Phase 2: ML Training (3-Way Ensemble: MLP + GBR + XGBoost)
  - Phase 3: Inverse Design & vHTS (Virtual High-Throughput Screening)
  - Phase 4: Advanced Upgrades (Pareto Front, GNN, VAE)
  - Phase 5: Reporting & Results

### Phase 2: Interactive Polymer Generation & Configuration
- **Backbone Selection** (10 types: PE, PP, PVC, PTFE, PVDF, Polystyrene, PMMA, Polycarbonate, PET, Nylon-6)
- **Functional Group Customization** (Left/Right groups with real-time SMILES generation)
- **Physical Parameters Configuration**
  - Dielectric Constant (eps)
  - Glass Transition Temperature (Tg)
  - Density
  - Thickness (nm)
  - Applied Voltage
  - Temperature

### Phase 3: Model Selection & Testing
- **Multi-Model Dashboard**
  - 3-Way Ensemble (MLP + GBR + XGBoost) → R² = 0.9558
  - Graph Neural Network (GNN) → R² = 0.9528
  - Variational Autoencoder (VAE) → Generative capabilities
- **Model Performance Metrics Display** with count-up animations
- **Model Comparison Interface**

### Phase 4: Inverse Design Discovery
- **Target Capacitance Input** (10-2000 pF/m)
- **Virtual Library Configuration**
  - Library size slider (1,000-25,000 candidates)
  - Thickness range constraints
  - Material family filters
- **Discovery Execution & Screening** (with progress animations)
- **Top-N Results Display** (Rank 1-6 candidates)

### Phase 5: Results Visualization & Analytics
- **Polymer Structure Rendering** (2D molecule visualizations via RDKit)
- **Performance Metrics** with count-up animations:
  - R² Score (Training & Cross-Validation)
  - Accuracy %
  - Number of Successful Simulations (551/1440)
  - MSE/RMSE
  - Cross-Fold Validation Scores
- **Comparative Analytics** (candidate ranking, deviation from target)
- **Downloadable Results** (JSON, CSV, molecule images)

---

## 🎨 UI/UX COMPONENT SPECIFICATIONS

### 1. **MENU STYLE** - Staggered Menu
**Source:** https://reactbits.dev/components/staggered-menu

**Implementation Details:**
- Primary navigation menu with staggered reveal animation
- Menu items appear sequentially with slight delays (50-100ms between each)
- Used for: Main navigation, phase selection, model switching
- Color scheme: Match the pixel snow background with contrasting text
- **Placement Options:**
  - Top hamburger menu for full pipeline overview
  - Side panel for phase-specific controls
  - Context menus for inline actions (e.g., molecule rendering, result actions)

**Functional Integration:**
- Main nav: Phase selection (0-5)
- Phase nav: Within each phase, staggered menu for sub-options
- Action menu: Model selection, export options, visualization toggles

---

### 2. **STEPPER ANIMATION** - Sequential Phase Display
**Source:** https://reactbits.dev/components/stepper

**Implementation Details:**
- Animated progress indicator showing 6 phases
- Current phase highlighted with smooth transitions
- Completed phases show checkmark with animation
- Upcoming phases grayed out
- Click on completed phases to view historical results
- Currently-executing phase shows spinning/pulsing animation (even though it's pre-computed, create the impression of active processing)

**Visual Specifications:**
- Step circles: 60px diameter
- Connecting lines between steps: Animated fill from left-to-right as phases complete
- Animation duration: 300-500ms per transition
- Colors:
  - Active/Current: Bright accent (e.g., #00D9FF or matching theme)
  - Completed: Green (#4CAF50) with checkmark
  - Upcoming: Light gray (#E0E0E0)
  - Connector lines: Gradient from completed to upcoming phases

---

### 3. **BACKGROUND ANIMATION** - Pixel Snow
**Source:** https://reactbits.dev/backgrounds/pixel-snow

**Implementation Details:**
- Full-viewport pixel snow effect as primary background
- Pixel density: Medium-to-high (adjustable for performance)
- Snow particle color: White or semi-transparent white (#FFFFFF, opacity 0.7-0.9)
- Background base: Dark blue or charcoal (#0F1419, #1A1A2E)
- Snow speed: Slow-to-medium (creates calm, scientific ambiance)
- Particle size: 2-4px squares (truly "pixel" style)
- Should NOT obscure content; slightly blurred/layered behind UI elements

**Performance Optimization:**
- Canvas-based rendering recommended (not DOM nodes)
- Limit particle count to maintain 60fps
- Provide GPU acceleration option

---

### 4. **TEXT ANIMATION** - Text Type Effect
**Source:** https://reactbits.dev/text-animations/text-type

**Implementation Details:**
- Used for: Page titles, phase descriptions, result highlights
- Typing speed: 50-100ms per character (adjustable)
- Cursor visible during typing (e.g., blinking "|")
- Animation triggers: Page load, phase transition, result generation
- Text to animate:
  - Main title: "🔬 Polymer Informatics Discovery Engine"
  - Phase descriptions: "Generating combinatorial polymer library..."
  - Result reveals: "Top Candidate: Predicted 199.8 pF/m"
  - Metric displays: Count-up numbers followed by typing unit label

**Color & Style:**
- Text color: High contrast (white on dark background)
- Font: Monospace or modern sans-serif (Inter, Space Mono, JetBrains Mono)
- Font weight: Bold for main titles, regular for descriptions

---

### 5. **CLICK ANIMATION** - Click Spark/Ripple Effect
**Source:** https://reactbits.dev/animations/click-spark

**Implementation Details:**
- Triggered on: Button clicks, card interactions, metric displays
- Effect: Radial burst of particles/sparks from click point
- Particle type: Small glowing dots or star-shaped particles
- Color: Match accent color (e.g., cyan, electric blue, or theme color)
- Duration: 400-600ms total animation
- Particle count: 8-16 sparks per click
- Spread radius: 100-150px from click origin
- Opacity: Fade from 1.0 to 0 (particles disappear)

**Use Cases:**
- "Run Discovery" button: Big spark burst on click
- Result cards: Subtle spark cluster when hovering/selecting
- Metric cards: Spark animation when count-up completes
- Model selection: Confirm selection with spark feedback

---

### 6. **BORDER ANIMATION** - Star Border
**Source:** https://reactbits.dev/animations/star-border

**Implementation Details:**
- Applied to: Card containers, result cards, active panels, metric displays
- Animation: Animated border with star-like trail effect
- Border color: Gradient or pulsing (e.g., cyan → purple → cyan)
- Border width: 2-3px
- Speed: 2-4 second loop (smooth, continuous)
- Effect style: Stars or particles moving along the border path

**Use Cases:**
- Active phase indicator: Border animation around current phase section
- Highlighted result card: Rank #1 result has animated star border
- Model card: Selected model displays star border
- Metric card: Stands out with animated border when value reaches threshold

**Pro Tip:** Can layer multiple star borders for emphasis (e.g., Rank #1 candidate)

---

### 7. **COUNT-UP ANIMATION** - Metric Display
**Source:** (Implement using a library like react-countup or custom solution)

**Key Metrics to Animate:**
1. **R² Score** (0 → 0.9558)
   - Format: ".0000"
   - Duration: 2-3 seconds
2. **Accuracy %** (0 → ~95-96%)
   - Format: "95.3%"
   - Duration: 2-3 seconds
3. **Successful Simulations** (0 → 551)
   - Format: "551 / 1440"
   - Duration: 2-3 seconds
4. **Model Performance Metrics** (MSE, RMSE, MAE)
   - Format: Varies (0.xxxx)
   - Duration: 2-3 seconds
5. **Cross-Validation Scores** (0 → 0.9073)
   - Format: ".0000"
   - Duration: 2-3 seconds

**Animation Style:**
- Easing: EaseOut or EaseInOut (smooth deceleration)
- Number increments: Rapid at start, slowing toward end
- Prefix/Suffix: Add labels (e.g., "R² = ", " pF/m", " samples")
- Trigger: On metric card entrance to viewport or phase completion
- Sound (optional): Subtle "level up" sound effect on completion

---

## 🏗️ SYSTEM ARCHITECTURE

### Frontend Stack (Recommended)
- **Framework:** React 18+ (TypeScript recommended for internship-level quality)
- **Build Tool:** Vite (fast development, optimized builds)
- **Styling:** Tailwind CSS + CSS Modules (for component-scoped animations)
- **Animation Library:** Framer Motion (handles complex sequential animations)
- **State Management:** Zustand or Context API (lightweight, sufficient for single-user)
- **HTTP Client:** Axios or Fetch API
- **Visualization:** Plotly.js or Chart.js (for metrics/analytics), RDKit-js for molecules (if client-side), or server-provided images
- **Icons:** React Icons (Feather or HeroIcons)

### Backend Stack (Recommended)
- **Framework:** FastAPI (Python, excellent scientific library ecosystem)
- **ORM/Database:** SQLite or PostgreSQL (for result caching)
- **Workers:** Celery + Redis (for long-running inverse design tasks)
- **ML Pipeline:** Joblib-loaded models (pre-pickled ensembles)
- **Chemistry:** RDKit (SMILES generation, molecule rendering)
- **API Docs:** Auto-generated OpenAPI (Swagger UI)

### Key API Endpoints
```
GET  /api/health                      # Health check
GET  /api/pipeline/phases             # Get all phases metadata
POST /api/polymer/generate            # Generate SMILES from config
POST /api/model/predict               # Single or batch prediction
POST /api/inverse-design/search       # Virtual library screening
GET  /api/results/{task_id}           # Fetch task results
GET  /api/metrics/summary             # Training metrics & stats
POST /api/molecules/render            # Render 2D structure image
```

---

## 📐 LAYOUT & WIREFRAME

### Main Dashboard Layout (Recommended)

```
┌─────────────────────────────────────────────────────────────────┐
│  🔬 POLYMER INFORMATICS DISCOVERY ENGINE                    ⚙️ │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Phase Stepper (Horizontal):                                    │
│  [0]──[1]──[2]✓──[3]➤──[4]──[5]  (animated, interactive)       │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│                      MAIN CONTENT AREA                           │
│                                                                   │
│  ┌─ Left Sidebar (35%) ─────┐  ┌─ Main Panel (65%) ────────┐   │
│  │                          │  │                            │   │
│  │ Navigation Menu          │  │ Current Phase Content      │   │
│  │ (Staggered):             │  │ (Dynamic based on phase)   │   │
│  │ • Phase Overview         │  │                            │   │
│  │ • Data Generation        │  │ ┌──────────────────────┐  │   │
│  │ • Simulation Config      │  │ │ Polymer Generator    │  │   │
│  │ • Model Selection        │  │ │ [Backbone Selector]  │  │   │
│  │ • Inverse Design         │  │ │ [Group Selectors]    │  │   │
│  │ • Results & Analytics    │  │ │ [Parameters Sliders] │  │   │
│  │                          │  │ │ [Run Button] ✨       │  │   │
│  │                          │  │ └──────────────────────┘  │   │
│  │                          │  │                            │   │
│  │                          │  │ ┌──────────────────────┐  │   │
│  │                          │  │ │ Results Grid (3-col) │  │   │
│  │                          │  │ │ [Card 1][Card 2]...  │  │   │
│  │                          │  │ │ (star borders)       │  │   │
│  │                          │  │ └──────────────────────┘  │   │
│  │                          │  │                            │   │
│  └──────────────────────────┘  └────────────────────────────┘   │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  Metrics Footer (Count-up Cards):                               │
│  [R²: 0.9558] [Acc: 95.3%] [Sims: 551/1440] [MSE: 0.0125]     │
│  (with animated borders & spark effects on completion)          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 DETAILED PHASE FLOWS

### Phase 0: Environment & Overview
**Content:**
- Header with typing animation: "🔬 Polymer Informatics Discovery Engine"
- Description of the project
- Quick stats: "1440 polymers generated | 551 successful simulations | 10 backbone families"
- CTA button: "Begin Discovery" (with spark effect on click)

---

### Phase 1: ANSYS Maxwell 2D Simulation Campaign
**Content:**
- Title with typing animation: "Combinatorial Polymer Generation"
- Educational text describing SMILES generation
- Display: "1440 unique configurations across 10 backbone families"
- Visualization options:
  - Interactive backbone selector (10 buttons)
  - Show example SMILES strings
  - Simulation summary stats: "551/1440 successful (38.3%)"
- Visual feedback: Animated cards showing each backbone family

---

### Phase 2: ML Training & Model Selection
**Content:**
- Title: "Machine Learning Training Results"
- Three model cards (staggered reveal):
  1. **3-Way Ensemble** (MLP + GBR + XGBoost)
     - R² = 0.9558 (count-up)
     - 10-Fold CV: 0.9073
     - Features: 512 Morgan bits + 6 physical
  2. **Graph Neural Network (GNN)**
     - R² = 0.9528 (count-up)
     - 5-Fold CV: 0.9301
     - Architecture: Graph-based molecular representation
  3. **Variational Autoencoder (VAE)**
     - Latent Dim: 128
     - Purpose: Generative discovery
     - Reconstruction Error: [metric]

- Model Comparison Table (interactive):
  - Selectable rows with star-border highlighting
  - Comparative metrics

---

### Phase 3: Inverse Design & Virtual High-Throughput Screening (vHTS)
**Content:**
- **Left Panel (Interactive Controls):**
  - Target Capacitance: Number input (10-2000 pF/m)
  - Virtual Library Size: Slider (1000-25000)
  - Thickness Range: Dual slider (100-5000 nm)
  - Material Family Filter: Multi-select checkboxes
  - Model Selection: Dropdown (Ensemble/GNN)
  - **"Run Discovery" Button** with click spark effect

- **Main Panel (Results):**
  - Running animation (stepper or progress bar) while searching
  - Once complete: Grid of top-6 candidates (3 columns)
  - Each result card includes:
    - Rank badge (#1, #2, etc.)
    - Predicted capacitance (pF/m)
    - Deviation from target (error %)
    - Base material (PE, PP, etc.)
    - Thickness (nm)
    - 2D molecule structure image (RDKit render)
    - SMILES string
    - Action buttons: [View Details] [Export] [Compare]
    - Animated star border, especially for Rank #1

---

### Phase 4: Advanced Upgrades & Analytics
**Content:**
- **Three Sub-Sections (Staggered Menu):**

  1. **Pareto Front Optimization**
     - Scatter plot: Trade-off between two objectives (e.g., R² vs. inference speed)
     - Interactive tooltip on hover
     - Highlighted Pareto-optimal candidates

  2. **Generative Discovery (VAE)**
     - Latent space slider controls (2-3 principal dimensions)
     - Real-time molecule generation preview
     - "Generate & Test" button

  3. **Model Comparison Dashboard**
     - Side-by-side metric comparison (count-up animations)
     - Confusion matrix / error distribution plot
     - Cross-fold validation scores

---

### Phase 5: Comprehensive Results & Reporting
**Content:**
- **Summary Statistics (Count-up Cards):**
  - Total Polymers Screened: 0 → 25,000
  - Successful Predictions: 0 → [count]
  - Best Candidate Accuracy: 0% → [%]
  - R² Score: 0.0000 → 0.9558

- **Comparative Analytics:**
  - Results table: Rank | Polymer | Target | Predicted | Error | Material
  - Sortable/filterable columns
  - Visual bars showing error magnitude

- **Downloadable Exports:**
  - [Download CSV] with spark effect
  - [Download JSON] with spark effect
  - [Export Top Candidate SMILES] with spark effect
  - [Generate Report PDF]

---

## ⚡ ANIMATION CHECKLIST

### Entrance Animations (Page/Component Load)
- [ ] Staggered menu items fade-in with horizontal slide (50ms stagger)
- [ ] Phase stepper draws from left to right
- [ ] Result cards slide-in with stagger
- [ ] Text elements type out on entry

### Interaction Animations
- [ ] Button click triggers spark burst
- [ ] Hover on card reveals star border
- [ ] Modal/panel entrance: scale + fade
- [ ] Dropdown menu: staggered item appearance

### Process Animations
- [ ] Stepper phase transition (smooth color/state change)
- [ ] Discovery execution: spinning/pulsing progress indicator
- [ ] Count-up animations on metric reveals
- [ ] Border animations on active/highlighted elements

### Idle Animations (Continuous)
- [ ] Pixel snow background floating gently
- [ ] Star borders pulsing/animated continuously
- [ ] Breathing effect on "active" elements

---

## 🎯 INTERNSHIP-LEVEL QUALITY STANDARDS

### Code Quality
- [ ] TypeScript for type safety
- [ ] ESLint + Prettier for code formatting
- [ ] Component modularity: Each animation component is isolated & reusable
- [ ] Custom hooks for animation logic
- [ ] Proper error handling & loading states

### UX/Accessibility
- [ ] Keyboard navigation support (especially for stepper)
- [ ] ARIA labels for all interactive elements
- [ ] Color contrast meets WCAG AA standards
- [ ] Smooth animations don't cause motion sickness (respect prefers-reduced-motion)
- [ ] Mobile responsiveness (if applicable)

### Performance
- [ ] Canvas-based pixel snow for smooth 60fps
- [ ] Lazy load heavy visualizations
- [ ] Memoized components to prevent unnecessary re-renders
- [ ] Optimized Framer Motion animations (use GPU acceleration)

### Documentation
- [ ] Component storybook (Storybook.js) for all animation components
- [ ] README with setup instructions & architecture overview
- [ ] Inline code comments for complex animations
- [ ] Environment setup guide (.env.example)

---

## 🚀 DEVELOPMENT ROADMAP

### Sprint 1: Foundation & Layout
- [ ] Project setup (Vite + React + TypeScript)
- [ ] Tailwind CSS + Framer Motion integration
- [ ] Pixel snow background implementation
- [ ] Main dashboard layout & navigation structure
- [ ] Phase stepper component

### Sprint 2: Animation Components
- [ ] Staggered menu implementation
- [ ] Text type animation on titles
- [ ] Click spark/ripple effect
- [ ] Star border animation
- [ ] Count-up animation component

### Sprint 3: Phase Content & Integration
- [ ] API client setup (Axios)
- [ ] Phase 0-5 content implementation
- [ ] Polymer generator form (Phase 1)
- [ ] Model selection cards (Phase 2)
- [ ] Connect frontend to backend API

### Sprint 4: Discovery & Results
- [ ] Inverse design search form (Phase 3)
- [ ] Results grid with molecule rendering
- [ ] Analytics dashboard (Phase 4-5)
- [ ] Download/export functionality
- [ ] Error handling & loading states

### Sprint 5: Polish & Optimization
- [ ] Responsive design refinement
- [ ] Animation performance optimization
- [ ] Accessibility audit
- [ ] Create Storybook documentation
- [ ] Final testing & bug fixes

---

## 📝 DELIVERABLES

By the end of this project, you should have:

1. **React Frontend Repository**
   - Complete source code with all animations implemented
   - Environment setup guide
   - Storybook for component library

2. **Backend API Integration**
   - Well-documented API endpoints
   - Error handling & response standardization

3. **Deployed Instance** (optional)
   - Live demo on Vercel or similar
   - Or Docker container for local deployment

4. **Documentation**
   - Component API reference
   - Architecture overview
   - Animation implementation guide
   - Setup & deployment instructions

5. **Code Quality**
   - 80%+ code coverage (unit tests)
   - Type-safe TypeScript codebase
   - Performance metrics documented

---

## 🎨 RECOMMENDED COLOR PALETTE

- **Primary Background:** `#0F1419` (dark blue-gray)
- **Secondary Background:** `#1A1A2E` (slightly lighter)
- **Accent Color (Primary):** `#00D9FF` (cyan)
- **Accent Color (Secondary):** `#FF006E` (hot pink)
- **Success:** `#4CAF50` (green)
- **Error:** `#FF5252` (red)
- **Text Primary:** `#FFFFFF` (white)
- **Text Secondary:** `#B0BEC5` (light gray)
- **Border:** `#37474F` (dark gray with transparency)

---

## 📚 REFERENCE LIBRARIES

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "framer-motion": "^10.x",
    "zustand": "^4.x",
    "axios": "^1.x",
    "react-countup": "^6.x",
    "plotly.js": "^2.x",
    "react-icons": "^4.x"
  },
  "devDependencies": {
    "typescript": "^5.x",
    "vite": "^4.x",
    "tailwindcss": "^3.x",
    "eslint": "^8.x",
    "prettier": "^3.x",
    "@testing-library/react": "^14.x",
    "storybook": "^7.x"
  }
}
```

---

## ✅ FINAL NOTES

- This is an **internship-level project**, so prioritize clean code, documentation, and professional standards
- Focus on **one phase at a time** to avoid scope creep
- Test each animation independently before integration
- Keep animations **subtle but noticeable** (don't overdo it)
- **Performance first:** A smooth 60fps experience beats fancy animations
- Ask for clarification on requirements as they arise
- Consider accessibility from day one, not as an afterthought

---

**Ready to build? Start with Phase 0 setup and the core animation components!**
