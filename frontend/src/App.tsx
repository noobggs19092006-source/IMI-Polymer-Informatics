import { useState, useEffect } from 'react';
import { 
  ArrowRightCircle, 
  Zap, 
  LockKeyhole, 
  Fingerprint, 
  Menu, 
  X,
  Settings, 
  Play, 
  BrainCircuit, 
  Search, 
  BarChart3, 
  Database, 
  FlaskConical,
  Home
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Stepper, 
  type Phase, 
  TextTypeReal, 
  StaggeredMenu, 
  type MenuItem, 
  CountUpMetric,
  ClickSparkReal
} from './components/animations';
import {
  Phase0Overview,
  Phase1Generation,
  Phase2ModelSelection,
  Phase3InverseDesign,
  Phase4Analytics,
  Phase5Results
} from './pages';

const PHASES: Phase[] = [
  { id: 0, label: 'Environment' },
  { id: 1, label: 'Generation' },
  { id: 2, label: 'Simulation' },
  { id: 3, label: 'ML Training' },
  { id: 4, label: 'Discovery' },
  { id: 5, label: 'Results' },
];

const MENU_ITEMS: MenuItem[] = [
  { id: 'overview', label: 'Phase Overview', icon: Database },
  { id: 'generation', label: 'Data Generation', icon: Play },
  { id: 'simulation', label: 'Simulation Config', icon: Settings },
  { id: 'model', label: 'Model Selection', icon: BrainCircuit },
  { id: 'inverse', label: 'Inverse Design', icon: Search },
  { id: 'results', label: 'Results & Analytics', icon: BarChart3 },
];

const NAV_LINKS = [
  { label: 'Pipeline', phase: 0, menuId: 'overview' },
  { label: 'Simulation', phase: 2, menuId: 'simulation' },
  { label: 'Training', phase: 2, menuId: 'model' },
  { label: 'Discovery', phase: 3, menuId: 'inverse' },
  { label: 'Analytics', phase: 4, menuId: 'inverse' }
];

