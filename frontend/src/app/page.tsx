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
    <div className="min-h-screen bg-abyssal text-diamond selection:bg-cyan-bright selection:text-abyssal relative overflow-x-hidden">
      {/* Global subtle radial ambient gradient */}
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(15,61,86,0.45),rgba(5,19,32,1))] pointer-events-none -z-20" />

      {/* 1. Glass Navbar with 3D logo & cyan glow */}
      <Navbar />

      <main>
        {/* 2. Hero Section with 3D Emblem and cover texture */}
        <Hero />

        {/* 3. Clinical Trust Metrics & Stats */}
        <TrustMetrics />

        {/* 4. 3D Vitrine of Treatments with one-click booking triggers */}
        <Features />

        {/* 5. OmniChannel Showcase with holographic looping video reel */}
        <OmniChannelMockup />

        {/* 6. Interactive Booking CTA & 45-min Slot Picker */}
        <BookingCTA />
      </main>

      {/* 7. Footer with Medical Disclaimer & Clinic Address */}
      <Footer />
    </div>
  );
}
