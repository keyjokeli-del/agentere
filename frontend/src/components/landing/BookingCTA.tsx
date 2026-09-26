'use client';

import React, { useState, useEffect } from 'react';
import { Calendar, Clock, MessageCircle, Sparkles, CheckCircle2, ArrowRight, Stethoscope, Download, User, Phone } from 'lucide-react';

const POPULAR_TREATMENTS = [
  'Consulta Odontológica General',
  'Blanqueamiento Dental Láser',
  'Implantes de Titanio y Zafiro 3D',
  'Guardia de Urgencias Odontológicas 24/7',
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

  // Direct 2-click booking state (Mejora 22)
  const [patientName, setPatientName] = useState<string>('');
  const [patientPhone, setPatientPhone] = useState<string>('');
  const [isBooking, setIsBooking] = useState<boolean>(false);
  const [bookingSuccess, setBookingSuccess] = useState<any>(null);
  const [bookingError, setBookingError] = useState<string>('');

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
        const res = await fetch(`${BACKEND_URL}/api/slots?target_date=${selectedDate}&treatment=${encodeURIComponent(selectedTreatment)}`);
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
  }, [selectedDate, selectedTreatment, BACKEND_URL]);

  const handleDirectBooking = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!patientName.trim() || !patientPhone.trim() || !selectedSlot) {
      setBookingError('Por favor completa tu nombre, teléfono y selecciona un horario.');
      return;
    }
    setBookingError('');
    setIsBooking(true);

    try {
      const res = await fetch(`${BACKEND_URL}/api/appointments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_name: patientName.trim(),
          contact: patientPhone.trim(),
          treatment: selectedTreatment,
          date: selectedDate,
          time: selectedSlot,
          channel: 'web'
        })
      });

      if (res.ok) {
        const data = await res.json();
        setBookingSuccess(data);
      } else {
        const errData = await res.json();
        setBookingError(errData.detail || 'El horario solicitado no se encuentra disponible. Por favor elige otro.');
      }
    } catch {
      setBookingError('Error de conexión con el servidor de citas. Por favor intenta por WhatsApp.');
    } finally {
      setIsBooking(false);
    }
  };

  const whatsappMessage = encodeURIComponent(
    `Hola! Me gustaría reservar un turno para ${selectedTreatment} en Lumina Dental Studio el día ${selectedDate} a las ${selectedSlot || '09:00'} hs. Mi nombre es ${patientName || 'Paciente'}.`
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

          <div className="relative grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            {/* Left Column: Heading & Value Proposition */}
            <div className="lg:col-span-7 space-y-5 text-center lg:text-left">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full glass-badge text-xs font-bold uppercase tracking-wider">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Reserva Inteligente en Tiempo Real (2 Clics)</span>
              </span>

              <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
                ¿Listo para transformar tu sonrisa?{' '}
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-bright to-teal-300">
                  Elige tu turno y confirma de inmediato.
                </span>
              </h2>

              {/* Treatment Selector Chips */}
              <div className="space-y-2 pt-2">
                <label className="text-xs font-bold text-titanium-300 uppercase tracking-wider flex items-center gap-1.5 justify-center lg:justify-start">
                  <Stethoscope className="w-3.5 h-3.5 text-cyan-bright" />
                  <span>Tratamiento Solicitado:</span>
                </label>
                <div className="flex flex-wrap gap-2 justify-center lg:justify-start">
                  {POPULAR_TREATMENTS.map(t => (
                    <button
                      key={t}
                      type="button"
                      onClick={() => setSelectedTreatment(t)}
                      className={`text-xs px-3.5 py-1.5 rounded-full font-medium transition-all ${
                        selectedTreatment === t
                          ? 'bg-cyan-bright text-abyssal font-bold shadow-cyan-glow scale-102'
                          : 'bg-white/5 hover:bg-white/10 text-titanium-300 border border-white/10'
                      }`}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>

              {/* Highlights */}
              <div className="grid grid-cols-3 gap-3 pt-4 border-t border-white/10 text-left">
                <div>
                  <div className="text-cyan-bright font-bold text-sm">30–90 min</div>
                  <div className="text-[11px] text-titanium-400">Duración calibrada</div>
                </div>
                <div>
                  <div className="text-cyan-bright font-bold text-sm">0 Colisiones</div>
                  <div className="text-[11px] text-titanium-400">Google Calendar</div>
                </div>
                <div>
                  <div className="text-cyan-bright font-bold text-sm">100% Gratuito</div>
                  <div className="text-[11px] text-titanium-400">Evaluación inicial</div>
                </div>
              </div>
            </div>

            {/* Right Column: Interactive Slot Selector & Direct Booking */}
            <div className="lg:col-span-5 bg-sapphire-950/90 border border-cyan-bright/25 rounded-2xl p-6 shadow-xl space-y-4">
              
              {bookingSuccess ? (
                <div className="space-y-4 text-center py-4 animate-in fade-in zoom-in-95 duration-300">
                  <div className="w-14 h-14 rounded-full bg-emerald-500/20 border border-emerald-400 flex items-center justify-center mx-auto text-emerald-400">
                    <CheckCircle2 className="w-8 h-8" />
                  </div>
                  <h3 className="text-lg font-bold text-white">¡Cita Confirmada con Éxito!</h3>
                  <div className="bg-sapphire-900/60 border border-cyan-bright/20 rounded-xl p-3.5 text-xs text-titanium-300 text-left space-y-1">
                    <p><strong className="text-white">Paciente:</strong> {bookingSuccess.patient_name}</p>
                    <p><strong className="text-white">Fecha:</strong> {bookingSuccess.date} a las {bookingSuccess.time} hs</p>
                    <p><strong className="text-white">Tratamiento:</strong> {bookingSuccess.treatment}</p>
                  </div>

                  <div className="flex flex-col gap-2 pt-2">
                    <a
                      href={`${BACKEND_URL}/api/appointments/ics?appt_id=${bookingSuccess.id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center gap-2 w-full py-2.5 px-4 rounded-xl bg-cyan-bright text-abyssal font-bold text-xs hover:scale-102 transition shadow-cyan-glow"
                    >
                      <Download className="w-4 h-4" />
                      Descargar recordatorio .ics
                    </a>
                    <a
                      href={`https://wa.me/5491123456789?text=${whatsappMessage}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center gap-2 w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition"
                    >
                      <MessageCircle className="w-4 h-4" />
                      Abrir en WhatsApp
                    </a>
                    <button
                      type="button"
                      onClick={() => setBookingSuccess(null)}
                      className="text-xs text-titanium-400 hover:text-white pt-1 transition"
                    >
                      Agendar otro turno
                    </button>
                  </div>
                </div>
              ) : (
                <form onSubmit={handleDirectBooking} className="space-y-4">
                  {/* Date Input */}
                  <div className="space-y-1">
                    <label 
                      htmlFor="booking-date" 
                      className="text-xs font-bold text-titanium-300 flex items-center gap-1.5"
                    >
                      <Calendar className="w-3.5 h-3.5 text-cyan-bright" />
                      <span>1. Seleccionar Fecha:</span>
                    </label>
                    <input
                      id="booking-date"
                      type="date"
                      value={selectedDate}
                      min={new Date().toISOString().split('T')[0]}
                      onChange={e => setSelectedDate(e.target.value)}
                      className="w-full bg-sapphire-900/60 border border-white/20 rounded-xl px-3.5 py-2 text-xs font-semibold text-white focus:outline-none focus:ring-2 focus:ring-cyan-bright"
                    />
                  </div>

                  {/* Slots Grid */}
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-titanium-300 flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5 text-cyan-bright" />
                        <span>2. Horarios Libres:</span>
                      </span>
                      <span className="text-[10px] text-cyan-bright font-mono">
                        {loadingSlots ? 'Buscando...' : `${slots.length} libres`}
                      </span>
                    </div>

                    <div className="grid grid-cols-3 gap-1.5 max-h-32 overflow-y-auto pr-1">
                      {loadingSlots ? (
                        Array.from({ length: 6 }).map((_, i) => (
                          <div key={i} className="h-8 rounded-lg bg-white/5 border border-white/10 animate-pulse" />
                        ))
                      ) : slots.length === 0 ? (
                        <span className="col-span-3 text-[11px] text-titanium-400 italic py-4 text-center">
                          Sin turnos disponibles en esta fecha.
                        </span>
                      ) : (
                        slots.map((slot, i) => (
                          <button
                            key={i}
                            type="button"
                            onClick={() => setSelectedSlot(slot)}
                            className={`py-1.5 px-2 rounded-lg text-xs font-mono font-bold transition-all ${
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

                  {/* Patient Name & Phone Inputs (Mejora 22) */}
                  <div className="space-y-2 pt-1 border-t border-white/10">
                    <div className="space-y-1">
                      <label className="text-[11px] font-bold text-titanium-300 flex items-center gap-1.5">
                        <User className="w-3 h-3 text-cyan-bright" />
                        <span>Nombre y Apellido:</span>
                      </label>
                      <input
                        type="text"
                        required
                        placeholder="Ej. Valentina Morales"
                        value={patientName}
                        onChange={e => setPatientName(e.target.value)}
                        className="w-full bg-sapphire-900/60 border border-white/20 rounded-xl px-3 py-1.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-cyan-bright"
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-[11px] font-bold text-titanium-300 flex items-center gap-1.5">
                        <Phone className="w-3 h-3 text-cyan-bright" />
                        <span>Teléfono / WhatsApp:</span>
                      </label>
                      <input
                        type="tel"
                        required
                        placeholder="Ej. +54 9 11 2345-6789"
                        value={patientPhone}
                        onChange={e => setPatientPhone(e.target.value)}
                        className="w-full bg-sapphire-900/60 border border-white/20 rounded-xl px-3 py-1.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-cyan-bright"
                      />
                    </div>
                  </div>

                  {bookingError && (
                    <div className="p-2 rounded-lg bg-red-500/20 border border-red-500/40 text-red-200 text-[11px]">
                      {bookingError}
                    </div>
                  )}

                  {/* Direct 2-Click Confirm Button */}
                  <button
                    type="submit"
                    disabled={isBooking || !selectedSlot}
                    className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-cyan-bright via-teal-400 to-cyan-500 text-abyssal-950 font-extrabold text-xs flex items-center justify-center gap-2 shadow-cyan-glow hover:scale-102 active:scale-98 transition disabled:opacity-50 disabled:pointer-events-none"
                  >
                    <CheckCircle2 className="w-4 h-4 text-abyssal-950" />
                    <span>{isBooking ? 'Confirmando con IA...' : 'Confirmar Reserva Inmediata'}</span>
                  </button>

                  <p className="text-[10px] text-center text-titanium-400">
                    Sincronización anti-colisión en tiempo real con Google Calendar.
                  </p>
                </form>
              )}

            </div>

          </div>

        </div>

      </div>
    </section>
  );
}