export default function App() {
  const [showDashboard, setShowDashboard] = useState(false);
  const [currentPhase, setCurrentPhase] = useState(0);
  const [activeMenuId, setActiveMenuId] = useState(MENU_ITEMS[0].id);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Stagger helper
  const fadeUp = (delay: number) => ({
    hidden: { opacity: 0, y: 28 },
    visible: { 
      opacity: 1, 
      y: 0, 
      transition: { 
        delay, 
        duration: 0.6, 
        ease: [0.22, 1, 0.36, 1] as const
      } 
    }
  });

  const handleMenuSelect = (menuId: string) => {
    setActiveMenuId(menuId);
    const phaseMap: { [key: string]: number } = {
      'overview': 0,
      'generation': 1,
      'simulation': 2,
      'model': 2,
      'inverse': 3,
      'results': 5,
    };
    const phase = phaseMap[menuId];
    if (phase !== undefined) {
      setCurrentPhase(phase);
    }
  };

  // Sync menu ID back when currentPhase changes
  useEffect(() => {
    const reversePhaseMap: { [key: number]: string } = {
      0: 'overview',
      1: 'generation',
      2: 'model',
      3: 'inverse',
      4: 'inverse',
      5: 'results',
    };
    const menuId = reversePhaseMap[currentPhase];
    if (menuId) {
      setActiveMenuId(menuId);
    }
  }, [currentPhase]);

  const handleNavLinkClick = (phase: number, menuId: string) => {
    setCurrentPhase(phase);
    setActiveMenuId(menuId);
    setShowDashboard(true);
    setIsMobileMenuOpen(false);
  };

  return (
    <div className="relative w-full min-h-screen text-[#192837] font-body bg-[#ffffff] overflow-hidden flex flex-col justify-between">
      
      {/* Fullscreen Video Background */}
      <video 
        autoPlay 
        muted 
        loop 
        playsInline 
        className="absolute inset-0 w-full h-full object-cover z-0 select-none pointer-events-none"
      >
        <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260518_003132_8b7edcb6-c64d-4a52-a9ca-879942e122ad.mp4" type="video/mp4" />
      </video>

      {/* Video Overlay Layer to guarantee readability */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#ffffff]/70 via-[#ffffff]/60 to-[#ffffff]/90 z-0 pointer-events-none" />

      {/* Conditional Layout Rendering with AnimatePresence */}
      <AnimatePresence mode="wait">
        {!showDashboard ? (
          <motion.div 
            key="hero"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
            className="flex-1 flex flex-col justify-between min-h-screen relative z-10"
          >
            {/* Landing Navbar */}
            <header className="w-full max-w-[1280px] mx-auto px-5 sm:px-8 py-4 sm:py-5 flex items-center justify-between z-10 flex-none">
              {/* Left: Logo */}
              <div className="flex items-center gap-3">
                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" overflow="visible" viewBox="0 0 256 256" className="shrink-0">
                  <path d="M 64 128 L 64.5 128 L 32 95 L 0 64 L 0 0 L 64 0 L 128 64 L 128 64.5 L 161 32 L 192 0 L 256 0 L 256 64 L 192 128 L 128 128 L 128 192 L 96 223 L 63.5 256 L 0 256 L 0 192 Z M 256 192 L 224 223 L 191.5 256 L 128 256 L 128 192 L 192 128 L 256 128 Z" fill="#192837"/>
                </svg>
                <span className="font-heading text-lg font-bold uppercase tracking-tight text-[#192837]">Polymer Informatics</span>
              </div>

              {/* Center: Desktop Nav Links */}
              <nav className="hidden md:flex items-center gap-8">
                {NAV_LINKS.map(link => (
                  <button 
                    key={link.label} 
                    onClick={() => handleNavLinkClick(link.phase, link.menuId)}
                    className="text-sm font-medium text-[#192837] hover:opacity-75 transition-opacity cursor-pointer bg-transparent border-none"
                  >
                    {link.label}
                  </button>
                ))}
              </nav>

              {/* Right: Desktop CTA Buttons */}
              <div className="hidden md:flex items-center gap-3">
                <button 
                  onClick={() => setShowDashboard(true)}
                  className="px-5 py-2.5 bg-[#F2F2EE] hover:bg-[#EAEAEA] text-[#192837] text-sm font-semibold rounded-full transition-colors duration-200 cursor-pointer"
                >
                  Sign In
                </button>
                <button 
                  onClick={() => setShowDashboard(true)}
                  className="px-5 py-2.5 bg-[#7342E2] hover:bg-[#7342E2]/90 text-white text-sm font-semibold rounded-full transition-colors duration-200 cursor-pointer shadow-sm"
                >
                  Start Discovery
                </button>
              </div>

              {/* Mobile Menu Trigger */}
              <button 
                onClick={() => setIsMobileMenuOpen(true)}
                className="md:hidden p-2 text-[#192837] hover:bg-slate-200/50 rounded-lg transition-colors cursor-pointer"
                aria-label="Open menu"
              >
                <Menu size={24} />
              </button>
            </header>

            {/* Hero Content */}
            <div className="w-full max-w-[1280px] mx-auto px-5 sm:px-8 flex-1 flex items-center pt-[clamp(40px,8vw,72px)] pb-12">
              <div className="max-w-[560px] flex flex-col items-start text-left">
                {/* Heading */}
                <motion.h1 
                  variants={fadeUp(0)}
                  initial="hidden"
                  animate="visible"
                  style={{ fontFamily: 'var(--font-heading)' }}
                  className="text-[clamp(1.65rem,5vw,3rem)] font-extrabold leading-[1.05] tracking-[-0.01em] text-[#192837] mb-6"
                >
                  <Zap size={24} className="inline-block text-[#192837] mr-2 align-middle relative -top-[2px]" />
                  Discover Next-Gen Dielectrics
                  <LockKeyhole size={24} className="inline-block text-[#192837] mx-2 align-middle relative -top-[2px]" />
                  with Physics-Informed ML
                  <Fingerprint size={24} className="inline-block text-[#192837] ml-2 align-middle relative -top-[2px]" />
                </motion.h1>

                {/* Subtext */}
                <motion.p 
                  variants={fadeUp(0.15)}
                  initial="hidden"
                  animate="visible"
                  style={{ fontFamily: 'var(--font-body)' }}
                  className="text-base md:text-[clamp(0.9rem,2.5vw,1.1rem)] leading-[1.65] text-[#192837] opacity-80 mb-8 max-w-[560px]"
                >
                  Zero complexity, total precision. Polymer Informatics screens virtual libraries, validates structures via ANSYS Maxwell 2D, and uses 3-way ML ensembles to discover optimal dielectrics.
                </motion.p>

                {/* Button */}
                <motion.div
                  variants={fadeUp(0.30)}
                  initial="hidden"
                  animate="visible"
                >
                  <motion.button 
                    whileHover={{ scale: 1.04, filter: 'brightness(1.1)' }}
                    whileTap={{ scale: 0.96 }}
                    onClick={() => setShowDashboard(true)}
                    style={{ 
                      fontFamily: 'var(--font-body)',
                      boxShadow: '0 4px 24px rgba(115,66,226,0.28)'
                    }}
                    className="flex items-center justify-between gap-8 px-6 py-[17px] bg-[#7342E2] hover:bg-[#7342E2]/95 text-white font-semibold text-base rounded-[50px] transition-all duration-300 min-w-[210px] cursor-pointer"
                  >
                    <span className="text-[clamp(0.9rem,2vw,1rem)]">Start Discovery</span>
                    <ArrowRightCircle size={20} className="text-white" />
                  </motion.button>
                </motion.div>
              </div>
            </div>

            {/* Empty Spacer */}
            <div className="w-full py-4 flex-none" />
          </motion.div>
        ) : (
          <motion.div 
            key="dashboard"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            transition={{ duration: 0.4 }}
            className="flex-1 flex flex-col justify-between min-h-screen relative z-10"
          >
            {/* Dashboard Header */}
            <header className="w-full bg-bg-secondary/70 backdrop-blur-md border-b border-border p-6 z-10 flex-none shadow-sm shadow-indigo-100/5">
              <div className="max-w-7xl mx-auto flex flex-col space-y-6">
                <div className="flex items-center space-x-3">
                  {/* Flask logo acts as back to home trigger */}
                  <button 
                    onClick={() => setShowDashboard(false)}
                    className="flex items-center space-x-2 bg-transparent border-none p-1 hover:opacity-85 transition-opacity cursor-pointer text-left"
                    title="Back to Landing Page"
                  >
                    <FlaskConical className="w-6 h-6 text-accent-primary" />
                    <TextTypeReal 
                      text="Polymer Informatics Discovery Engine" 
                      className="text-xl md:text-2xl font-bold font-mono tracking-tight text-text-primary font-heading"
                    />
                  </button>
                  
                  {/* Home Action Shortcut */}
                  <button
                    onClick={() => setShowDashboard(false)}
                    className="p-1.5 hover:bg-slate-200/50 rounded-lg text-text-secondary transition-colors cursor-pointer"
                    title="Back to Home"
                  >
                    <Home size={18} />
                  </button>

                  <span className="ml-auto flex items-center space-x-2 px-3 py-1 bg-bg-primary/50 rounded-full border border-border text-xs text-text-secondary font-mono">
                    <div className="w-2 h-2 rounded-full bg-accent-primary animate-pulse" />
                    <span>ANSYS Engine Online</span>
                  </span>
                </div>
                
                <div className="px-4">
                  <Stepper 
                    phases={PHASES} 
                    currentPhase={currentPhase} 
                    onPhaseClick={(id) => setCurrentPhase(id)} 
                  />
                </div>
              </div>
            </header>

            {/* Dashboard Content Container */}
            <main className="flex-1 flex max-w-7xl w-full mx-auto px-6 py-8 gap-8 items-stretch min-h-0 z-10">
              
              {/* Sidebar */}
              <aside className="w-64 bg-bg-secondary/70 backdrop-blur-md border border-border rounded-xl p-6 flex flex-col shadow-sm shadow-indigo-100/5">
                <h2 className="text-xs uppercase tracking-widest text-text-secondary mb-4 ml-4 font-bold">Navigation</h2>
                <StaggeredMenu 
                  items={MENU_ITEMS}
                  activeId={activeMenuId}
                  onSelect={handleMenuSelect}
                />
                
                <div className="mt-auto pt-4 border-t border-border">
                  <ClickSparkReal>
                    <button 
                      onClick={() => setCurrentPhase(prev => Math.min(prev + 1, 5))}
                      className="w-full py-3 bg-accent-primary hover:bg-accent-primary/95 text-white font-bold rounded-lg transition-all duration-200 cursor-pointer shadow-sm active:scale-95"
                    >
                      Advance Phase
                    </button>
                  </ClickSparkReal>
                </div>
              </aside>

              {/* Dynamic Pages Area */}
              <section className="flex-1 bg-bg-secondary/45 backdrop-blur-md border border-border rounded-xl p-8 relative overflow-y-auto">
                <div className="max-w-5xl">
                  {currentPhase === 0 && <Phase0Overview onAdvance={() => setCurrentPhase(1)} />}
                  {currentPhase === 1 && <Phase1Generation />}
                  {currentPhase === 2 && <Phase2ModelSelection />}
                  {currentPhase === 3 && <Phase3InverseDesign />}
                  {currentPhase === 4 && <Phase4Analytics />}
                  {currentPhase === 5 && <Phase5Results />}
                </div>
              </section>
            </main>

            {/* Dashboard Footer */}
            <footer className="w-full bg-bg-secondary/70 backdrop-blur-md border-t border-border p-4 z-10 flex-none shadow-sm shadow-indigo-100/5">
              <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-4">
                <CountUpMetric 
                  label="R² Score"
                  value={0.9558}
                  decimals={4}
                  duration={2.5}
                />
                <CountUpMetric 
                  label="Accuracy"
                  value={95.3}
                  decimals={1}
                  suffix="%"
                  duration={3}
                />
                <CountUpMetric 
                  label="Simulations"
                  value={551}
                  suffix=" / 1440"
                  duration={2.5}
                />
                <CountUpMetric 
                  label="MSE"
                  value={0.0125}
                  decimals={4}
                  duration={2}
                />
              </div>
            </footer>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Mobile Drawer (AnimatePresence) */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <>
            {/* Backdrop */}
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsMobileMenuOpen(false)}
              className="fixed inset-0 bg-[#192837]/35 backdrop-blur-[4px] z-40"
            />

            {/* Menu Sheet */}
            <motion.aside 
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ ease: [0.22, 1, 0.36, 1], duration: 0.45 }}
              className="fixed right-0 top-0 w-full max-w-[360px] h-[100dvh] bg-[#CFC8C5] shadow-[-12px_0_48px_rgba(25,40,55,0.18)] z-50 flex flex-col p-6 text-[#192837]"
            >
              {/* Header */}
              <div className="flex items-center justify-between pb-6 border-b border-[#192837]/10">
                <div className="flex items-center gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="none" viewBox="0 0 256 256">
                    <path d="M 64 128 L 64.5 128 L 32 95 L 0 64 L 0 0 L 64 0 L 128 64 L 128 64.5 L 161 32 L 192 0 L 256 0 L 256 64 L 192 128 L 128 128 L 128 192 L 96 223 L 63.5 256 L 0 256 L 0 192 Z M 256 192 L 224 223 L 191.5 256 L 128 256 L 128 192 L 192 128 L 256 128 Z" fill="#192837"/>
                  </svg>
                  <span className="font-heading text-lg font-bold uppercase tracking-tight">Polymer Informatics</span>
                </div>
                <button 
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="p-2 text-[#192837] hover:bg-[#192837]/10 rounded-full transition-colors cursor-pointer"
                  aria-label="Close menu"
                >
                  <X size={20} />
                </button>
              </div>

              {/* Staggered Navigation links */}
              <nav className="flex-1 flex flex-col gap-6 pt-8">
                {NAV_LINKS.map((link, i) => (
                  <motion.button
                    key={link.label}
                    onClick={() => handleNavLinkClick(link.phase, link.menuId)}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.18 + i * 0.07, ease: 'easeOut' }}
                    className="text-left text-lg font-semibold hover:text-[#7342E2] transition-colors bg-transparent border-none cursor-pointer flex items-center justify-between"
                  >
                    <span>{link.label}</span>
                  </motion.button>
                ))}
              </nav>

              {/* Drawer Footer CTAs */}
              <div className="pt-6 border-t border-[#192837]/10 flex flex-col gap-3">
                <button 
                  onClick={() => { setShowDashboard(true); setIsMobileMenuOpen(false); }}
                  className="w-full py-3 bg-[#F2F2EE] hover:bg-[#EAEAEA] text-[#192837] font-semibold rounded-full transition-colors cursor-pointer"
                >
                  Sign In
                </button>
                <button 
                  onClick={() => { setShowDashboard(true); setIsMobileMenuOpen(false); }}
                  className="w-full py-3 bg-[#7342E2] hover:bg-[#7342E2]/90 text-white font-semibold rounded-full transition-colors cursor-pointer shadow-md"
                >
                  Start Discovery
                </button>
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

    </div>
  );
}
