'use client';

import React from 'react';
import Navbar from '@/components/landing/Navbar';
import Hero from '@/components/landing/Hero';
import Features from '@/components/landing/Features';
import TrustMetrics from '@/components/landing/TrustMetrics';
import OmniChannelMockup from '@/components/landing/OmniChannelMockup';
import BookingCTA from '@/components/landing/BookingCTA';
import Footer from '@/components/landing/Footer';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-sapphire-950 text-slate-100 selection:bg-cyan-bright selection:text-sapphire-950 relative">
      {/* Global subtle radial ambient gradient */}
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(15,61,86,0.5),rgba(8,34,49,1))] pointer-events-none -z-20" />

      {/* 1. Glass Navbar */}
      <Navbar />

      <main>
        {/* 2. Hero Section (with 3D mascot Lumi placeholder) */}
        <Hero />

        {/* 3. Clinical Trust Metrics & Stats */}
        <TrustMetrics />

        {/* 4. 4 Clinical & Technological Pillars */}
        <Features />

        {/* 5. OmniChannel Showcase (with 16:9 3D conceptual art placeholder) */}
        <OmniChannelMockup />

        {/* 6. Interactive Booking CTA & 45-min Slot Picker */}
        <BookingCTA />
      </main>

      {/* 7. Footer with Medical Disclaimer & Clinic Address */}
      <Footer />
    </div>
  );
}
