'use client';

import React, { useState, useMemo } from 'react';
import {
  Calendar as CalendarIcon,
  Clock,
  User,
  Phone,
  CheckCircle2,
  AlertCircle,
  Plus,
  Lock,
  Bell,
  Sparkles,
  ExternalLink,
  ChevronRight,
  Filter,
  Users,
  ShieldCheck,
  Zap,
  X
} from 'lucide-react';
import { Appointment } from '@/types';

interface InteractiveAgendaProps {
  appointments: Appointment[];
  availableSlots: string[];
  selectedDate: string;
  onSelectDate: (date: string) => void;
  loadingSlots: boolean;
  backendUrl: string;
  getAuthHeaders: (extra?: Record<string, string>) => Record<string, string>;
  onRefreshData: () => Promise<void>;
  onInsertSlotIntoChat?: (slot: string, date: string) => void;
  onSelectPatientChat?: (contact: string) => void;
}

export const InteractiveAgenda: React.FC<InteractiveAgendaProps> = ({
  appointments,
  availableSlots,
  selectedDate,
  onSelectDate,
  loadingSlots,
  backendUrl,
  getAuthHeaders,
  onRefreshData,
  onInsertSlotIntoChat,
  onSelectPatientChat
}) => {
  const [durationFilter, setDurationFilter] = useState<number>(45);
  const [doctorFilter, setDoctorFilter] = useState<string>('all');
  const [selectedSlotPopover, setSelectedSlotPopover] = useState<string | null>(null);
  const [briefingModal, setBriefingModal] = useState<{
    isOpen: boolean;
    loading: boolean;
    lines: string[];
    patient: string;
  } | null>(null);
  const [blockModal, setBlockModal] = useState<boolean>(false);
  const [blockReason, setBlockReason] = useState<string>('Esterilización de Autoclave');
  const [blockTime, setBlockTime] = useState<string>('12:00');
  const [reminderStatus, setReminderStatus] = useState<Record<string, string>>({});
  const [waitlistModal, setWaitlistModal] = useState<boolean>(false);
  const [manualBookingModal, setManualBookingModal] = useState<boolean>(false);
  const [manualForm, setManualForm] = useState({
    patient_name: '',
    contact: '',
    treatment: 'Consulta Odontológica y Diagnóstico',
    time: '10:00'
  });

  // Filter confirmed appointments by doctor
  const filteredAppointments = useMemo(() => {
    return appointments.filter((a) => {
      if (doctorFilter !== 'all') {
        const doc = (a.treatment?.toLowerCase().includes('implante') || a.treatment?.toLowerCase().includes('ortodoncia'))
          ? 'Dr. Especialista'
          : 'Dra. Nairoby Domínguez';
        if (doctorFilter !== doc) return false;
      }
      return true;
    });
  }, [appointments, doctorFilter]);

  // Handle Send Reminder
  const handleSendReminder = async (appt: Appointment) => {
    setReminderStatus((prev) => ({ ...prev, [appt.id]: 'sending' }));
    try {
      const res = await fetch(`${backendUrl}/api/dashboard/send-reminder`, {
        method: 'POST',
        headers: getAuthHeaders(),
        credentials: 'include',
        body: JSON.stringify({
          contact: appt.contact,
          patient_name: appt.patient_name,
          appointment_date: appt.date,
          appointment_time: appt.time,
          treatment: appt.treatment
        })
      });
      if (res.ok) {
        setReminderStatus((prev) => ({ ...prev, [appt.id]: 'sent' }));
        setTimeout(() => {
          setReminderStatus((prev) => ({ ...prev, [appt.id]: '' }));
        }, 4000);
      }
    } catch {
      setReminderStatus((prev) => ({ ...prev, [appt.id]: 'error' }));
    }
  };

  // Handle AI Pre-Consultation Briefing
  const handleOpenBriefing = async (appt: Appointment) => {
    setBriefingModal({
      isOpen: true,
      loading: true,
      lines: [],
      patient: appt.patient_name
    });

    try {
      const res = await fetch(`${backendUrl}/api/dashboard/briefing`, {
        method: 'POST',
        headers: getAuthHeaders(),
        credentials: 'include',
        body: JSON.stringify({
          patient_name: appt.patient_name,
          contact: appt.contact,
          treatment: appt.treatment,
          date: appt.date,
          time: appt.time,
          channel: appt.channel
        })
      });

      if (res.ok) {
        const data = await res.json();
        setBriefingModal({
          isOpen: true,
          loading: false,
          lines: data.briefing_lines || [],
          patient: appt.patient_name
        });
      }
    } catch {
      setBriefingModal({
        isOpen: true,
        loading: false,
        lines: ['No se pudo generar el briefing en este momento.'],
        patient: appt.patient_name
      });
    }
  };

  // Handle Block Slot
  const handleBlockSlot = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${backendUrl}/api/dashboard/calendar/block-slot`, {
        method: 'POST',
        headers: getAuthHeaders(),
        credentials: 'include',
        body: JSON.stringify({
          date: selectedDate,
          time: blockTime,
          reason: blockReason,
          duration_min: 45
        })
      });
      if (res.ok) {
        setBlockModal(false);
        await onRefreshData();
      }
    } catch (err) {
      console.error('[BlockSlot] Error:', err);
    }
  };

  // Handle Manual Appointment Create
  const handleManualBookingSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${backendUrl}/api/appointments`, {
        method: 'POST',
        headers: getAuthHeaders(),
        credentials: 'include',
        body: JSON.stringify({
          ...manualForm,
          date: selectedDate,
          channel: 'manual_dashboard'
        })
      });
      if (res.ok) {
        setManualBookingModal(false);
        setManualForm({ patient_name: '', contact: '', treatment: 'Consulta Odontológica', time: '10:00' });
        await onRefreshData();
      }
    } catch (err) {
      console.error('[ManualBooking] Error:', err);
    }
  };

  // Weekly mock occupancy
  const weeklyDays = [
    { day: 'Lun', date: '28', occ: 85 },
    { day: 'Mar', date: '29', occ: 90 },
    { day: 'Mié', date: '30', occ: 75 },
    { day: 'Jue', date: '01', occ: 95 },
    { day: 'Vie', date: '02', occ: 60 },
    { day: 'Sáb', date: '03', occ: 40 }
  ];

  return (
    <div className="space-y-6">
      {/* Top Controls & Occupancy Strip */}
      <div className="glass-card rounded-3xl p-5 border border-cyan-bright/20 bg-sapphire-950/80 shadow-xl space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-teal-500/20 text-teal-300 flex items-center justify-center border border-teal-500/30">
              <CalendarIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-extrabold text-sm text-white flex items-center gap-2">
                Agenda Médica en Tiempo Real
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-teal-500/20 text-teal-300 border border-teal-500/30">
                  Google Calendar API
                </span>
              </h3>
              <p className="text-xs text-titanium-400">Control de sillones, citas confirmadas y sincronización bidireccional</p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* Date Input */}
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => onSelectDate(e.target.value)}
              className="text-xs px-3 py-1.5 rounded-xl bg-black/50 border border-white/15 text-white focus:outline-none focus:border-cyan-bright font-mono"
            />

            {/* Block Slot Action */}
            <button
              onClick={() => setBlockModal(true)}
              className="px-3 py-1.5 rounded-xl bg-rose-500/15 hover:bg-rose-500/25 text-rose-300 border border-rose-500/30 text-xs font-bold transition cursor-pointer flex items-center gap-1.5"
            >
              <Lock className="w-3.5 h-3.5" />
              <span>Bloquear Slot</span>
            </button>

            {/* Quick Manual Booking */}
            <button
              onClick={() => setManualBookingModal(true)}
              className="px-3.5 py-1.5 rounded-xl bg-cyan-bright hover:bg-cyan-bright/90 text-abyssal text-xs font-bold shadow-cyan-glow transition cursor-pointer flex items-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>+ Cita Manual</span>
            </button>
          </div>
        </div>

        {/* Weekly Occupancy Progress Strip (Mejora 37) */}
        <div className="pt-3 border-t border-white/10">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-titanium-300">Ocupación Semanal de Sillones Clínicos</span>
            <span className="text-[10px] font-mono text-cyan-bright">Semana en Curso</span>
          </div>
          <div className="grid grid-cols-6 gap-2">
            {weeklyDays.map((w, idx) => (
              <div key={idx} className="p-2 rounded-xl bg-black/40 border border-white/5 text-center space-y-1">
                <span className="text-[10px] text-titanium-400 block font-mono">
                  {w.day} {w.date}
                </span>
                <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      w.occ >= 90 ? 'bg-rose-400' : w.occ >= 70 ? 'bg-amber-400' : 'bg-emerald-400'
                    }`}
                    style={{ width: `${w.occ}%` }}
                  />
                </div>
                <span className="text-[9px] font-mono font-bold text-white block">{w.occ}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Available Slots Section (Mejora 33, 36, 41) */}
      <div className="glass-card rounded-3xl p-5 border border-cyan-bright/20 bg-sapphire-950/70 shadow-xl space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h4 className="font-extrabold text-sm text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-cyan-bright" />
              <span>Horarios Disponibles para {selectedDate}</span>
            </h4>
            <p className="text-xs text-titanium-400">Haz clic en un horario libre para agendar o insertar en el chat del paciente</p>
          </div>

          {/* Duration Filter (30 / 45 / 90) */}
          <div className="flex items-center gap-1 bg-black/40 p-1 rounded-xl border border-white/10 text-xs">
            {[30, 45, 90].map((dur) => (
              <button
                key={dur}
                onClick={() => setDurationFilter(dur)}
                className={`px-2.5 py-1 rounded-lg font-mono font-bold transition cursor-pointer ${
                  durationFilter === dur ? 'bg-cyan-bright text-abyssal' : 'text-titanium-400 hover:text-white'
                }`}
              >
                {dur}m
              </button>
            ))}
          </div>
        </div>

        {/* Slot Chips Grid */}
        <div className="relative">
          {loadingSlots ? (
            <div className="p-6 text-center text-xs text-cyan-bright animate-pulse">
              Consultando Google Calendar API en tiempo real...
            </div>
          ) : availableSlots.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {availableSlots.map((slot) => {
                const hour = parseInt(slot.split(':')[0], 10);
                const isPrime = hour >= 17 && hour <= 19;
                const isSelected = selectedSlotPopover === slot;

                return (
                  <div key={slot} className="relative">
                    <button
                      onClick={() => setSelectedSlotPopover((prev) => (prev === slot ? null : slot))}
                      className={`px-3 py-2 rounded-xl text-xs font-mono font-bold transition-all duration-150 cursor-pointer border flex items-center gap-1.5 ${
                        isPrime
                          ? 'bg-amber-500/15 border-amber-500/40 text-amber-300 hover:bg-amber-500/25 ring-1 ring-amber-500/20'
                          : 'bg-cyan-950/40 border-cyan-bright/30 text-cyan-200 hover:bg-cyan-bright/20'
                      } ${isSelected ? 'ring-2 ring-cyan-bright scale-105' : ''}`}
                    >
                      <span>{slot} hs</span>
                      {isPrime && <span className="text-[9px] text-amber-400" title="Horario Prime">⭐</span>}
                    </button>

                    {/* Popover on click (Mejora 33) */}
                    {isSelected && (
                      <div className="absolute top-full left-0 mt-2 z-40 w-56 p-2.5 rounded-2xl bg-sapphire-950 border border-cyan-bright/50 shadow-2xl text-xs space-y-1.5 animate-fadeIn">
                        <button
                          onClick={() => {
                            onInsertSlotIntoChat?.(slot, selectedDate);
                            setSelectedSlotPopover(null);
                          }}
                          className="w-full text-left p-2 rounded-xl bg-cyan-bright/15 hover:bg-cyan-bright/25 text-cyan-bright font-bold transition flex items-center gap-2 cursor-pointer"
                        >
                          <span>💬 Insertar en el Chat</span>
                        </button>
                        <button
                          onClick={() => {
                            setManualForm((prev) => ({ ...prev, time: slot }));
                            setManualBookingModal(true);
                            setSelectedSlotPopover(null);
                          }}
                          className="w-full text-left p-2 rounded-xl bg-white/5 hover:bg-white/10 text-white font-semibold transition flex items-center gap-2 cursor-pointer"
                        >
                          <span>📅 Agendar Paciente</span>
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="p-6 text-center text-xs text-titanium-400">
              No hay turnos disponibles para esta fecha. Intenta cambiar el día o consultar la lista de espera.
            </div>
          )}
        </div>
      </div>

      {/* Confirmed Appointments Section (Mejora 34, 38, 39) */}
      <div className="glass-card rounded-3xl p-5 border border-cyan-bright/20 bg-sapphire-950/70 shadow-xl space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h4 className="font-extrabold text-sm text-white flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Citas Médicas Confirmadas ({filteredAppointments.length})</span>
            </h4>
            <p className="text-xs text-titanium-400">Fichas clínicas con briefing de pre-consulta y recordatorios automáticos</p>
          </div>

          {/* Doctor filter dropdown */}
          <select
            value={doctorFilter}
            onChange={(e) => setDoctorFilter(e.target.value)}
            className="text-xs px-3 py-1.5 rounded-xl bg-black/50 border border-white/15 text-white focus:outline-none focus:border-cyan-bright font-medium"
          >
            <option value="all">Todos los Profesionales</option>
            <option value="Dra. Nairoby Domínguez">Dra. Nairoby Domínguez (Directora)</option>
            <option value="Dr. Especialista">Dr. Especialista en Implantes / Ortodoncia</option>
          </select>
        </div>

        {/* Appointment Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {filteredAppointments.length > 0 ? (
            filteredAppointments.map((appt) => {
              const isSendingReminder = reminderStatus[appt.id] === 'sending';
              const isSentReminder = reminderStatus[appt.id] === 'sent';

              return (
                <div
                  key={appt.id}
                  className="p-4 rounded-2xl bg-black/40 border border-white/10 hover:border-cyan-bright/40 transition flex flex-col justify-between gap-3 relative group"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2">
                        <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
                        <span className="font-extrabold text-sm text-white">{appt.patient_name}</span>
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-bright/15 text-cyan-bright border border-cyan-bright/30">
                        {appt.time} hs
                      </span>
                    </div>

                    <p className="text-xs text-titanium-300 font-medium">{appt.treatment}</p>

                    <div className="mt-2 flex flex-wrap items-center gap-2 text-[10px] text-titanium-400 font-mono">
                      <span>Contacto: <strong className="text-white">{appt.contact}</strong></span>
                      <span>•</span>
                      <span>Canal: <strong className="text-cyan-bright uppercase">{appt.channel}</strong></span>
                    </div>
                  </div>

                  {/* Action Buttons Strip */}
                  <div className="pt-3 border-t border-white/10 flex flex-wrap items-center justify-between gap-2 text-xs">
                    {/* Pre-Consultation AI Briefing (Mejora 38) */}
                    <button
                      onClick={() => handleOpenBriefing(appt)}
                      className="px-2.5 py-1 rounded-xl bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/30 font-bold transition flex items-center gap-1 cursor-pointer"
                    >
                      <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                      <span>Briefing IA</span>
                    </button>

                    {/* Send WhatsApp Reminder (Mejora 39) */}
                    <button
                      onClick={() => handleSendReminder(appt)}
                      disabled={isSendingReminder}
                      className="px-2.5 py-1 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 font-bold transition flex items-center gap-1 cursor-pointer disabled:opacity-50"
                    >
                      <Bell className="w-3.5 h-3.5" />
                      <span>{isSentReminder ? '✓ Enviado' : isSendingReminder ? 'Enviando...' : 'Recordatorio'}</span>
                    </button>

                    {/* Jump to Chat */}
                    {onSelectPatientChat && (
                      <button
                        onClick={() => onSelectPatientChat(appt.contact)}
                        className="px-2.5 py-1 rounded-xl bg-white/5 hover:bg-white/10 text-titanium-300 hover:text-white transition font-medium cursor-pointer"
                      >
                        Abrir Chat →
                      </button>
                    )}
                  </div>
                </div>
              );
            })
          ) : (
            <div className="col-span-2 p-8 text-center text-titanium-400 text-xs">
              No hay citas confirmadas registradas para los filtros seleccionados.
            </div>
          )}
        </div>
      </div>

      {/* AI Pre-Consultation Briefing Modal (Mejora 38) */}
      {briefingModal?.isOpen && (
        <div className="fixed inset-0 z-60 bg-black/80 flex items-center justify-center p-4 animate-fadeIn">
          <div className="max-w-md w-full glass-panel rounded-3xl p-6 border border-purple-500/40 bg-sapphire-950 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-purple-400" />
                <h3 className="font-extrabold text-sm text-white">Briefing Pre-Consulta IA</h3>
              </div>
              <button
                onClick={() => setBriefingModal(null)}
                className="p-1 text-titanium-400 hover:text-white cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-titanium-300">
              Resumen ejecutivo generado por el AnalyzerAgent para el odontólogo antes de ingresar a gabinete:
            </p>

            {briefingModal.loading ? (
              <div className="p-6 text-center text-xs text-purple-300 animate-pulse">
                Sintetizando antecedentes clínicos de Neon PGVector...
              </div>
            ) : (
              <div className="p-3.5 rounded-2xl bg-purple-950/40 border border-purple-500/30 space-y-2 text-xs text-purple-100">
                {briefingModal.lines.map((line, idx) => (
                  <p key={idx} className="font-medium">{line}</p>
                ))}
              </div>
            )}

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setBriefingModal(null)}
                className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs cursor-pointer"
              >
                Entendido
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Block Slot Modal (Mejora 35) */}
      {blockModal && (
        <div className="fixed inset-0 z-60 bg-black/80 flex items-center justify-center p-4 animate-fadeIn">
          <div className="max-w-md w-full glass-panel rounded-3xl p-6 border border-rose-500/40 bg-sapphire-950 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <h3 className="font-extrabold text-sm text-white flex items-center gap-2">
                <Lock className="w-4 h-4 text-rose-400" />
                <span>Bloquear Horario de Sillón</span>
              </h3>
              <button onClick={() => setBlockModal(false)} className="text-titanium-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>
            <form onSubmit={handleBlockSlot} className="space-y-3">
              <div>
                <label className="block text-[11px] font-bold text-titanium-300 mb-1">Hora de Inicio</label>
                <input
                  type="text"
                  value={blockTime}
                  onChange={(e) => setBlockTime(e.target.value)}
                  placeholder="12:00"
                  className="w-full text-xs p-2.5 rounded-xl bg-black/50 border border-white/15 text-white"
                />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-titanium-300 mb-1">Motivo del Bloqueo</label>
                <select
                  value={blockReason}
                  onChange={(e) => setBlockReason(e.target.value)}
                  className="w-full text-xs p-2.5 rounded-xl bg-black/50 border border-white/15 text-white"
                >
                  <option value="Esterilización de Instrumental Autoclave">Esterilización de Autoclave</option>
                  <option value="Pausa Médica / Almuerzo Odontólogo">Pausa Médica / Almuerzo</option>
                  <option value="Cirugía de Urgencia Imprevista">Cirugía de Urgencia Imprevista</option>
                  <option value="Mantenimiento de Sillón Odontológico">Mantenimiento de Sillón</option>
                </select>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setBlockModal(false)}
                  className="px-3 py-1.5 rounded-xl bg-white/10 text-white text-xs font-bold"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold"
                >
                  Confirmar Bloqueo
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Manual Booking Modal (Mejora 42) */}
      {manualBookingModal && (
        <div className="fixed inset-0 z-60 bg-black/80 flex items-center justify-center p-4 animate-fadeIn">
          <div className="max-w-md w-full glass-panel rounded-3xl p-6 border border-cyan-bright/40 bg-sapphire-950 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <h3 className="font-extrabold text-sm text-white flex items-center gap-2">
                <Plus className="w-4 h-4 text-cyan-bright" />
                <span>Alta Rápida de Cita Manual</span>
              </h3>
              <button onClick={() => setManualBookingModal(false)} className="text-titanium-400 hover:text-white">
                <X className="w-4 h-4" />
              </button>
            </div>
            <form onSubmit={handleManualBookingSubmit} className="space-y-3">
              <div>
                <label className="block text-[11px] font-bold text-titanium-300 mb-1">Nombre Completo del Paciente</label>
                <input
                  type="text"
                  required
                  value={manualForm.patient_name}
                  onChange={(e) => setManualForm({ ...manualForm, patient_name: e.target.value })}
                  placeholder="Ej. Mariana González"
                  className="w-full text-xs p-2.5 rounded-xl bg-black/50 border border-white/15 text-white"
                />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-titanium-300 mb-1">Teléfono o WhatsApp</label>
                <input
                  type="text"
                  required
                  value={manualForm.contact}
                  onChange={(e) => setManualForm({ ...manualForm, contact: e.target.value })}
                  placeholder="+54 9 11 ..."
                  className="w-full text-xs p-2.5 rounded-xl bg-black/50 border border-white/15 text-white"
                />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-titanium-300 mb-1">Tratamiento Odontológico</label>
                <select
                  value={manualForm.treatment}
                  onChange={(e) => setManualForm({ ...manualForm, treatment: e.target.value })}
                  className="w-full text-xs p-2.5 rounded-xl bg-black/50 border border-white/15 text-white"
                >
                  <option value="Consulta Odontológica y Diagnóstico">Consulta Odontológica y Diagnóstico</option>
                  <option value="Limpieza Dental y Profilaxis">Limpieza Dental y Profilaxis (30m)</option>
                  <option value="Blanqueamiento Dental LED">Blanqueamiento Dental LED (60m)</option>
                  <option value="Ortodoncia (Evaluación y Ajuste)">Ortodoncia (Evaluación y Ajuste)</option>
                  <option value="Implantes Dentales de Titanio">Implantes Dentales (90m)</option>
                  <option value="Endodoncia Tratamiento de Conducto">Endodoncia Conducto (90m)</option>
                  <option value="Extracción Muela del Juicio">Extracción Muela del Juicio (45m)</option>
                </select>
              </div>
              <div>
                <label className="block text-[11px] font-bold text-titanium-300 mb-1">Horario Reservado</label>
                <input
                  type="text"
                  required
                  value={manualForm.time}
                  onChange={(e) => setManualForm({ ...manualForm, time: e.target.value })}
                  placeholder="10:00"
                  className="w-full text-xs p-2.5 rounded-xl bg-black/50 border border-white/15 text-white"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setManualBookingModal(false)}
                  className="px-3 py-1.5 rounded-xl bg-white/10 text-white text-xs font-bold"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-xl bg-cyan-bright hover:bg-cyan-bright/90 text-abyssal text-xs font-bold"
                >
                  Guardar Cita
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
