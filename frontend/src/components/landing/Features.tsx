'use client';

import React from 'react';
import Image from 'next/image';
import { Calendar, ArrowRight, Zap, Shield, Sparkles, CheckCircle2, Tag } from 'lucide-react';

const TREATMENTS_DATA = [
  {
    id: 'blanqueamiento-laser',
    title: 'Blanqueamiento Dental Láser',
    category: 'Estética Dental',
    price: '$90 a $150 USD',
    subtitle: 'Fotoactivación en Frío de Alta Precisión',
    description: 'Elimina manchas severas de café y tabaco en una sola sesión clínica de 45 minutos. Fórmula protectora que previene la sensibilidad gingival.',
    image: '/social-kit/ig-post-blanqueamiento.png',
    features: ['Sesión única de 45 min', 'Hasta 8 tonos más blanco', 'Cero sensibilidad posterior'],
    badge: 'Popular',
    accent: 'border-cyan-bright/40 text-cyan-bright',
  },
  {
    id: 'implantes-guiados-3d',
    title: 'Implantes de Titanio y Zafiro 3D',
    category: 'Implantología Digital',
    price: '$350 a $600 USD',
    subtitle: 'Planificación Tomográfica Computarizada',
    description: 'Fijación de implantes de titanio y coronas de zafiro de grado quirúrgico con guías 3D. Cirugía mínimamente invasiva con recuperación acelerada.',
    image: '/social-kit/ig-post-implantes.png',
    features: ['Guía quirúrgica 3D', 'Titanio y zafiro biocompatible', 'Recuperación express'],
    badge: 'Alta Complejidad',
    accent: 'border-teal-400/40 text-teal-300',
  },
  {
    id: 'urgencias-triage-247',
    title: 'Guardia de Urgencias Odontológicas 24/7',
    category: 'Guardia Inmediata',
    price: 'Triage inmediato',
    subtitle: 'Priorización y Alivio Inmediato',
    description: 'Asistencia prioritaria para dolor agudo, inflamación o traumatismos. Nuestro agente inteligente evalúa el cuadro y bloquea un turno de urgencia en Calendar.',
    image: '/social-kit/ig-post-urgencias.png',
    features: ['Atención en el día', 'Triage instantáneo vía WhatsApp', 'Protocolo anti-dolor'],
    badge: '24 Horas',
    accent: 'border-rose-400/40 text-rose-300',
  }
];

export default function Features() {
  const handleSelectTreatment = (treatmentTitle: string) => {
    if (typeof window !== 'undefined') {
      window.dispatchEvent(
        new CustomEvent('lumina:select-treatment', {
          detail: { treatment: treatmentTitle }
        })
      );
      const bookingSection = document.getElementById('agendar');
      if (bookingSection) {
        bookingSection.scrollIntoView({ behavior: 'smooth' });
      }
    }
  };

  return (
    <section 
      id="tratamientos"
      aria-label="Vitrina 3D de tratamientos y servicios clínicos de Lumina Dental Studio"
      className="py-16 md:py-24 relative overflow-hidden"
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-16">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full glass-badge text-xs font-bold uppercase tracking-wider">
            <Zap className="w-3.5 h-3.5" />
            <span>Tratamientos & Odontología Avanzada</span>
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
            Excelencia clínica respaldada por{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-bright to-teal-300">
              tecnología digital y robótica
            </span>
          </h2>
          <p className="text-titanium-300 text-sm sm:text-base leading-relaxed">
            Explora nuestros tratamientos principales con aranceles transparentes. Selecciona el servicio que necesitas y nuestro sistema coordinará tu cita directamente en la agenda médica.
          </p>
        </div>

        {/* 3D Showcase Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {TREATMENTS_DATA.map((treatment) => (
            <div
              key={treatment.id}
              className="group rounded-3xl overflow-hidden glass-card gpu-layer hover:border-cyan-bright/50 transition-all duration-300 hover:-translate-y-1.5 flex flex-col justify-between shadow-2xl relative"
            >
              {/* Image Container with Zoom Effect */}
              <div className="relative w-full aspect-square overflow-hidden bg-abyssal">
                <Image
                  src={treatment.image}
                  alt={treatment.title}
                  fill
                  sizes="(max-width: 768px) 100vw, 33vw"
                  className="object-cover group-hover:scale-108 transition-transform duration-500"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-sapphire-950 via-sapphire-950/20 to-transparent" />
                
                {/* Badge Tag */}
                <div className="absolute top-4 left-4">
                  <span className="px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider bg-sapphire-950/80 backdrop-blur-md text-white border border-white/20">
                    {treatment.category}
                  </span>
                </div>
                
                <div className="absolute top-4 right-4">
                  <span className={`px-2.5 py-1 rounded-full text-[10px] font-mono font-bold uppercase bg-abyssal/90 backdrop-blur-md border ${treatment.accent}`}>
                    {treatment.badge}
                  </span>
                </div>

                {/* Price Overlay Bar */}
                <div className="absolute bottom-3 left-4 right-4">
                  <div className="flex items-center justify-between px-3 py-1.5 rounded-xl bg-sapphire-950/85 backdrop-blur-md border border-cyan-bright/30 text-xs">
                    <span className="text-titanium-400 flex items-center gap-1 font-medium">
                      <Tag className="w-3 h-3 text-cyan-bright" /> Arancel est.:
                    </span>
                    <span className="font-bold text-cyan-bright font-mono">
                      {treatment.price}
                    </span>
                  </div>
                </div>
              </div>

              {/* Card Body */}
              <div className="p-6 flex-1 flex flex-col justify-between space-y-4 bg-sapphire-950/70">
                <div className="space-y-2">
                  <span className="text-[11px] font-mono text-cyan-bright font-semibold uppercase tracking-wider">
                    {treatment.subtitle}
                  </span>
                  <h3 className="text-xl font-bold text-white group-hover:text-cyan-bright transition-colors">
                    {treatment.title}
                  </h3>
                  <p className="text-titanium-300 text-xs sm:text-sm leading-relaxed">
                    {treatment.description}
                  </p>
                </div>

                {/* Micro Features List */}
                <div className="space-y-2 pt-3 border-t border-white/10">
                  {treatment.features.map((feat, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-xs text-titanium-300">
                      <CheckCircle2 className="w-3.5 h-3.5 text-cyan-bright shrink-0" />
                      <span>{feat}</span>
                    </div>
                  ))}
                </div>

                {/* Action CTA: Agendar este tratamiento */}
                <div className="pt-4">
                  <button
                    type="button"
                    onClick={() => handleSelectTreatment(treatment.title)}
                    className="w-full py-3 px-4 rounded-xl bg-white/10 hover:bg-cyan-bright hover:text-abyssal text-white font-bold text-xs flex items-center justify-center gap-2 transition-all duration-200 border border-white/15 hover:border-cyan-bright shadow-xs cursor-pointer group/btn"
                  >
                    <Calendar className="w-4 h-4 text-cyan-bright group-hover/btn:text-abyssal transition-colors" />
                    <span>Agendar este tratamiento</span>
                    <ArrowRight className="w-3.5 h-3.5 ml-1 group-hover/btn:translate-x-1 transition-transform" />
                  </button>
                </div>

              </div>

            </div>
          ))}
        </div>

      </div>
    </section>
  );
}
