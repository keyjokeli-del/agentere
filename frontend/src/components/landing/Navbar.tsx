'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { MessageCircle, Calendar, Sparkles, LayoutDashboard } from 'lucide-react';

export default function Navbar() {
  return (
    <header className="sticky top-4 z-50 max-w-6xl mx-auto px-4 sm:px-6 w-full">
      <nav 
        aria-label="Navegación principal"
        className="glass-panel gpu-layer rounded-2xl px-4 sm:px-6 h-16 flex items-center justify-between border border-cyan-bright/20 shadow-2xl backdrop-blur-xl bg-sapphire-950/85"
      >
        {/* Brand Logo & Name */}
        <Link 
          href="/" 
          className="flex items-center gap-3 group focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-bright rounded-lg"
        >
          <div className="relative w-10 h-10 rounded-xl overflow-hidden border border-cyan-bright/40 shadow-[0_0_15px_rgba(0,229,255,0.35)] group-hover:scale-105 group-hover:shadow-[0_0_22px_rgba(0,229,255,0.6)] transition-all duration-300 bg-abyssal">
            <Image
              src="/social-kit/lumina-logo.png"
              alt="Lumina Dental Studio Emblem"
              fill
              sizes="40px"
              className="object-cover"
              priority
            />
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold text-base tracking-tight text-white flex items-center gap-1.5">
              Lumina <span className="text-cyan-bright font-medium text-xs tracking-widest uppercase">Dental Studio</span>
            </span>
            <span className="text-[10px] text-titanium-400 font-medium tracking-wide">
              Odontología de Precisión & IA 24/7
            </span>
          </div>
        </Link>

        {/* Navigation Links */}
        <div className="hidden md:flex items-center gap-6 text-xs font-semibold text-titanium-300">
          <a 
            href="#tratamientos" 
            className="hover:text-cyan-bright transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-bright rounded-md px-1.5 py-1"
          >
            Tratamientos
          </a>
          <a 
            href="#tecnologia" 
            className="hover:text-cyan-bright transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-bright rounded-md px-1.5 py-1"
          >
            Tecnología Omnicanal
          </a>
          <a 
            href="#agendar" 
            className="hover:text-cyan-bright transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-bright rounded-md px-1.5 py-1"
          >
            Agendar Turno
          </a>
          <Link
            href="/dashboard"
            className="flex items-center gap-1.5 text-cyan-bright hover:text-white transition-colors bg-cyan-bright/10 hover:bg-cyan-bright/20 px-3 py-1.5 rounded-xl border border-cyan-bright/30"
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>Portal Clínico</span>
          </Link>
        </div>

        {/* Primary Action Button (WhatsApp) */}
        <div className="flex items-center gap-3">
          <a
            href="https://wa.me/?text=Hola%2C%20quisiera%20consultar%20por%20un%20turno%20en%20Lumina%20Dental%20Studio"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 bg-cyan-bright hover:bg-cyan-bright/90 text-abyssal font-bold text-xs px-4 py-2.5 rounded-xl transition-all duration-200 shadow-cyan-glow hover:scale-102 focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
            aria-label="WhatsApp 24/7 - Consultar o agendar turno"
          >
            <MessageCircle className="w-4 h-4 fill-current" />
            <span className="hidden sm:inline">WhatsApp 24/7</span>
            <span className="sm:hidden">Turno</span>
          </a>
        </div>
      </nav>
    </header>
  );
}
