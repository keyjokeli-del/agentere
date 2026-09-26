'use client';

import React, { useState, useEffect } from 'react';
import { Calendar, Clock, MessageCircle, Sparkles, CheckCircle2, ArrowRight, Stethoscope } from 'lucide-react';

const POPULAR_TREATMENTS = [
  'Consulta Odontológica General',
  'Blanqueamiento Dental Láser',
  'Implantes Guiados 3D',
  'Triage de Urgencias 24/7',
  'Limpieza y Profilaxis Ultrasónica'
];

export default function BookingCTA() {
  const [selectedTreatment, setSelectedTreatment] = useState<string>('Consulta Odontológica General');
  const [selectedDate, setSelectedDate] = useState<string>(() => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  });
  const [slots, setSlots] = useState<string[]>([]);
  const [loadingSlots, setLoadingSlots] = useState<boolean>(false);
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);

  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  // Listen to treatment selection dispatched from Features.tsx
  useEffect(() => {
    const handler = (e: Event) => {
      const customEvent = e as CustomEvent<{ treatment: string }>;
      if (customEvent.detail?.treatment) {
        setSelectedTreatment(customEvent.detail.treatment);
      }
    };
    window.addEventListener('lumina:select-treatment', handler);
    return () => window.removeEventListener('lumina:select-treatment', handler);
  }, []);

  useEffect(() => {
    const fetchSlots = async () => {
      setLoadingSlots(true);
      try {
        const res = await fetch(`${BACKEND_URL}/api/slots?target_date=${selectedDate}`);
        if (res.ok) {
          const data = await res.json();
          setSlots(data.slots || []);
          if (data.slots?.length > 0) {
            setSelectedSlot(data.slots[0]);
          } else {
            setSelectedSlot(null);
          }
        }
      } catch {
        // Fallback default slots if backend is offline
        setSlots(['09:00', '09:45', '10:30', '11:15', '14:15', '15:00', '16:30']);
        setSelectedSlot('09:45');
      } finally {
        setLoadingSlots(false);
      }
    };

    fetchSlots();
  }, [selectedDate, BACKEND_URL]);

  const whatsappMessage = encodeURIComponent(
    `Hola! Me gustaría reservar un turno para ${selectedTreatment} en Lumina Dental Studio el día ${selectedDate} a las ${selectedSlot || '09:00'} hs.`
  );

  return (
    <section 
      id="agendar"
      aria-label="Sección para agendar turno"
      className="py-16 md:py-24 relative overflow-hidden"
    >
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Glow Wrap Box */}
        <div className="relative rounded-3xl p-8 sm:p-12 md:p-14 bg-gradient-to-br from-sapphire-900/90 via-sapphire-950 to-abyssal-950 border border-cyan-bright/35 backdrop-blur-2xl shadow-[0_0_50px_rgba(0,229,255,0.12)] overflow-hidden">
          
          {/* Subtle Ambient Radial Lights */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-bright/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-sapphire-800/25 rounded-full blur-3xl pointer-events-none" />

          <div className="relative grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            
            {/* Left Column: Heading & Value Proposition */}
            <div className="lg:col-span-7 space-y-5 text-center lg:text-left">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full glass-badge text-xs font-bold uppercase tracking-wider">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Reserva Inteligente en Tiempo Real</span>
              </span>

              <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
                ¿Listo para transformar tu sonrisa?{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-bright to-teal-300">
                  Elige tu turno y tratamiento.
                </span>
              </h2>

              {/* Treatment Selector Chips */}
              <div className="space-y-2 pt-1 text-left">
                <label className="text-xs font-bold text-titanium-300 flex items-center gap-1.5">
                  <Stethoscope className="w-3.5 h-3.5 text-cyan-bright" />
                  <span>Tratamiento seleccionado:</span>
                </label>
                <div className="flex flex-wrap gap-2">
                  {POPULAR_TREATMENTS.map((t, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => setSelectedTreatment(t)}
                      className={`text-xs px-3 py-1.5 rounded-xl font-medium transition-all cursor-pointer ${
                        selectedTreatment === t
                          ? 'bg-cyan-bright text-abyssal font-bold shadow-cyan-glow'
                          : 'bg-white/5 text-titanium-300 hover:bg-white/10 border border-white/10'
                      }`}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>

              <p className="text-titanium-300 text-xs sm:text-sm leading-relaxed max-w-md mx-auto lg:mx-0 pt-2">
                Nuestra agenda en Google Calendar bloquea espacios de 45 minutos sin solapamientos. Selecciona horario y confirma con un clic vía WhatsApp.
              </p>

              <div className="pt-2 flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4">
                <a
                  href={`https://wa.me/?text=${whatsappMessage}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full sm:w-auto flex items-center justify-center gap-2.5 bg-cyan-bright hover:bg-cyan-bright/90 text-abyssal font-bold text-sm px-6 py-3.5 rounded-xl transition-all duration-200 shadow-cyan-glow hover:scale-102 focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
                  aria-label="Confirmar Turno en WhatsApp - Finalizar reserva en consultorio"
                >
                  <MessageCircle className="w-4 h-4 fill-current" />
                  <span>Confirmar Turno en WhatsApp</span>
                  <ArrowRight className="w-4 h-4 ml-1" />
                </a>
              </div>
            </div>

            {/* Right Column: Interactive Slot Selector */}
            <div className="lg:col-span-5 bg-sapphire-950/90 border border-cyan-bright/25 rounded-2xl p-6 shadow-xl space-y-4">
              
              {/* Date Input */}
              <div className="space-y-1.5">
                <label 
                  htmlFor="booking-date" 
                  className="text-xs font-bold text-titanium-300 flex items-center gap-1.5"
                >
                  <Calendar className="w-3.5 h-3.5 text-cyan-bright" />
                  <span>Seleccionar Fecha:</span>
                </label>
                <input
                  id="booking-date"
                  aria-label="Seleccionar fecha para turno odontológico"
                  type="date"
                  value={selectedDate}
                  min={new Date().toISOString().split('T')[0]}
                  onChange={e => setSelectedDate(e.target.value)}
                  className="w-full bg-sapphire-900/60 border border-white/20 rounded-xl px-3.5 py-2.5 text-xs font-semibold text-white focus:outline-none focus:ring-2 focus:ring-cyan-bright"
                />
              </div>

              {/* Slots Grid with Fixed Height & Skeletons (CLS = 0.00) */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-titanium-300 flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-cyan-bright" />
                    <span>Horarios Disponibles (45 min):</span>
                  </span>
                  <span className="text-[10px] text-cyan-bright font-mono">
                    {loadingSlots ? 'Buscando...' : `${slots.length} libres`}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-2 min-h-[148px] max-h-44 overflow-y-auto pr-1 items-start">
                  {loadingSlots ? (
                    Array.from({ length: 6 }).map((_, i) => (
                      <div
                        key={i}
                        className="h-9 rounded-xl bg-white/5 border border-white/10 animate-pulse"
                        aria-hidden="true"
                      />
                    ))
                  ) : slots.length === 0 ? (
                    <span className="col-span-3 text-xs text-titanium-400 italic py-10 text-center">
                      No hay turnos disponibles para esta fecha.
                    </span>
                  ) : (
                    slots.map((slot, i) => (
                      <button
                        key={i}
                        type="button"
                        onClick={() => setSelectedSlot(slot)}
                        className={`py-2 px-2.5 rounded-xl text-xs font-mono font-bold transition-all cursor-pointer ${
                          selectedSlot === slot
                            ? 'bg-cyan-bright text-abyssal shadow-cyan-glow scale-102'
                            : 'bg-white/5 hover:bg-white/10 text-titanium-200 border border-white/10'
                        }`}
                      >
                        {slot} hs
                      </button>
                    ))
                  )}
                </div>
              </div>

              {/* Slot Confirmation helper */}
              {selectedSlot && (
                <div className="pt-2 border-t border-white/10 flex flex-col gap-1 text-xs text-titanium-300">
                  <div className="flex items-center justify-between">
                    <span className="text-titanium-400">Reserva:</span>
                    <span className="font-bold text-cyan-bright flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5 text-cyan-bright" />
                      {selectedDate} a las {selectedSlot} hs
                    </span>
                  </div>
                  <div className="text-[11px] text-titanium-400 truncate">
                    Motivo: <span className="text-white font-medium">{selectedTreatment}</span>
                  </div>
                </div>
              )}

            </div>

          </div>

        </div>

      </div>
    </section>
  );
}
