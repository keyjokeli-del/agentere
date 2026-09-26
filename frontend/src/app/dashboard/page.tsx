'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Calendar as CalendarIcon,
  Clock,
  MessageSquare,
  Sparkles,
  Smartphone,
  Send,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  QrCode,
  ShieldCheck,
  UserCheck,
  Stethoscope,
  Database,
  Trash2,
  ExternalLink,
  ChevronRight,
  LogOut,
  Power,
  CalendarCheck,
  Lock
} from 'lucide-react';
import {
  ChannelType,
  Appointment,
  Activity,
  WhatsAppStatus,
  WhatsAppQRResponse,
  SlotsResponse,
  ChatMessage
} from '@/types';

const FacebookIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
  </svg>
);

const InstagramIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
  </svg>
);

const YoutubeIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
  </svg>
);

const QUICK_PROMPTS = [
  '¿Cuánto cuesta un blanqueamiento dental y qué incluye?',
  'Hola, quisiera agendar un turno para ortodoncia mañana a las 10:30',
  'Tengo un dolor muy fuerte y punzante en una muela, ¿atienden urgencias hoy?',
  '¿Qué antibiótico o pastilla puedo tomar para calmar la infección?',
  'Confirmo el turno para limpieza a las 09:45'
];

export default function Dashboard() {
  // Security PIN Access Gate (Restricts /dashboard to clinic staff)
  const ADMIN_PIN = process.env.NEXT_PUBLIC_ADMIN_PIN || '2026';
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isAuthChecking, setIsAuthChecking] = useState<boolean>(true);
  const [enteredPin, setEnteredPin] = useState<string>('');
  const [pinError, setPinError] = useState<string>('');

  useEffect(() => {
    const saved = typeof window !== 'undefined' ? sessionStorage.getItem('lumina_dashboard_auth') : null;
    if (saved === 'true') {
      setIsAuthenticated(true);
    }
    setIsAuthChecking(false);
  }, []);

  const handlePinSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (enteredPin.trim() === ADMIN_PIN) {
      setIsAuthenticated(true);
      if (typeof window !== 'undefined') {
        sessionStorage.setItem('lumina_dashboard_auth', 'true');
      }
      setPinError('');
    } else {
      setPinError('PIN de seguridad clínico incorrecto. Intente nuevamente.');
      setEnteredPin('');
    }
  };

  const handleLogout = () => {
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem('lumina_dashboard_auth');
    }
    setIsAuthenticated(false);
    setEnteredPin('');
  };

  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [backendOnline, setBackendOnline] = useState<boolean>(false);
  const [calendarOnline, setCalendarOnline] = useState<string>('Memoria');
  
  // WhatsApp & Neon State
  const [waData, setWaData] = useState<WhatsAppStatus>({
    status: 'disconnected',
    user: null,
    hasQR: false,
    storage: 'local_disk',
    neonConfigured: false
  });
  const [qrCode, setQrCode] = useState<string | null>(null);
  const [showQrModal, setShowQrModal] = useState<boolean>(false);
  const [isConnectingWA, setIsConnectingWA] = useState<boolean>(false);
  const [isDisconnectingWA, setIsDisconnectingWA] = useState<boolean>(false);

  // Calendar Slots Viewer
  const [selectedDate, setSelectedDate] = useState<string>(() => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  });
  const [availableSlots, setAvailableSlots] = useState<string[]>([]);
  const [loadingSlots, setLoadingSlots] = useState<boolean>(false);

  // Omnichannel Simulator State
  const [simChannel, setSimChannel] = useState<ChannelType>('whatsapp');
  const [simSender, setSimSender] = useState<string>('Mariana Ruiz');
  const [simMessage, setSimMessage] = useState<string>('');
  const [simLoading, setSimLoading] = useState<boolean>(false);
  const [chatLog, setChatLog] = useState<ChatMessage[]>([
    {
      id: 'init-1',
      sender: 'Sistema Multicanal',
      text: '👋 ¡Bienvenido al Simulador Omnicanal! Los agentes de IA (Triage, FAQ y Citas con Groq Llama 3.3) están listos para responder y gestionar reservas en tiempo real.',
      isBot: true,
      agent: 'Dental AI Coordinator',
      intent: 'GREETING',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);

  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
  const WA_SERVICE_URL = process.env.NEXT_PUBLIC_WHATSAPP_URL || 'http://localhost:3001';

  // 1. Fetch Backend Data
  const fetchBackendData = useCallback(async () => {
    try {
      const healthRes = await fetch(`${BACKEND_URL}/`);
      if (healthRes.ok) {
        const healthData = await healthRes.json();
        setBackendOnline(true);
        setCalendarOnline(healthData.calendar || 'Activo');
      } else {
        setBackendOnline(false);
      }

      const apptRes = await fetch(`${BACKEND_URL}/api/appointments`);
      if (apptRes.ok) {
        const apptData = await apptRes.json();
        setAppointments(apptData || []);
      }

      const summaryRes = await fetch(`${BACKEND_URL}/api/dashboard/summary`);
      if (summaryRes.ok) {
        const summaryData = await summaryRes.json();
        setActivities(summaryData.recent_activities || []);
      }
    } catch {
      setBackendOnline(false);
    }
  }, [BACKEND_URL]);

  // 2. Fetch Slots for selected date
  const fetchSlots = useCallback(async (dateStr: string) => {
    setLoadingSlots(true);
    try {
      const res = await fetch(`${BACKEND_URL}/api/slots?target_date=${dateStr}`);
      if (res.ok) {
        const data: SlotsResponse = await res.json();
        setAvailableSlots(data.slots || []);
      }
    } catch {
      setAvailableSlots([]);
    } finally {
      setLoadingSlots(false);
    }
  }, [BACKEND_URL]);

  // 3. Fetch WhatsApp Status & QR
  const fetchWhatsAppStatus = useCallback(async () => {
    try {
      const res = await fetch(`${WA_SERVICE_URL}/api/status`);
      if (res.ok) {
        const data: WhatsAppStatus = await res.json();
        setWaData(data);

        if (data.status === 'waiting_for_scan' || data.hasQR) {
          const qrRes = await fetch(`${WA_SERVICE_URL}/api/qr`);
          if (qrRes.ok) {
            const qrData: WhatsAppQRResponse = await qrRes.json();
            setQrCode(qrData.qr);
          }
        } else if (data.status === 'connected') {
          setQrCode(null);
        }
      }
    } catch {
      setWaData(prev => ({ ...prev, status: 'disconnected' }));
    }
  }, [WA_SERVICE_URL]);

  // Periodic Polling
  useEffect(() => {
    fetchBackendData();
    fetchWhatsAppStatus();
    fetchSlots(selectedDate);

    const interval = setInterval(() => {
      fetchBackendData();
      fetchWhatsAppStatus();
    }, 4000);

    return () => clearInterval(interval);
  }, [fetchBackendData, fetchWhatsAppStatus, fetchSlots, selectedDate]);

  // Handle WhatsApp Connect
  const handleConnectWhatsApp = async () => {
    setIsConnectingWA(true);
    try {
      await fetch(`${WA_SERVICE_URL}/api/connect`, { method: 'POST' });
      setShowQrModal(true);
      await fetchWhatsAppStatus();
    } catch {
      alert('Error iniciando la conexión con el microservicio de WhatsApp.');
    } finally {
      setIsConnectingWA(false);
    }
  };

  // Handle WhatsApp Disconnect
  const handleDisconnectWhatsApp = async () => {
    if (!confirm('¿Deseas desvincular y cerrar la sesión de WhatsApp de la clínica?')) return;
    setIsDisconnectingWA(true);
    try {
      await fetch(`${WA_SERVICE_URL}/api/disconnect`, { method: 'POST' });
      setQrCode(null);
      await fetchWhatsAppStatus();
    } catch {
      alert('Error desconectando sesión.');
    } finally {
      setIsDisconnectingWA(false);
      setShowQrModal(false);
    }
  };

  // Handle Message Submission in Simulator
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!simMessage.trim() || simLoading) return;

    const userMsg = simMessage.trim();
    setSimMessage('');
    setSimLoading(true);

    const userMessageObj: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: simSender,
      text: userMsg,
      isBot: false,
      channel: simChannel,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setChatLog(prev => [...prev, userMessageObj]);

    try {
      const res = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMsg,
          sender_id: simSender.toLowerCase().replace(/\s+/g, '_'),
          sender_name: simSender,
          channel: simChannel
        })
      });

      if (res.ok) {
        const data = await res.json();
        const botMessageObj: ChatMessage = {
          id: `bot-${Date.now()}`,
          sender: 'Asistente Odontológico',
          text: data.reply,
          isBot: true,
          channel: simChannel,
          agent: data.agent,
          intent: data.intent,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setChatLog(prev => [...prev, botMessageObj]);
        fetchBackendData();
        fetchSlots(selectedDate);
      } else {
        setChatLog(prev => [
          ...prev,
          {
            id: `err-${Date.now()}`,
            sender: 'Sistema',
            text: '⚠️ Ocurrió un error al procesar el mensaje con el backend.',
            isBot: true,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ]);
      }
    } catch {
      setChatLog(prev => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: 'Sistema',
          text: '⚠️ Backend desconectado. Verifica que FastAPI esté corriendo en http://localhost:8000.',
          isBot: true,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setSimLoading(false);
    }
  };

  const selectQuickPrompt = (prompt: string) => {
    setSimMessage(prompt);
  };

  if (isAuthChecking) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-teal-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-teal-950 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-slate-900/90 border border-teal-500/20 backdrop-blur-xl rounded-3xl p-8 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-teal-500/10 rounded-full blur-2xl pointer-events-none" />
          
          <div className="text-center mb-8">
            <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 shadow-inner">
              <ShieldCheck className="w-8 h-8" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Lumina Dental Studio</h1>
            <p className="text-xs uppercase tracking-widest text-teal-400 font-semibold mt-1">Panel de Control Clínico</p>
            <p className="text-sm text-slate-400 mt-3">
              Acceso restringido para el equipo médico y coordinadores. Ingrese el PIN de seguridad para continuar.
            </p>
          </div>

          <form onSubmit={handlePinSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5 text-center">
                PIN DE ADMINISTRACIÓN
              </label>
              <input
                type="password"
                maxLength={8}
                autoFocus
                value={enteredPin}
                onChange={(e) => {
                  setEnteredPin(e.target.value);
                  setPinError('');
                }}
                placeholder="••••"
                className="w-full text-center tracking-[0.5em] text-2xl font-mono px-4 py-3 rounded-xl bg-slate-800/80 border border-slate-700 text-white placeholder-slate-600 focus:outline-none focus:ring-2 focus:ring-teal-400 focus:border-transparent transition"
              />
            </div>

            {pinError && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs text-center flex items-center justify-center gap-1.5">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {pinError}
              </div>
            )}

            <button
              type="submit"
              className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-slate-950 font-bold text-sm shadow-lg shadow-teal-500/20 transition transform active:scale-[0.98] flex items-center justify-center gap-2 cursor-pointer"
            >
              <Lock className="w-4 h-4" /> Desbloquear Panel
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-slate-800 text-center">
            <a
              href="/"
              className="text-xs text-slate-400 hover:text-teal-400 transition inline-flex items-center gap-1.5"
            >
              ← Volver al sitio público de pacientes
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 pb-16">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-teal-600 flex items-center justify-center text-white shadow-sm ring-2 ring-teal-100">
              <Stethoscope className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-bold text-lg text-slate-900 leading-none">Clínica Dental Sonrisas</h1>
                <span className="bg-teal-50 text-teal-700 text-[10px] font-bold px-2 py-0.5 rounded-full border border-teal-200 uppercase tracking-wide">
                  Panel Omnicanal
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium mt-0.5">Atención 24/7 con IA • $0 USD Costo Operativo</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Status Badges */}
            <div className="hidden md:flex items-center gap-2">
              <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${
                backendOnline ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-rose-50 text-rose-700 border-rose-200'
              }`}>
                <span className={`w-2 h-2 rounded-full ${backendOnline ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
                {backendOnline ? 'FastAPI Backend Online' : 'Backend Offline'}
              </span>

              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
                <Sparkles className="w-3.5 h-3.5" /> Groq Llama 3.3 (Capa Gratis)
              </span>

              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                <CalendarIcon className="w-3.5 h-3.5" /> {calendarOnline}
              </span>
            </div>

            <button
              onClick={() => {
                fetchBackendData();
                fetchWhatsAppStatus();
                fetchSlots(selectedDate);
              }}
              className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition"
              title="Refrescar métricas y estado"
            >
              <RefreshCw className="w-4 h-4" />
            </button>

            <button
              onClick={handleLogout}
              className="p-2 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
              title="Bloquear panel clínico (Cerrar sesión)"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-8">
        {/* Section 1: Real-Time Channels Monitor */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900 tracking-tight flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-teal-600" />
                Monitor de Canales en Tiempo Real
              </h2>
              <p className="text-xs text-slate-500">Conectores sin costo mensual integrados a los agentes de atención y agenda</p>
            </div>
            <span className="text-xs font-semibold text-slate-500 bg-white px-3 py-1 rounded-lg border border-slate-200">
              4 Redes Omnicanal
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* WhatsApp (Baileys + Neon) */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs hover:shadow-md transition flex flex-col justify-between relative overflow-hidden">
              <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-50 rounded-full -mr-8 -mt-8 pointer-events-none" />
              <div>
                <div className="flex items-center justify-between mb-3 relative">
                  <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shadow-xs">
                    <Smartphone className="w-5 h-5" />
                  </div>
                  <span className={`px-2.5 py-1 rounded-full text-xs font-bold inline-flex items-center gap-1.5 ${
                    waData.status === 'connected' ? 'bg-emerald-100 text-emerald-800' :
                    waData.status === 'waiting_for_scan' ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-700'
                  }`}>
                    <span className={`w-2 h-2 rounded-full ${
                      waData.status === 'connected' ? 'bg-emerald-500 animate-pulse' :
                      waData.status === 'waiting_for_scan' ? 'bg-amber-500 animate-bounce' : 'bg-slate-400'
                    }`} />
                    {waData.status === 'connected' ? 'Conectado' : waData.status === 'waiting_for_scan' ? 'Esperando QR' : 'Desconectado'}
                  </span>
                </div>

                <h3 className="font-bold text-slate-900 text-sm">WhatsApp (Baileys Bridge)</h3>
                <p className="text-xs text-slate-500 mt-1">Conexión WebSocket directa sin pago de API oficial ni intermediarios.</p>

                {/* Neon Postgres Status */}
                <div className="mt-3 pt-3 border-t border-slate-100">
                  <div className="flex items-center gap-1.5">
                    <Database className="w-3.5 h-3.5 text-purple-600" />
                    <span className="text-[11px] font-bold text-slate-700">Persistencia:</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                      waData.neonConfigured
                        ? 'bg-purple-100 text-purple-800 border border-purple-200'
                        : 'bg-amber-50 text-amber-800 border border-amber-200'
                    }`}>
                      {waData.neonConfigured ? '⚡ Neon Postgres (Cero desconexión)' : '💾 Disco Local Contingencia'}
                    </span>
                  </div>
                  {waData.user && (
                    <p className="text-[11px] font-mono text-emerald-700 mt-1 truncate">
                      Línea: {waData.user}
                    </p>
                  )}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-2">
                <button
                  onClick={() => setShowQrModal(true)}
                  className="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl transition shadow-xs"
                >
                  <QrCode className="w-3.5 h-3.5" />
                  {waData.status === 'connected' ? 'Ver Conexión' : 'Escanear QR'}
                </button>
                {waData.status === 'connected' && (
                  <button
                    onClick={handleDisconnectWhatsApp}
                    disabled={isDisconnectingWA}
                    className="p-2 text-rose-600 hover:bg-rose-50 rounded-xl transition border border-rose-200"
                    title="Cerrar sesión de WhatsApp"
                  >
                    <LogOut className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>

            {/* Facebook Messenger */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs hover:shadow-md transition flex flex-col justify-between relative overflow-hidden">
              <div className="absolute top-0 right-0 w-24 h-24 bg-blue-50 rounded-full -mr-8 -mt-8 pointer-events-none" />
              <div>
                <div className="flex items-center justify-between mb-3 relative">
                  <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shadow-xs">
                    <FacebookIcon className="w-5 h-5" />
                  </div>
                  <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800 inline-flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" /> Webhook Activo
                  </span>
                </div>
                <h3 className="font-bold text-slate-900 text-sm">Facebook Messenger</h3>
                <p className="text-xs text-slate-500 mt-1">Recepción de mensajes privados de la Fan Page de la clínica.</p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-500 flex items-center gap-1.5 font-medium">
                <CheckCircle2 className="w-4 h-4 text-blue-600" /> Meta Developer Free Tier
              </div>
            </div>

            {/* Instagram Direct */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs hover:shadow-md transition flex flex-col justify-between relative overflow-hidden">
              <div className="absolute top-0 right-0 w-24 h-24 bg-pink-50 rounded-full -mr-8 -mt-8 pointer-events-none" />
              <div>
                <div className="flex items-center justify-between mb-3 relative">
                  <div className="w-10 h-10 rounded-xl bg-pink-50 text-pink-600 flex items-center justify-center shadow-xs">
                    <InstagramIcon className="w-5 h-5" />
                  </div>
                  <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-pink-100 text-pink-800 inline-flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-pink-500 animate-pulse" /> DMs & Reels
                  </span>
                </div>
                <h3 className="font-bold text-slate-900 text-sm">Instagram Direct</h3>
                <p className="text-xs text-slate-500 mt-1">Respuestas a preguntas en publicaciones, reels y mensajes directos.</p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-500 flex items-center gap-1.5 font-medium">
                <CheckCircle2 className="w-4 h-4 text-pink-600" /> Graph API Free Tier
              </div>
            </div>

            {/* YouTube Comments */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-xs hover:shadow-md transition flex flex-col justify-between relative overflow-hidden">
              <div className="absolute top-0 right-0 w-24 h-24 bg-red-50 rounded-full -mr-8 -mt-8 pointer-events-none" />
              <div>
                <div className="flex items-center justify-between mb-3 relative">
                  <div className="w-10 h-10 rounded-xl bg-red-50 text-red-600 flex items-center justify-center shadow-xs">
                    <YoutubeIcon className="w-5 h-5" />
                  </div>
                  <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-red-100 text-red-800 inline-flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" /> Comentarios
                  </span>
                </div>
                <h3 className="font-bold text-slate-900 text-sm">YouTube Channel</h3>
                <p className="text-xs text-slate-500 mt-1">Interpreta consultas odontológicas en videos educativos y guía a agendar.</p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-500 flex items-center gap-1.5 font-medium">
                <CheckCircle2 className="w-4 h-4 text-red-600" /> Google Cloud Free Quota
              </div>
            </div>
          </div>
        </section>

        {/* Section 2: Interactive Simulator & Google Calendar Agenda */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Simulator Console */}
          <section className="lg:col-span-7 bg-white rounded-3xl border border-slate-200 shadow-xs overflow-hidden flex flex-col">
            <div className="p-4 sm:p-5 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3 bg-slate-50/50">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-teal-100 text-teal-700 flex items-center justify-center">
                  <MessageSquare className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="font-bold text-sm text-slate-900 leading-tight">Simulador de Chat Omnicanal</h2>
                  <p className="text-[11px] text-slate-500">Prueba cómo responden los agentes al simular mensajes de pacientes</p>
                </div>
              </div>

              {/* Channel Selector */}
              <div className="flex items-center gap-1 bg-white p-1 rounded-xl border border-slate-200 text-xs font-semibold shadow-xs">
                <button
                  onClick={() => setSimChannel('whatsapp')}
                  className={`px-2.5 py-1 rounded-lg flex items-center gap-1 transition ${
                    simChannel === 'whatsapp' ? 'bg-emerald-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <Smartphone className="w-3.5 h-3.5" /> WA
                </button>
                <button
                  onClick={() => setSimChannel('facebook')}
                  className={`px-2.5 py-1 rounded-lg flex items-center gap-1 transition ${
                    simChannel === 'facebook' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <FacebookIcon className="w-3.5 h-3.5" /> FB
                </button>
                <button
                  onClick={() => setSimChannel('instagram')}
                  className={`px-2.5 py-1 rounded-lg flex items-center gap-1 transition ${
                    simChannel === 'instagram' ? 'bg-pink-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <InstagramIcon className="w-3.5 h-3.5" /> IG
                </button>
                <button
                  onClick={() => setSimChannel('youtube')}
                  className={`px-2.5 py-1 rounded-lg flex items-center gap-1 transition ${
                    simChannel === 'youtube' ? 'bg-red-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <YoutubeIcon className="w-3.5 h-3.5" /> YT
                </button>
              </div>
            </div>

            {/* Patient Name & Quick Chips */}
            <div className="p-3 bg-slate-100/60 border-b border-slate-200/70 flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wide">Paciente:</span>
                <input
                  type="text"
                  value={simSender}
                  onChange={e => setSimSender(e.target.value)}
                  className="bg-white border border-slate-300 rounded-lg px-2.5 py-1 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-1 focus:ring-teal-500"
                  placeholder="Nombre del paciente"
                />
                <span className="text-[11px] text-slate-400">Canal: <strong className="uppercase text-slate-600">{simChannel}</strong></span>
              </div>

              {/* Quick Prompts */}
              <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
                <span className="text-[10px] font-bold text-slate-400 whitespace-nowrap">Ejemplos:</span>
                {QUICK_PROMPTS.map((p, i) => (
                  <button
                    key={i}
                    onClick={() => selectQuickPrompt(p)}
                    className="text-[10px] font-medium bg-white hover:bg-teal-50 hover:text-teal-700 hover:border-teal-300 text-slate-600 border border-slate-200 px-2.5 py-1 rounded-full whitespace-nowrap transition"
                  >
                    {p.length > 35 ? p.substring(0, 35) + '...' : p}
                  </button>
                ))}
              </div>
            </div>

            {/* Chat Messages Body */}
            <div className="p-4 sm:p-5 flex-1 overflow-y-auto space-y-4 max-h-[460px] min-h-[380px] bg-slate-50/40">
              {chatLog.map(msg => (
                <div key={msg.id} className={`flex flex-col ${msg.isBot ? 'items-start' : 'items-end'}`}>
                  <div className="flex items-center gap-1.5 mb-1 px-1 text-xs text-slate-500 font-medium">
                    <span>{msg.sender}</span>
                    <span className="text-[10px] text-slate-400">{msg.timestamp}</span>
                    {msg.agent && (
                      <span className="px-2 py-0.5 rounded-full bg-teal-50 text-teal-700 border border-teal-200 text-[10px] font-bold">
                        {msg.agent}
                      </span>
                    )}
                    {msg.intent && (
                      <span className="px-2 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200 text-[10px] font-bold">
                        {msg.intent}
                      </span>
                    )}
                  </div>
                  <div className={`p-4 rounded-2xl max-w-[88%] text-sm leading-relaxed whitespace-pre-line shadow-xs ${
                    msg.isBot
                      ? 'bg-white border border-slate-200 text-slate-800'
                      : 'bg-teal-600 text-white font-medium shadow-teal-700/10'
                  }`}>
                    {msg.text}
                  </div>
                </div>
              ))}
              {simLoading && (
                <div className="flex items-center gap-2 text-xs text-slate-500 italic p-3 bg-white rounded-2xl border border-slate-200 inline-flex shadow-xs animate-pulse">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin text-teal-600" />
                  Groq Llama 3.3 está analizando el caso y verificando Google Calendar...
                </div>
              )}
            </div>

            {/* Message Input Form */}
            <form onSubmit={handleSendMessage} className="p-3 sm:p-4 bg-white border-t border-slate-200 flex gap-2">
              <input
                type="text"
                value={simMessage}
                onChange={e => setSimMessage(e.target.value)}
                placeholder={`Escribe como paciente en ${simChannel.toUpperCase()}...`}
                className="flex-1 bg-slate-50 border border-slate-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:bg-white transition"
              />
              <button
                type="submit"
                disabled={simLoading || !simMessage.trim()}
                className="bg-teal-600 hover:bg-teal-700 disabled:opacity-50 text-white px-5 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 transition shadow-xs"
              >
                <Send className="w-4 h-4" />
                Enviar
              </button>
            </form>
          </section>

          {/* Google Calendar & Appointments Viewer */}
          <section className="lg:col-span-5 bg-white rounded-3xl border border-slate-200 shadow-xs overflow-hidden flex flex-col">
            <div className="p-4 sm:p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center">
                  <CalendarIcon className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="font-bold text-sm text-slate-900 leading-tight">Agenda en Google Calendar</h2>
                  <p className="text-[11px] text-slate-500">Franjas de 45 min con bloqueo estricto anti-colisión</p>
                </div>
              </div>
              <span className="text-xs font-bold px-2.5 py-1 bg-blue-50 text-blue-700 rounded-full border border-blue-200">
                {appointments.length} turnos
              </span>
            </div>

            {/* Date Selector & Available 45-min slots */}
            <div className="p-4 bg-slate-50/60 border-b border-slate-200/80 space-y-3">
              <div className="flex items-center justify-between gap-2">
                <label className="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                  <CalendarCheck className="w-4 h-4 text-blue-600" /> Consultar Día:
                </label>
                <input
                  type="date"
                  value={selectedDate}
                  onChange={e => {
                    setSelectedDate(e.target.value);
                    fetchSlots(e.target.value);
                  }}
                  className="text-xs font-semibold bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
              </div>

              {/* Dynamic 45-minute Slots Pill Box */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wide">
                    Horarios Libres (45 min):
                  </span>
                  <span className="text-[10px] font-semibold text-blue-700">
                    {loadingSlots ? 'Consultando...' : `${availableSlots.length} disponibles`}
                  </span>
                </div>

                <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
                  {loadingSlots ? (
                    <span className="text-xs text-slate-400 italic">Cargando disponibilidad...</span>
                  ) : availableSlots.length === 0 ? (
                    <span className="text-xs text-slate-400 italic">No quedan horarios disponibles para este día.</span>
                  ) : (
                    availableSlots.map((slot, idx) => (
                      <button
                        key={idx}
                        onClick={() => selectQuickPrompt(`Quiero agendar un turno para el día ${selectedDate} a las ${slot}`)}
                        title="Hacer clic para pedir este turno en el chat"
                        className="text-[11px] font-mono font-bold bg-white text-blue-700 border border-blue-200 hover:bg-blue-600 hover:text-white px-2 py-0.5 rounded-md transition shadow-2xs"
                      >
                        {slot}
                      </button>
                    ))
                  )}
                </div>
              </div>
            </div>

            {/* Appointments List */}
            <div className="p-4 sm:p-5 flex-1 overflow-y-auto max-h-[460px] space-y-3">
              {appointments.length === 0 ? (
                <div className="text-center py-14 text-slate-400">
                  <CalendarIcon className="w-12 h-12 mx-auto mb-2 opacity-25" />
                  <p className="text-sm font-semibold text-slate-600">No hay citas registradas todavía</p>
                  <p className="text-xs text-slate-400 mt-1 max-w-xs mx-auto">
                    Usa el simulador o escribe por WhatsApp para agendar un turno de evaluación o limpieza.
                  </p>
                </div>
              ) : (
                appointments.map(appt => (
                  <div
                    key={appt.id}
                    className="p-3.5 rounded-2xl border border-slate-200 bg-white hover:border-blue-300 transition shadow-2xs space-y-2"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-bold text-xs text-slate-900 flex items-center gap-1.5">
                          <UserCheck className="w-3.5 h-3.5 text-teal-600" />
                          {appt.patient_name}
                        </h4>
                        <p className="text-[11px] text-slate-500">{appt.treatment}</p>
                      </div>
                      <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200">
                        {appt.status}
                      </span>
                    </div>

                    <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600 font-medium">
                      <div className="flex items-center gap-3">
                        <span className="flex items-center gap-1 text-slate-700">
                          <CalendarIcon className="w-3 h-3 text-blue-600" /> {appt.date}
                        </span>
                        <span className="flex items-center gap-1 text-slate-700">
                          <Clock className="w-3 h-3 text-blue-600" /> {appt.time} hs
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-400 uppercase font-semibold">
                        Vía {appt.channel}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </section>

        </div>
      </main>

      {/* WhatsApp QR Modal */}
      {showQrModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl border border-slate-200 animate-in fade-in zoom-in duration-150">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-600 flex items-center justify-center">
                  <Smartphone className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 text-sm">Vincular WhatsApp de la Clínica</h3>
                  <p className="text-[11px] text-slate-500">Motor Baileys con persistencia en Neon</p>
                </div>
              </div>
              <button
                onClick={() => setShowQrModal(false)}
                className="text-slate-400 hover:text-slate-600 text-base font-bold p-1"
              >
                ✕
              </button>
            </div>

            <div className="text-center py-3">
              {waData.status === 'connected' ? (
                <div className="space-y-4 py-4">
                  <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto shadow-inner">
                    <CheckCircle2 className="w-8 h-8" />
                  </div>
                  <div>
                    <h4 className="font-bold text-emerald-800 text-base">¡WhatsApp ya está conectado!</h4>
                    <p className="text-xs text-slate-500 mt-1">
                      El asistente de IA está respondiendo y agendando turnos desde el número de la clínica.
                    </p>
                    {waData.user && (
                      <p className="font-mono text-xs font-bold text-slate-700 bg-slate-100 py-1 px-3 rounded-lg mt-2 inline-block">
                        {waData.user}
                      </p>
                    )}
                  </div>
                  <div className="p-3 bg-purple-50 text-purple-800 rounded-xl text-xs font-medium border border-purple-200 text-left">
                    ⚡ <strong>Persistencia Activa:</strong> Las claves criptográficas Signal están guardadas en Neon PostgreSQL. Aunque se reinicie el servidor, no tendrás que volver a escanear el QR.
                  </div>
                  <button
                    onClick={handleDisconnectWhatsApp}
                    disabled={isDisconnectingWA}
                    className="w-full py-2.5 text-xs font-bold text-rose-600 bg-rose-50 hover:bg-rose-100 rounded-xl transition border border-rose-200 flex items-center justify-center gap-1.5"
                  >
                    <Power className="w-3.5 h-3.5" />
                    {isDisconnectingWA ? 'Cerrando sesión...' : 'Desvincular Dispositivo y Purgar Sesión'}
                  </button>
                </div>
              ) : qrCode ? (
                <div className="space-y-4">
                  <div className="p-3 bg-white border-2 border-slate-200 rounded-2xl inline-block shadow-inner">
                    <img src={qrCode} alt="WhatsApp QR Code" className="w-64 h-64 mx-auto rounded-lg" />
                  </div>
                  <div className="text-left text-xs text-slate-600 space-y-1 bg-slate-50 p-3 rounded-xl border border-slate-200">
                    <p className="font-bold text-slate-800 mb-1">Pasos para conectar:</p>
                    <p>1. Abre WhatsApp en el celular del consultorio.</p>
                    <p>2. Ve a <strong>Ajustes &gt; Dispositivos vinculados</strong>.</p>
                    <p>3. Presiona <strong>Vincular dispositivo</strong> y apunta al código QR.</p>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500">
                    <span>Modo de almacenamiento:</span>
                    <strong className="text-purple-700 uppercase">{waData.storage}</strong>
                  </div>
                </div>
              ) : (
                <div className="py-10 space-y-3 text-slate-500">
                  <RefreshCw className="w-8 h-8 animate-spin mx-auto text-teal-600" />
                  <p className="text-xs font-medium">Iniciando microservicio y generando código QR...</p>
                  <p className="text-[11px] text-slate-400">Verifica que el servicio esté ejecutándose en el puerto 3001.</p>
                </div>
              )}
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
              <button
                onClick={fetchWhatsAppStatus}
                className="text-xs text-slate-500 hover:text-slate-800 flex items-center gap-1 font-semibold"
              >
                <RefreshCw className="w-3 h-3" /> Refrescar QR
              </button>
              <button
                onClick={() => setShowQrModal(false)}
                className="px-4 py-1.5 text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
