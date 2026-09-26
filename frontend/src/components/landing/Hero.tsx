'use client';

import React from 'react';
import Image from 'next/image';
import { Calendar, MessageCircle, Sparkles, Star, ShieldCheck, ArrowRight, Clock, CheckCircle2 } from 'lucide-react';

export default function Hero() {
  return (
    <section 
      aria-label="Presentación principal de Lumina Dental Studio"
      className="relative pt-8 pb-20 md:pt-16 md:pb-28 overflow-hidden"
    >
      {/* Ambient Glows */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[650px] bg-sapphire-900/40 rounded-full blur-[140px] -z-10 pointer-events-none" />
      <div className="absolute top-1/3 right-10 w-[450px] h-[450px] bg-cyan-bright/15 rounded-full blur-[130px] -z-10 pointer-events-none" />

      {/* Subtle Cover Backdrop Texture */}
      <div className="absolute top-0 right-0 w-full md:w-3/5 h-[500px] opacity-15 pointer-events-none -z-20 overflow-hidden">
        <Image
          src="/social-kit/lumina-cover.png"
          alt="Lumina Dental Studio Atmosphere"
          fill
          sizes="(max-width: 768px) 100vw, 60vw"
          className="object-cover object-center mask-radial"
          priority
        />
        <div className="absolute inset-0 bg-gradient-to-r from-abyssal via-abyssal/80 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-t from-abyssal via-transparent to-transparent" />
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          
          {/* Left Column: Text & CTAs (7 cols) */}
          <div className="lg:col-span-7 space-y-6 text-center lg:text-left">
            
            {/* Value Badge */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full glass-badge text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5 animate-pulse" />
              <span>Odontología de Precisión & Asistente IA 24/7</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold text-white tracking-tight leading-[1.12]">
              Tu sonrisa en manos expertas.{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-bright via-teal-300 to-white">
                Tu turno agendado en segundos.
              </span>
            </h1>

            {/* Subheading */}
            <p className="text-titanium-300 text-sm sm:text-base lg:text-lg max-w-xl mx-auto lg:mx-0 leading-relaxed font-normal">
              Atención odontológica integral con tecnología digital de última generación. Consulta aranceles, aclara dudas clínicas o agenda tu cita médica al instante en Google Calendar vía WhatsApp, las 24 horas del día.
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-2">
              <a
                href="https://wa.me/?text=Hola%2C%20quisiera%20agendar%20una%20consulta%20de%20evaluaci%C3%B3n%20en%20Lumina%20Dental%20Studio"
                target="_blank"
                rel="noopener noreferrer"
                className="w-full sm:w-auto flex items-center justify-center gap-2.5 bg-cyan-bright hover:bg-cyan-bright/90 text-abyssal font-bold text-sm px-6 py-3.5 rounded-xl transition-all duration-200 shadow-cyan-glow hover:scale-102 focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
                aria-label="Agendar por WhatsApp - Chatear con el asistente clínico y reservar turno"
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
            <div className="pt-4 flex flex-wrap items-center justify-center lg:justify-start gap-6 border-t border-white/10 text-xs text-titanium-400">
              <div className="flex items-center gap-1.5">
                <div className="flex text-amber-400">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-3.5 h-3.5 fill-current" />
                  ))}
                </div>
                <span className="font-bold text-white">4.9 / 5</span>
                <span>(1,200+ pacientes atendidos)</span>
              </div>

              <div className="flex items-center gap-1.5 text-titanium-300">
                <ShieldCheck className="w-4 h-4 text-cyan-bright" />
                <span>Odontólogos matriculados</span>
              </div>

              <div className="flex items-center gap-1.5 text-titanium-300">
                <Clock className="w-4 h-4 text-cyan-bright" />
                <span>Turnos de 45 min sin demoras</span>
              </div>
            </div>

          </div>

          {/* Right Column: 3D Emblem & Clinic Viewport (5 cols) */}
          <div className="lg:col-span-5 flex justify-center">
            <div className="relative w-full max-w-[420px] aspect-square flex items-center justify-center">
              
              {/* Radial Halo Behind Emblem */}
              <div className="absolute inset-0 bg-gradient-to-tr from-cyan-bright/30 via-sapphire-900/50 to-transparent rounded-full blur-3xl -z-10 animate-pulse-subtle" />
              
              {/* Floating Glass Container */}
              <div className="relative w-full h-full rounded-3xl border border-cyan-bright/30 glass-card gpu-layer p-6 flex flex-col items-center justify-between group overflow-hidden shadow-2xl">
                
                {/* Decorative Top Pill */}
                <div className="w-full flex items-center justify-between text-[11px] font-semibold text-titanium-300 border-b border-white/10 pb-3">
                  <span className="flex items-center gap-1.5 text-cyan-bright">
                    <span className="w-2 h-2 rounded-full bg-cyan-bright animate-ping" />
                    Lumi • Asistente Virtual 3D
                  </span>
                  <span className="text-[10px] bg-cyan-bright/10 text-cyan-bright border border-cyan-bright/30 px-2 py-0.5 rounded font-mono">
                    IA Activa 24/7
                  </span>
                </div>

                {/* 3D EMBLEM DISPLAY (1024x1024 Render) */}
                <div className="relative w-full flex-1 aspect-square rounded-2xl overflow-hidden my-3 border border-cyan-bright/30 group-hover:border-cyan-bright/60 transition-all duration-300 shadow-inner bg-abyssal/80">
                  <Image
                    src="/social-kit/lumina-logo.png"
                    alt="Lumina Dental Studio 3D Emblem"
                    fill
                    sizes="(max-width: 768px) 380px, 420px"
                    className="object-contain p-4 group-hover:scale-105 transition-transform duration-500"
                    priority
                  />
                  <div className="absolute inset-0 bg-radial from-cyan-bright/10 via-transparent to-transparent pointer-events-none" />
                </div>

                {/* Micro Bottom Status Card */}
                <div className="w-full bg-sapphire-950/90 border border-cyan-bright/20 rounded-xl p-3 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                    <span className="text-white font-medium text-[11px]">Responde en &lt; 3 seg</span>
                  </div>
                  <span className="text-[10px] text-cyan-bright font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3 text-cyan-bright" />
                    Google Calendar Sincronizado
                  </span>
                </div>

              </div>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
