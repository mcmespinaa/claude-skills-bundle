# Component Patterns Reference

Copy-paste patterns for premium UI components. Built for Next.js + Tailwind CSS v4 + Motion (Framer Motion) + shadcn/ui. Adapt to your project's stack.

## Table of Contents

### Core Components
1. [Animated Hero Section](#animated-hero-section)
2. [Glassmorphism Card](#glassmorphism-card)
3. [Staggered Grid Reveal](#staggered-grid-reveal)
4. [Sticky Nav with Blur](#sticky-nav-with-blur)
5. [Scroll-Triggered Section](#scroll-triggered-section)
6. [Animated Counter](#animated-counter)
7. [Gradient Text](#gradient-text)
8. [Spotlight Hover Card](#spotlight-hover-card)
9. [Animated Background Grid](#animated-background-grid)
10. [CTA Section with Glow](#cta-section-with-glow)

### Directory & Data Components
11. [Bento Grid Layout](#bento-grid-layout)
12. [Directory Card with Category](#directory-card-with-category)
13. [Filter Chip Bar](#filter-chip-bar)
14. [Multi-View Toggle](#multi-view-toggle)
15. [Map Detail Panel](#map-detail-panel)
16. [Search with Autocomplete](#search-with-autocomplete)
17. [Animated Stat Card](#animated-stat-card)

---

## Animated Hero Section

```tsx
// Using Framer Motion + Tailwind
import { motion } from "motion/react";

function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-zinc-950">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-blue-500/10 via-transparent to-transparent" />

      <div className="relative z-10 max-w-4xl mx-auto px-4 text-center">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="text-5xl md:text-7xl font-bold tracking-tight text-white"
        >
          Build something
          <span className="bg-gradient-to-r from-blue-400 to-violet-400 bg-clip-text text-transparent">
            {" "}beautiful
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut", delay: 0.1 }}
          className="mt-6 text-lg text-zinc-400 max-w-2xl mx-auto"
        >
          A short, compelling description that supports the headline.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut", delay: 0.2 }}
          className="mt-10 flex gap-4 justify-center"
        >
          <button className="px-8 py-3 rounded-full bg-white text-zinc-900 font-medium hover:bg-zinc-200 transition-colors">
            Get Started
          </button>
          <button className="px-8 py-3 rounded-full border border-white/20 text-white hover:bg-white/10 transition-colors">
            Learn More
          </button>
        </motion.div>
      </div>
    </section>
  );
}
```

---

## Glassmorphism Card

```tsx
function GlassCard({ title, description, icon }: { title: string; description: string; icon: React.ReactNode }) {
  return (
    <div className="group relative rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl p-8 transition-all duration-300 hover:bg-white/10 hover:border-white/20">
      <div className="mb-4 text-blue-400">{icon}</div>
      <h3 className="text-xl font-semibold text-white">{title}</h3>
      <p className="mt-2 text-zinc-400 leading-relaxed">{description}</p>
    </div>
  );
}
```

---

## Staggered Grid Reveal

```tsx
import { motion } from "motion/react";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } },
};

function FeatureGrid({ features }: { features: Array<{ title: string; description: string }> }) {
  return (
    <motion.div
      variants={container}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, margin: "-100px" }}
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
    >
      {features.map((feature) => (
        <motion.div key={feature.title} variants={item}>
          <GlassCard title={feature.title} description={feature.description} />
        </motion.div>
      ))}
    </motion.div>
  );
}
```

---

## Sticky Nav with Blur

```tsx
"use client";
import { useEffect, useState } from "react";

function Navbar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-zinc-950/80 backdrop-blur-xl border-b border-white/10"
          : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <span className="text-white font-semibold text-lg">Brand</span>
        <div className="hidden md:flex gap-8">
          {["Features", "Pricing", "About"].map((link) => (
            <a key={link} href={`#${link.toLowerCase()}`} className="text-zinc-400 hover:text-white transition-colors text-sm">
              {link}
            </a>
          ))}
        </div>
        <button className="px-5 py-2 rounded-full bg-white text-zinc-900 text-sm font-medium hover:bg-zinc-200 transition-colors">
          Sign Up
        </button>
      </div>
    </nav>
  );
}
```

---

## Scroll-Triggered Section

```tsx
import { motion } from "motion/react";

function Section({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return (
    <section className="py-24 md:py-32">
      <div className="max-w-7xl mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight text-white">{title}</h2>
          <p className="mt-4 text-zinc-400 max-w-2xl mx-auto">{subtitle}</p>
        </motion.div>
        {children}
      </div>
    </section>
  );
}
```

---

## Animated Counter

```tsx
import { useEffect, useRef, useState } from "react";
import { useInView } from "motion/react";

function Counter({ target, suffix = "" }: { target: number; suffix?: string }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!isInView) return;
    const duration = 2000;
    const steps = 60;
    const increment = target / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        setCount(target);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, duration / steps);
    return () => clearInterval(timer);
  }, [isInView, target]);

  return (
    <span ref={ref} className="text-5xl font-bold text-white tabular-nums">
      {count.toLocaleString()}{suffix}
    </span>
  );
}
```

---

## Gradient Text

```tsx
function GradientText({ children, from = "from-blue-400", to = "to-violet-400" }: {
  children: React.ReactNode;
  from?: string;
  to?: string;
}) {
  return (
    <span className={`bg-gradient-to-r ${from} ${to} bg-clip-text text-transparent`}>
      {children}
    </span>
  );
}
```

---

## Spotlight Hover Card

```tsx
"use client";
import { useRef, useState } from "react";

function SpotlightCard({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  };

  return (
    <div
      ref={ref}
      onMouseMove={handleMouseMove}
      className="relative overflow-hidden rounded-2xl border border-white/10 bg-zinc-900 p-8"
    >
      <div
        className="pointer-events-none absolute -inset-px opacity-0 transition-opacity duration-300 group-hover:opacity-100"
        style={{
          background: `radial-gradient(600px circle at ${position.x}px ${position.y}px, rgba(59,130,246,0.1), transparent 40%)`,
        }}
      />
      {children}
    </div>
  );
}
```

---

## Animated Background Grid

```css
/* Add to global CSS */
.bg-grid {
  background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 64px 64px;
}

.bg-grid-fade {
  mask-image: radial-gradient(ellipse at center, black 30%, transparent 70%);
}
```

```tsx
function GridBackground() {
  return (
    <div className="absolute inset-0 bg-grid bg-grid-fade" aria-hidden="true" />
  );
}
```

---

## CTA Section with Glow

```tsx
import { motion } from "motion/react";

function CTASection() {
  return (
    <section className="relative py-24 overflow-hidden">
      {/* Glow effect */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-500/20 rounded-full blur-[128px]" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="relative z-10 max-w-2xl mx-auto text-center px-4"
      >
        <h2 className="text-3xl md:text-5xl font-bold tracking-tight text-white">
          Ready to get started?
        </h2>
        <p className="mt-4 text-zinc-400">
          Join thousands of users building beautiful interfaces.
        </p>
        <button className="mt-8 px-8 py-4 rounded-full bg-blue-500 text-white font-medium hover:bg-blue-400 transition-colors">
          Start Building
        </button>
      </motion.div>
    </section>
  );
}
```

---

## Bento Grid Layout

```tsx
// Homepage dashboard-style bento grid with varied card sizes
function BentoGrid({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 auto-rows-[180px]">
      {children}
    </div>
  );
}

function BentoCard({
  title, description, icon, className = "", colSpan = 1, rowSpan = 1,
}: {
  title: string; description: string; icon: React.ReactNode;
  className?: string; colSpan?: 1 | 2; rowSpan?: 1 | 2;
}) {
  return (
    <div
      className={`group relative overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-6 transition-all duration-300 hover:bg-white/10 hover:border-white/20
        ${colSpan === 2 ? "md:col-span-2" : ""}
        ${rowSpan === 2 ? "md:row-span-2" : ""}
        ${className}`}
    >
      <div className="mb-3 text-emerald-400 transition-transform group-hover:scale-110 duration-300">
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-white">{title}</h3>
      <p className="mt-1 text-sm text-zinc-400 leading-relaxed">{description}</p>
    </div>
  );
}

// Usage:
// <BentoGrid>
//   <BentoCard colSpan={2} title="80+ Initiatives" description="..." icon={<Globe />} />
//   <BentoCard title="12 Categories" description="..." icon={<Layers />} />
//   <BentoCard title="13 Regions" description="..." icon={<Map />} />
//   <BentoCard rowSpan={2} title="Interactive Map" description="..." icon={<MapPin />} />
//   <BentoCard colSpan={2} title="Open Database" description="..." icon={<Database />} />
// </BentoGrid>
```

---

## Directory Card with Category

```tsx
import { motion } from "motion/react";

const CATEGORY_COLORS: Record<string, string> = {
  ecovillage: "#34d399",
  coliving: "#38bdf8",
  social_enterprise: "#818cf8",
  cooperative: "#c084fc",
  permaculture: "#fbbf24",
  network: "#fb923c",
};

function DirectoryCard({
  name, category, location, description, tags, onClick,
}: {
  name: string; category: string; location: string;
  description: string; tags: string[]; onClick: () => void;
}) {
  const color = CATEGORY_COLORS[category] || "#38bdf8";

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      onClick={onClick}
      className="group cursor-pointer rounded-2xl border border-white/10 bg-white/5 p-5 transition-all duration-300 hover:bg-white/10 hover:border-white/20"
      style={{ borderLeftColor: color, borderLeftWidth: 3 }}
    >
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-white group-hover:text-zinc-100">{name}</h3>
          <p className="mt-0.5 text-xs text-zinc-500">{location}</p>
        </div>
        <span
          className="text-[10px] font-medium uppercase tracking-wider px-2 py-0.5 rounded-full"
          style={{ color, backgroundColor: `${color}20` }}
        >
          {category.replace("_", " ")}
        </span>
      </div>
      <p className="mt-3 text-sm text-zinc-400 line-clamp-2">{description}</p>
      <div className="mt-3 flex flex-wrap gap-1.5">
        {tags.slice(0, 3).map((tag) => (
          <span key={tag} className="text-[10px] px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-400 border border-white/5">
            {tag}
          </span>
        ))}
        {tags.length > 3 && (
          <span className="text-[10px] px-2 py-0.5 text-zinc-500">+{tags.length - 3}</span>
        )}
      </div>
    </motion.div>
  );
}
```

---

## Filter Chip Bar

```tsx
"use client";
import { useState } from "react";

function FilterChipBar({
  categories, activeFilters, onToggle,
}: {
  categories: { id: string; label: string; color: string; count: number }[];
  activeFilters: Set<string>;
  onToggle: (id: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {categories.map((cat) => {
        const active = activeFilters.has(cat.id);
        return (
          <button
            key={cat.id}
            onClick={() => onToggle(cat.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border transition-all duration-200 ${
              active
                ? "border-current bg-current/15"
                : "border-zinc-700 bg-zinc-800/50 text-zinc-500 hover:border-zinc-500 hover:text-zinc-300"
            }`}
            style={active ? { color: cat.color } : undefined}
          >
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: active ? cat.color : "currentColor" }}
            />
            {cat.label}
            <span className="opacity-50">{cat.count}</span>
          </button>
        );
      })}
    </div>
  );
}
```

---

## Multi-View Toggle

```tsx
"use client";
import { motion } from "motion/react";

type View = "grid" | "list" | "map" | "table";

const views: { id: View; label: string; icon: string }[] = [
  { id: "grid", label: "Grid", icon: "⊞" },
  { id: "list", label: "List", icon: "☰" },
  { id: "map", label: "Map", icon: "🗺" },
  { id: "table", label: "Table", icon: "⊟" },
];

function ViewToggle({ active, onChange }: { active: View; onChange: (v: View) => void }) {
  return (
    <div className="inline-flex gap-1 p-1 rounded-lg bg-zinc-800/80 border border-white/5">
      {views.map((v) => (
        <button
          key={v.id}
          onClick={() => onChange(v.id)}
          className={`relative px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
            active === v.id ? "text-zinc-900" : "text-zinc-400 hover:text-zinc-200"
          }`}
        >
          {active === v.id && (
            <motion.div
              layoutId="active-view"
              className="absolute inset-0 bg-white rounded-md"
              transition={{ type: "spring", stiffness: 400, damping: 30 }}
            />
          )}
          <span className="relative z-10 flex items-center gap-1.5">
            {v.icon} {v.label}
          </span>
        </button>
      ))}
    </div>
  );
}
```

---

## Map Detail Panel

```tsx
import { motion, AnimatePresence } from "motion/react";
import { X } from "lucide-react";

function DetailPanel({
  item, onClose,
}: {
  item: { name: string; category: string; location: string; description: string; focus: string[]; website?: string; founded?: string } | null;
  onClose: () => void;
}) {
  return (
    <AnimatePresence mode="wait">
      {item && (
        <motion.aside
          key={item.name}
          initial={{ x: "100%", opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: "100%", opacity: 0 }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
          className="fixed right-0 top-0 bottom-0 w-[400px] bg-zinc-900 border-l border-white/10 overflow-y-auto z-50"
        >
          <div className="p-6">
            <button onClick={onClose} className="absolute top-4 right-4 p-2 text-zinc-500 hover:text-white transition-colors">
              <X size={18} />
            </button>

            <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
              {item.category}
            </span>
            <h2 className="mt-2 text-2xl font-bold text-white">{item.name}</h2>
            <p className="mt-1 text-sm text-zinc-500">{item.location}</p>

            <p className="mt-6 text-sm text-zinc-300 leading-relaxed">{item.description}</p>

            <div className="mt-6 flex flex-wrap gap-2">
              {item.focus.map((f) => (
                <span key={f} className="text-[11px] px-2.5 py-1 rounded-full bg-zinc-800 text-zinc-400 border border-white/5">
                  {f}
                </span>
              ))}
            </div>

            {item.website && (
              <a
                href={item.website}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-6 inline-flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-emerald-400 bg-emerald-400/10 border border-emerald-400/20 rounded-lg hover:bg-emerald-400/20 transition-colors"
              >
                Visit Website →
              </a>
            )}
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
```

---

## Search with Autocomplete

```tsx
"use client";
import { useState, useMemo, useRef, useEffect } from "react";
import { Search } from "lucide-react";

function SearchAutocomplete({
  items, onSelect, placeholder = "Search initiatives...",
}: {
  items: { id: string; name: string; category: string }[];
  onSelect: (id: string) => void;
  placeholder?: string;
}) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const filtered = useMemo(() => {
    if (!query.trim()) return [];
    const q = query.toLowerCase();
    return items.filter((i) => i.name.toLowerCase().includes(q)).slice(0, 8);
  }, [query, items]);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <div ref={ref} className="relative">
      <div className="relative">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
        <input
          value={query}
          onChange={(e) => { setQuery(e.target.value); setOpen(true); }}
          onFocus={() => setOpen(true)}
          placeholder={placeholder}
          className="w-full pl-10 pr-4 py-2.5 text-sm bg-zinc-800/80 border border-white/10 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-500 transition-colors"
        />
      </div>
      {open && filtered.length > 0 && (
        <div className="absolute top-full mt-1 w-full bg-zinc-900 border border-white/10 rounded-lg shadow-2xl overflow-hidden z-50">
          {filtered.map((item) => (
            <button
              key={item.id}
              onClick={() => { onSelect(item.id); setQuery(item.name); setOpen(false); }}
              className="w-full text-left px-4 py-2.5 text-sm text-zinc-300 hover:bg-white/5 transition-colors flex items-center justify-between"
            >
              <span>{item.name}</span>
              <span className="text-[10px] text-zinc-500 uppercase">{item.category}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## Animated Stat Card

```tsx
import { useRef, useEffect, useState } from "react";
import { useInView } from "motion/react";

function StatCard({ value, label, suffix = "", color = "#34d399" }: {
  value: number; label: string; suffix?: string; color?: string;
}) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!isInView) return;
    const steps = 40;
    const increment = value / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= value) { setCount(value); clearInterval(timer); }
      else setCount(Math.floor(current));
    }, 30);
    return () => clearInterval(timer);
  }, [isInView, value]);

  return (
    <div ref={ref} className="rounded-2xl border border-white/10 bg-white/5 p-6 text-center">
      <div className="text-4xl font-bold tabular-nums" style={{ color }}>
        {count.toLocaleString()}{suffix}
      </div>
      <div className="mt-2 text-sm text-zinc-400">{label}</div>
    </div>
  );
}

// Usage:
// <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
//   <StatCard value={80} suffix="+" label="Initiatives" color="#34d399" />
//   <StatCard value={12} label="Categories" color="#38bdf8" />
//   <StatCard value={13} label="Regions" color="#fbbf24" />
//   <StatCard value={71} label="Ekobyar Registered" color="#c084fc" />
// </div>
```
