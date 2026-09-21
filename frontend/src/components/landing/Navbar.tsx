'use client';

import React from 'react';
import Link from 'next/link';
import { Stethoscope, MessageCircle, Calendar, ShieldCheck, LayoutDashboard } from 'lucide-react';

export default function Navbar() {
  return (
    <header className="sticky top-4 z-50 max-w-6xl mx-auto px-4 sm:px-6 w-full">
      <nav 
        aria-label="Navegación principal"
        className="backdrop-blur-xl bg-sapphire-950/70 border border-white/10 rounded-2xl px-4 sm:px-6 h-16 flex items-center justify-between shadow-glass-card shadow-sapphire-950/50"
      >
        {/* Brand Logo */}
        <Link 
          href="/" 
          className="flex items-center gap-2.5 group focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-bright rounded-lg"
          aria-label="Lumina Dental Studio - Inicio"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sapphire-800 to-cyan-bright/20 border border-cyan-bright/30 flex items-center justify-center text-cyan-bright group-hover:scale-105 transition-transform duration-200">
            <Stethoscope className="w-5 h-5 drop-shadow-[0_0_8px_rgba(0,229,255,0.6)]" />
          </div>
          <div className="flex flex-col">
            <span className="font-extrabold text-base tracking-tight text-white flex items-center gap-1.5">
              Lumina <span className="text-cyan-bright font-medium text-xs tracking-widest uppercase">Dental Studio</span>
            </span>
            <span className="text-[10px] text-slate-400 font-medium tracking-wide">
              Tecnología & Cuidado Clínico
            </span>
          </div>
        </Link>

        {/* Navigation Links */}
        <div className="hidden md:flex items-center gap-6 text-xs font-semibold text-slate-300">
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
            className="flex items-center gap-1.5 text-slate-400 hover:text-white transition-colors bg-white/5 hover:bg-white/10 px-2.5 py-1 rounded-lg border border-white/10"
          >
            <LayoutDashboard className="w-3.5 h-3.5 text-teal-400" />
            <span>Portal Consultorio</span>
          </Link>
        </div>

        {/* Primary Action Button (WhatsApp) */}
        <div className="flex items-center gap-3">
          <a
            href="https://wa.me/?text=Hola%2C%20quisiera%20consultar%20por%20un%20turno%20en%20Lumina%20Dental%20Studio"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 bg-cyan-bright hover:bg-cyan-bright/90 text-sapphire-950 font-bold text-xs px-4 py-2 rounded-xl transition-all duration-200 shadow-cyan-glow hover:scale-102 focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
            aria-label="Abrir chat de WhatsApp para consultar o agendar cita"
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
