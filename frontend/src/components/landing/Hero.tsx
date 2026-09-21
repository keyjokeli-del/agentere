'use client';

import React from 'react';
import Link from 'next/link';
import { Calendar, MessageCircle, Sparkles, Star, ShieldCheck, ArrowRight, Clock } from 'lucide-react';

export default function Hero() {
  return (
    <section 
      aria-label="Presentación principal de Lumina Dental Studio"
      className="relative pt-12 pb-20 md:pt-20 md:pb-28 overflow-hidden"
    >
      {/* Background Radial Glow Effects */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-sapphire-900/60 rounded-full blur-[140px] -z-10 pointer-events-none" />
      <div className="absolute top-1/3 right-10 w-[400px] h-[400px] bg-cyan-bright/10 rounded-full blur-[120px] -z-10 pointer-events-none" />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          
          {/* Left Column: Text & CTAs (7 cols) */}
          <div className="lg:col-span-7 space-y-6 text-center lg:text-left">
            
            {/* Value Badge */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-sapphire-900/60 border border-cyan-bright/30 text-cyan-bright text-xs font-semibold backdrop-blur-md shadow-glass-card">
              <Sparkles className="w-3.5 h-3.5 animate-pulse" />
              <span>Odontología de Precisión & Asistente IA 24/7</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold text-white tracking-tight leading-[1.15]">
              Tu sonrisa en manos expertas.{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-bright via-teal-300 to-white">
                Tu turno agendado en segundos.
              </span>
            </h1>

            {/* Subheading */}
            <p className="text-slate-300 text-sm sm:text-base lg:text-lg max-w-xl mx-auto lg:mx-0 leading-relaxed font-normal">
              Atención clínica personalizada con tecnología digital avanzada. Consulta precios, resuelve dudas o agenda tu cita al instante por WhatsApp o calendario en tiempo real, las 24 horas del día.
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-2">
              <a
                href="https://wa.me/?text=Hola%2C%20quisiera%20agendar%20una%20consulta%20de%20evaluaci%C3%B3n"
                target="_blank"
                rel="noopener noreferrer"
                className="w-full sm:w-auto flex items-center justify-center gap-2.5 bg-cyan-bright hover:bg-cyan-bright/90 text-sapphire-950 font-bold text-sm px-6 py-3.5 rounded-xl transition-all duration-200 shadow-cyan-glow hover:scale-102 focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
                aria-label="Chatear con el asistente clínico en WhatsApp y reservar turno"
              >
                <MessageCircle className="w-4 h-4 fill-current" />
                <span>Agendar por WhatsApp</span>
                <ArrowRight className="w-4 h-4 ml-1" />
              </a>

              <a
                href="#agendar"
                className="w-full sm:w-auto flex items-center justify-center gap-2 bg-white/10 hover:bg-white/15 text-white border border-white/20 font-semibold text-sm px-6 py-3.5 rounded-xl transition-colors backdrop-blur-md focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-bright"
              >
                <Calendar className="w-4 h-4 text-cyan-bright" />
                <span>Ver Disponibilidad de Turnos</span>
              </a>
            </div>

            {/* Social Proof & Guarantee */}
            <div className="pt-4 flex flex-wrap items-center justify-center lg:justify-start gap-6 border-t border-white/10 text-xs text-slate-400">
              <div className="flex items-center gap-1.5">
                <div className="flex text-amber-400">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-3.5 h-3.5 fill-current" />
                  ))}
                </div>
                <span className="font-bold text-white">4.9 / 5</span>
                <span>(1,200+ pacientes felices)</span>
              </div>

              <div className="flex items-center gap-1.5 text-slate-300">
                <ShieldCheck className="w-4 h-4 text-cyan-bright" />
                <span>Odontólogos matriculados</span>
              </div>

              <div className="flex items-center gap-1.5 text-slate-300">
                <Clock className="w-4 h-4 text-cyan-bright" />
                <span>Turnos de 45 min sin demoras</span>
              </div>
            </div>

          </div>

          {/* Right Column: 3D Mascot Viewport (5 cols) */}
          <div className="lg:col-span-5 flex justify-center">
            <div className="relative w-full max-w-[420px] aspect-square flex items-center justify-center">
              
              {/* Radial Halo Behind Mascot */}
              <div className="absolute inset-0 bg-gradient-to-tr from-cyan-bright/25 via-sapphire-900/40 to-transparent rounded-full blur-2xl -z-10 animate-pulse" />
              
              {/* Floating Glass Container */}
              <div className="relative w-full h-full rounded-3xl border border-cyan-bright/20 bg-sapphire-900/30 backdrop-blur-md p-6 flex flex-col items-center justify-between shadow-glass-card group overflow-hidden">
                
                {/* Decorative Top Pill */}
                <div className="w-full flex items-center justify-between text-[11px] font-semibold text-slate-400 border-b border-white/10 pb-3">
                  <span className="flex items-center gap-1.5 text-cyan-bright">
                    <span className="w-2 h-2 rounded-full bg-cyan-bright animate-ping" />
                    Lumi • Asistente Virtual 3D
                  </span>
                  <span className="text-[10px] bg-white/10 px-2 py-0.5 rounded text-slate-300">IA Activa 24/7</span>
                </div>

                {/* 3D RENDER PLACEHOLDER (NANO BANA2) */}
                {/* INSTRUCCIÓN: Cuando generes el render 3D con Nano Bana2, guárdalo en /public/images/3d/lumina-mascot-3d.webp y sustituye este contenedor con <Image src="/images/3d/lumina-mascot-3d.webp" alt="Lumi mascota 3D" width={420} height={420} priority className="object-contain" /> */}
                <div 
                  className="w-full flex-1 aspect-square bg-slate-900/60 border border-cyan-bright/30 rounded-2xl animate-pulse flex flex-col items-center justify-center text-center p-6 my-3 relative overflow-hidden group-hover:border-cyan-bright/60 transition-colors"
                  role="img"
                  aria-label="Render 3D Nano Bana2: Mascota Dental Lumi en porcelana translúcida con visor holográfico cian y halo sapphire"
                >
                  <div className="w-16 h-16 rounded-2xl bg-cyan-bright/10 border border-cyan-bright/40 flex items-center justify-center text-cyan-bright mb-3">
                    <Sparkles className="w-8 h-8 drop-shadow-[0_0_12px_rgba(0,229,255,0.8)]" />
                  </div>
                  <p className="font-bold text-xs text-white uppercase tracking-wider">
                    Render 3D Nano Bana2: [Mascota Dental 3D "Lumi"]
                  </p>
                  <p className="text-[11px] text-slate-400 mt-1 max-w-[240px]">
                    Aspect Ratio: <strong>1:1</strong> (Cuadrado 1024x1024px, fondo transparente)
                  </p>
                  <span className="mt-3 text-[10px] font-mono text-cyan-bright/90 bg-cyan-bright/10 px-2 py-0.5 rounded border border-cyan-bright/20">
                    /public/images/3d/lumina-mascot-3d.webp
                  </span>
                </div>

                {/* Micro Bottom Status Card */}
                <div className="w-full bg-sapphire-950/80 border border-white/10 rounded-xl p-2.5 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                    <span className="text-slate-200 font-medium text-[11px]">Responde en &lt; 3 seg</span>
                  </div>
                  <span className="text-[10px] text-cyan-bright font-bold">Google Calendar Sincronizado</span>
                </div>

              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
