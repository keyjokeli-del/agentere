'use client';

import React from 'react';
import { Bot, CalendarCheck, Share2, Award, Zap, Shield, Sparkles } from 'lucide-react';

const FEATURES_DATA = [
  {
    id: 'triage-ai',
    title: 'Triaje Clínico Inmediato 24/7',
    subtitle: 'Groq Llama 3.3',
    description: 'Comprende el motivo de consulta con precisión humana. Prioriza dolor agudo e inflamación y orienta al paciente sin diagnósticos vinculantes riesgosos.',
    tag: 'Triage de Urgencias',
    icon: Bot,
    glowColor: 'group-hover:border-cyan-bright/50'
  },
  {
    id: 'anti-collision-calendar',
    title: 'Agenda Google Calendar Anti-Colisión',
    subtitle: 'Franjas de 45 min',
    description: 'Calcula dinámicamente turnos libres entre 09:00 y 19:00 hs. Bloquea colisiones al instante y ofrece alternativas automáticas si un horario ya fue reservado.',
    tag: 'Cero Duplicados',
    icon: CalendarCheck,
    glowColor: 'group-hover:border-teal-400/50'
  },
  {
    id: 'omnichannel-zero-cost',
    title: 'Atención Omnicanal a Costo $0',
    subtitle: 'WhatsApp • Meta • YouTube',
    description: 'Tus pacientes escriben por WhatsApp (Baileys con persistencia en Neon), Facebook Messenger, Instagram Direct o comentarios de YouTube con respuesta instantánea.',
    tag: 'Sin Costos Mensuales',
    icon: Share2,
    glowColor: 'group-hover:border-blue-400/50'
  },
  {
    id: 'clinical-precision',
    title: 'Odontología de Precisión',
    subtitle: 'Profesionales Matriculados',
    description: 'Equipamiento digital de última generación para limpiezas, blanqueamientos, ortodoncia invisible y rehabilitación integral con presupuesto transparente.',
    tag: 'Calidad Médica',
    icon: Award,
    glowColor: 'group-hover:border-cyan-bright/50'
  }
];

export default function Features() {
  return (
    <section 
      id="tratamientos"
      aria-label="Pilares y características del servicio Lumina"
      className="py-16 md:py-24 relative overflow-hidden"
    >
      {/* Background Accent Lines */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-badge text-xs font-bold uppercase tracking-wider">
            <Zap className="w-3.5 h-3.5" />
            <span>Innovación al Servicio del Paciente</span>
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
            La combinación perfecta entre{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-bright to-teal-300">
              atención médica de excelencia
            </span>{' '}
            e inteligencia artificial
          </h2>
          <p className="text-slate-400 text-sm sm:text-base leading-relaxed">
            Eliminamos las esperas telefónicas y la falta de respuesta. Desde tu primer mensaje hasta la atención en el sillón odontológico, cada paso está diseñado para tu comodidad.
          </p>
        </div>

        {/* 4 Pillars Grid (Glassmorphism Cards) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8">
          {FEATURES_DATA.map((feat) => {
            const Icon = feat.icon;
            return (
              <div
                key={feat.id}
                className={`group relative rounded-3xl p-7 glass-card gpu-layer hover:border-cyan-bright/40 transition-all duration-300 hover:-translate-y-1 overflow-hidden ${feat.glowColor}`}
              >
                {/* Subtle Inner Glow on Hover */}
                <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-bright/5 rounded-full blur-2xl group-hover:bg-cyan-bright/15 transition-all duration-500 pointer-events-none" />

                <div className="flex items-start justify-between mb-5">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-sapphire-800 to-sapphire-950 border border-cyan-bright/30 flex items-center justify-center text-cyan-bright shadow-inner group-hover:scale-110 transition-transform duration-300">
                    <Icon className="w-6 h-6" />
                  </div>
                  <span className="text-[11px] font-bold uppercase tracking-wider px-3 py-1 rounded-full bg-white/5 text-cyan-bright border border-white/10">
                    {feat.tag}
                  </span>
                </div>

                <div className="space-y-2">
                  <span className="text-xs font-mono font-semibold text-cyan-bright/80 tracking-wide uppercase">
                    {feat.subtitle}
                  </span>
                  <h3 className="text-lg sm:text-xl font-bold text-white group-hover:text-cyan-bright transition-colors">
                    {feat.title}
                  </h3>
                  <p className="text-slate-300 text-xs sm:text-sm leading-relaxed pt-1">
                    {feat.description}
                  </p>
                </div>

                {/* Micro Guarantee Bullet */}
                <div className="mt-6 pt-4 border-t border-white/10 flex items-center gap-2 text-xs text-slate-400 font-medium">
                  <Shield className="w-3.5 h-3.5 text-teal-400" />
                  <span>Protocolo certificado de confidencialidad médica</span>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
