'use client';

import React from 'react';
import { Users, Clock, Zap, ShieldCheck } from 'lucide-react';

const METRICS = [
  {
    icon: Users,
    value: '+1,200',
    label: 'Pacientes Satisfechos',
    detail: 'Atención personalizada en cada consulta'
  },
  {
    icon: Clock,
    value: '45 min',
    label: 'Turnos Dedicados',
    detail: 'Atención puntual sin salas de espera llenas'
  },
  {
    icon: Zap,
    value: '< 3 seg',
    label: 'Tiempo de Respuesta',
    detail: 'Triaje instantáneo en WhatsApp y redes'
  },
  {
    icon: ShieldCheck,
    value: '100%',
    label: 'Odontólogos Matriculados',
    detail: 'Equipamiento digital de alta precisión'
  }
];

export default function TrustMetrics() {
  return (
    <section 
      aria-label="Indicadores de confianza y calidad clínica"
      className="py-12 border-y border-white/10 bg-sapphire-950/60 backdrop-blur-md"
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 lg:gap-8">
          {METRICS.map((metric, i) => {
            const Icon = metric.icon;
            return (
              <div 
                key={i} 
                className="text-center md:text-left flex flex-col items-center md:items-start p-4 rounded-2xl bg-white/5 border border-white/5 hover:border-cyan-bright/30 transition-colors group"
              >
                <div className="w-10 h-10 rounded-xl bg-cyan-bright/10 text-cyan-bright flex items-center justify-center mb-3 group-hover:scale-110 transition-transform">
                  <Icon className="w-5 h-5" />
                </div>
                <span className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                  {metric.value}
                </span>
                <span className="text-xs sm:text-sm font-bold text-cyan-bright mt-0.5">
                  {metric.label}
                </span>
                <p className="text-[11px] text-slate-400 mt-1">
                  {metric.detail}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
