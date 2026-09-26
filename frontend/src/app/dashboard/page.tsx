'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Image from 'next/image';
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
  Lock,
  Film,
  Play,
  Share2,
  Layers,
  Cpu,
  BrainCircuit,
  Eye,
  Activity as ActivityIcon
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

const CLINICAL_ASSETS = [
  {
    name: 'Logotipo 3D Oficial',
    filename: 'lumina-logo.png',
    type: 'Emblema 3D (1:1)',
    desc: 'Porcelana translúcida, anillo cian #00E5FF y zafiro.',
  },
  {
    name: 'Portada y Atmósfera Clínica',
    filename: 'lumina-cover.png',
    type: 'Widescreen (16:9)',
    desc: 'Gabinete odontológico de vanguardia con escáner digital 3D.',
  },
  {
    name: 'Post Blanqueamiento Láser',
    filename: 'ig-post-blanqueamiento.png',
    type: 'Social Post (1:1)',
    desc: 'Estética dental avanzada, fotoactivación en frío.',
  },
  {
    name: 'Post Implantes Guiados 3D',
    filename: 'ig-post-implantes.png',
    type: 'Social Post (1:1)',
    desc: 'Cirugía computarizada y fijación ósea milimétrica.',
  },
  {
    name: 'Post Guardia & Triage 24/7',
    filename: 'ig-post-urgencias.png',
    type: 'Social Post (1:1)',
    desc: 'Atención prioritaria inmediata sin esperas.',
  }
];

export default function Dashboard() {
  const ADMIN_PIN = process.env.NEXT_PUBLIC_ADMIN_PIN || '2026';
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isAuthChecking, setIsAuthChecking] = useState<boolean>(true);
  const [enteredPin, setEnteredPin] = useState<string>('');
  const [pinError, setPinError] = useState<string>('');
  const [activeDashboardTab, setActiveDashboardTab] = useState<'monitor' | 'pipeline' | 'media'>('monitor');

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
      text: '👋 ¡Bienvenido al Simulador Omnicanal de Lumina Dental Studio! La arquitectura modular de 3 agentes (ReaderAgent -> AnalyzerAgent -> SolverAgent) está activa y conectada a Neon Postgres y Google Calendar.',
      isBot: true,
      agent: 'Lumina Coordinator',
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
          text: '⚠️ Backend desconectado. Verifica que FastAPI esté corriendo en producción.',
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
      <div className="min-h-screen bg-abyssal flex items-center justify-center">
        <div className="w-10 h-10 border-2 border-cyan-bright border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // FUTURISTIC VAULT PIN GATE
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-abyssal flex items-center justify-center p-4 relative overflow-hidden">
        {/* Ambient Glows */}
        <div className="absolute w-[500px] h-[500px] bg-sapphire-900/40 rounded-full blur-[140px] pointer-events-none" />
        <div className="absolute w-[350px] h-[350px] bg-cyan-bright/15 rounded-full blur-[100px] pointer-events-none" />

        <div className="max-w-md w-full glass-panel border border-cyan-bright/30 rounded-3xl p-8 shadow-2xl relative overflow-hidden backdrop-blur-2xl bg-sapphire-950/90">
          <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-bright/10 rounded-full blur-2xl pointer-events-none" />
          
          <div className="text-center mb-8">
            <div className="relative w-20 h-20 mx-auto mb-4 rounded-2xl overflow-hidden border border-cyan-bright/40 shadow-cyan-glow bg-abyssal p-2">
              <Image
                src="/social-kit/lumina-logo.png"
                alt="Lumina Dental Studio Logo"
                fill
                sizes="80px"
                className="object-contain p-2"
                priority
              />
            </div>
            <h1 className="text-2xl font-extrabold text-white tracking-tight">Lumina Dental Studio</h1>
            <p className="text-xs uppercase tracking-widest text-cyan-bright font-bold mt-1">Bóveda de Control Clínico</p>
            <p className="text-xs text-titanium-400 mt-2">
              Acceso restringido para el equipo médico y coordinadores. Ingrese el PIN de seguridad (2026).
            </p>
          </div>

          <form onSubmit={handlePinSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-titanium-300 mb-1.5 text-center">
                PIN DE SEGURIDAD
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
                className="w-full text-center tracking-[0.5em] text-2xl font-mono px-4 py-3 rounded-xl bg-sapphire-900/60 border border-cyan-bright/30 text-white placeholder-titanium-400 focus:outline-none focus:ring-2 focus:ring-cyan-bright transition"
              />
            </div>

            {pinError && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs text-center flex items-center justify-center gap-1.5">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {pinError}
              </div>
            )}

            <button
              type="submit"
              className="w-full py-3 px-4 rounded-xl bg-cyan-bright hover:bg-cyan-bright/90 text-abyssal font-bold text-sm shadow-cyan-glow transition transform active:scale-[0.98] flex items-center justify-center gap-2 cursor-pointer"
            >
              <Lock className="w-4 h-4" /> Desbloquear Panel Clínico
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-white/10 text-center">
            <a
              href="/"
              className="text-xs text-titanium-400 hover:text-cyan-bright transition inline-flex items-center gap-1.5"
            >
              ← Volver al sitio público de pacientes
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-abyssal text-diamond pb-16 selection:bg-cyan-bright selection:text-abyssal">
      {/* Top Header */}
      <header className="glass-panel border-b border-cyan-bright/20 sticky top-0 z-30 backdrop-blur-xl bg-sapphire-950/85">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative w-10 h-10 rounded-xl overflow-hidden border border-cyan-bright/40 shadow-cyan-glow bg-abyssal">
              <Image
                src="/social-kit/lumina-logo.png"
                alt="Lumina Logo"
                fill
                sizes="40px"
                className="object-cover"
              />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-extrabold text-base text-white tracking-tight">Lumina Dental Studio</h1>
                <span className="bg-cyan-bright/10 text-cyan-bright text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border border-cyan-bright/30 uppercase tracking-wide">
                  Panel Clínico IA
                </span>
              </div>
              <p className="text-[11px] text-titanium-400 font-medium">Odontología de Precisión • $0 USD Costo de APIs</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Live Telemetry Badges */}
            <div className="hidden md:flex items-center gap-2">
              <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${
                backendOnline ? 'bg-emerald-950/60 text-emerald-300 border-emerald-500/30' : 'bg-rose-950/60 text-rose-300 border-rose-500/30'
              }`}>
                <span className={`w-2 h-2 rounded-full ${backendOnline ? 'bg-emerald-400 animate-pulse' : 'bg-rose-400'}`} />
                {backendOnline ? 'FastAPI Render Online' : 'Backend Offline'}
              </span>

              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-sapphire-900/60 text-cyan-bright border border-cyan-bright/30">
                <Sparkles className="w-3.5 h-3.5" /> Groq Llama 3.3
              </span>

              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-sapphire-900/60 text-teal-300 border border-teal-500/30">
                <CalendarIcon className="w-3.5 h-3.5" /> {calendarOnline}
              </span>
            </div>

            <button
              onClick={() => {
                fetchBackendData();
                fetchWhatsAppStatus();
                fetchSlots(selectedDate);
              }}
              className="p-2 text-titanium-300 hover:text-white hover:bg-white/10 rounded-xl transition cursor-pointer"
              title="Refrescar métricas y estado"
            >
              <RefreshCw className="w-4 h-4" />
            </button>

            <button
              onClick={handleLogout}
              className="p-2 text-rose-400 hover:bg-rose-950/50 rounded-xl transition cursor-pointer border border-rose-500/30"
              title="Bloquear panel clínico (Cerrar sesión)"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-8">
        
        {/* Navigation Tabs Bar */}
        <div className="flex items-center gap-3 border-b border-white/10 pb-4">
          <button
            onClick={() => setActiveDashboardTab('monitor')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              activeDashboardTab === 'monitor'
                ? 'bg-cyan-bright text-abyssal shadow-cyan-glow'
                : 'bg-white/5 text-titanium-300 hover:bg-white/10 border border-white/10'
            }`}
          >
            <ActivityIcon className="w-4 h-4" />
            <span>Monitor Omnicanal & Agenda</span>
          </button>

          <button
            onClick={() => setActiveDashboardTab('pipeline')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              activeDashboardTab === 'pipeline'
                ? 'bg-cyan-bright text-abyssal shadow-cyan-glow'
                : 'bg-white/5 text-titanium-300 hover:bg-white/10 border border-white/10'
            }`}
          >
            <BrainCircuit className="w-4 h-4" />
            <span>Arquitectura 3 Agentes</span>
          </button>

          <button
            onClick={() => setActiveDashboardTab('media')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              activeDashboardTab === 'media'
                ? 'bg-cyan-bright text-abyssal shadow-cyan-glow'
                : 'bg-white/5 text-titanium-300 hover:bg-white/10 border border-white/10'
            }`}
          >
            <Film className="w-4 h-4" />
            <span>Galería de Medios & Video Reel</span>
          </button>
        </div>

        {/* TAB 1: REAL-TIME CHANNELS & SIMULATOR */}
        {activeDashboardTab === 'monitor' && (
          <div className="space-y-8">
            {/* Real-time channels row */}
            <section>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-base font-extrabold text-white tracking-tight flex items-center gap-2">
                    <ShieldCheck className="w-5 h-5 text-cyan-bright" />
                    Monitor de Canales en Tiempo Real
                  </h2>
                  <p className="text-xs text-titanium-400">Conectores sin costo mensual integrados a los agentes de atención y agenda</p>
                </div>
                <span className="text-xs font-mono font-bold text-cyan-bright bg-cyan-bright/10 px-3 py-1 rounded-xl border border-cyan-bright/30">
                  4 Redes Activas
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* WhatsApp */}
                <div className="glass-card rounded-2xl p-5 border border-cyan-bright/20 shadow-xl flex flex-col justify-between relative overflow-hidden">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <div className="w-10 h-10 rounded-xl bg-emerald-950/80 text-emerald-400 flex items-center justify-center border border-emerald-500/30">
                        <Smartphone className="w-5 h-5" />
                      </div>
                      <span className={`px-2.5 py-1 rounded-full text-xs font-bold inline-flex items-center gap-1.5 ${
                        waData.status === 'connected' ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/30' :
                        waData.status === 'waiting_for_scan' ? 'bg-amber-950 text-amber-300 border border-amber-500/30' : 'bg-slate-900 text-slate-400 border border-slate-700'
                      }`}>
                        <span className={`w-2 h-2 rounded-full ${
                          waData.status === 'connected' ? 'bg-emerald-400 animate-pulse' :
                          waData.status === 'waiting_for_scan' ? 'bg-amber-400 animate-bounce' : 'bg-slate-500'
                        }`} />
                        {waData.status === 'connected' ? 'Conectado' : waData.status === 'waiting_for_scan' ? 'Esperando QR' : 'Desconectado'}
                      </span>
                    </div>

                    <h3 className="font-bold text-white text-sm">WhatsApp (Baileys Bridge)</h3>
                    <p className="text-xs text-titanium-400 mt-1">Conexión WebSocket directa sin pago de API oficial ni intermediarios.</p>

                    <div className="mt-3 pt-3 border-t border-white/10">
                      <div className="flex items-center gap-1.5">
                        <Database className="w-3.5 h-3.5 text-cyan-bright" />
                        <span className="text-[11px] font-bold text-titanium-300">Persistencia:</span>
                        <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-md bg-purple-950/80 text-purple-300 border border-purple-500/30">
                          {waData.neonConfigured ? '⚡ Neon Postgres' : '💾 Disco Contingencia'}
                        </span>
                      </div>
                      {waData.user && (
                        <p className="text-[11px] font-mono text-emerald-400 mt-1 truncate">
                          Línea: {waData.user}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-white/10 flex items-center gap-2">
                    <button
                      onClick={() => setShowQrModal(true)}
                      className="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 text-xs font-semibold bg-emerald-500 hover:bg-emerald-400 text-abyssal rounded-xl transition shadow-xs cursor-pointer"
                    >
                      <QrCode className="w-3.5 h-3.5" />
                      {waData.status === 'connected' ? 'Ver Conexión' : 'Escanear QR'}
                    </button>
                    {waData.status === 'connected' && (
                      <button
                        onClick={handleDisconnectWhatsApp}
                        disabled={isDisconnectingWA}
                        className="p-2 text-rose-400 hover:bg-rose-950/50 rounded-xl transition border border-rose-500/30 cursor-pointer"
                        title="Cerrar sesión de WhatsApp"
                      >
                        <LogOut className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>

                {/* Facebook Messenger */}
                <div className="glass-card rounded-2xl p-5 border border-cyan-bright/20 shadow-xl flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <div className="w-10 h-10 rounded-xl bg-blue-950/80 text-blue-400 flex items-center justify-center border border-blue-500/30">
                        <FacebookIcon className="w-5 h-5" />
                      </div>
                      <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-950 text-blue-300 border border-blue-500/30 inline-flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" /> Webhook Activo
                      </span>
                    </div>
                    <h3 className="font-bold text-white text-sm">Facebook Messenger</h3>
                    <p className="text-xs text-titanium-400 mt-1">Recepción y respuesta de consultas privadas en la Fan Page.</p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-white/10 text-xs text-titanium-300 flex items-center gap-1.5 font-medium">
                    <CheckCircle2 className="w-4 h-4 text-cyan-bright" /> Meta Developer Live Mode
                  </div>
                </div>

                {/* Instagram Direct */}
                <div className="glass-card rounded-2xl p-5 border border-cyan-bright/20 shadow-xl flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <div className="w-10 h-10 rounded-xl bg-pink-950/80 text-pink-400 flex items-center justify-center border border-pink-500/30">
                        <InstagramIcon className="w-5 h-5" />
                      </div>
                      <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-pink-950 text-pink-300 border border-pink-500/30 inline-flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-pink-400 animate-pulse" /> DMs & Reels
                      </span>
                    </div>
                    <h3 className="font-bold text-white text-sm">Instagram Direct</h3>
                    <p className="text-xs text-titanium-400 mt-1">Respuestas a preguntas en publicaciones, reels y mensajes directos.</p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-white/10 text-xs text-titanium-300 flex items-center gap-1.5 font-medium">
                    <CheckCircle2 className="w-4 h-4 text-cyan-bright" /> Graph API Free Tier
                  </div>
                </div>

                {/* YouTube Comments */}
                <div className="glass-card rounded-2xl p-5 border border-cyan-bright/20 shadow-xl flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <div className="w-10 h-10 rounded-xl bg-red-950/80 text-red-400 flex items-center justify-center border border-red-500/30">
                        <YoutubeIcon className="w-5 h-5" />
                      </div>
                      <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-red-950 text-red-300 border border-red-500/30 inline-flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-red-400 animate-pulse" /> Comentarios
                      </span>
                    </div>
                    <h3 className="font-bold text-white text-sm">Canal de YouTube</h3>
                    <p className="text-xs text-titanium-400 mt-1">Sondeo cada 10 min de consultas en videos y guía a agendar.</p>
                  </div>
                  <div className="mt-4 pt-3 border-t border-white/10 text-xs text-titanium-300 flex items-center gap-1.5 font-medium">
                    <CheckCircle2 className="w-4 h-4 text-cyan-bright" /> Google Cloud Free Quota
                  </div>
                </div>
              </div>
            </section>

            {/* Simulator Console & Google Calendar Agenda */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              
              {/* Simulator */}
              <section className="lg:col-span-7 glass-panel rounded-3xl border border-cyan-bright/25 shadow-2xl overflow-hidden flex flex-col bg-sapphire-950/90">
                <div className="p-4 sm:p-5 border-b border-white/10 flex flex-wrap items-center justify-between gap-3 bg-sapphire-900/40">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-cyan-bright/20 text-cyan-bright flex items-center justify-center border border-cyan-bright/30">
                      <MessageSquare className="w-4 h-4" />
                    </div>
                    <div>
                      <h2 className="font-bold text-sm text-white leading-tight">Simulador de Chat Omnicanal</h2>
                      <p className="text-[11px] text-titanium-400">Prueba en vivo la respuesta de los 3 agentes y la agenda médica</p>
                    </div>
                  </div>

                  {/* Channel Selector */}
                  <div className="flex items-center gap-1 bg-abyssal p-1 rounded-xl border border-white/10 text-xs font-semibold">
                    <button
                      onClick={() => setSimChannel('whatsapp')}
                      className={`px-2.5 py-1 rounded-lg flex items-center gap-1 transition cursor-pointer ${
                        simChannel === 'whatsapp' ? 'bg-emerald-500 text-abyssal font-bold' : 'text-titanium-300 hover:text-white'
                      }`}
                    >
                      <Smartphone className="w-3.5 h-3.5" /> WA
                    </button>
                    <button
                      onClick={() => setSimChannel('facebook')}
                      className={`px-2.5 py-1 rounded-lg flex items-center gap-1 transition cursor-pointer ${
                        simChannel === 'facebook' ? 'bg-blue-600 text-white font-bold' : 'text-titanium-300 hover:text-white'
                      }`}
                    >
                      <FacebookIcon className="w-3.5 h-3.5" /> FB
                    </button>
                    <button
                      onClick={() => setSimChannel('instagram')}
                      className={`px-2.5 py-1 rounded-lg flex items-center gap-1 transition cursor-pointer ${
                        simChannel === 'instagram' ? 'bg-pink-600 text-white font-bold' : 'text-titanium-300 hover:text-white'
                      }`}
                    >
                      <InstagramIcon className="w-3.5 h-3.5" /> IG
                    </button>
                    <button
                      onClick={() => setSimChannel('youtube')}
                      className={`px-2.5 py-1 rounded-lg flex items-center gap-1 transition cursor-pointer ${
                        simChannel === 'youtube' ? 'bg-red-600 text-white font-bold' : 'text-titanium-300 hover:text-white'
                      }`}
                    >
                      <YoutubeIcon className="w-3.5 h-3.5" /> YT
                    </button>
                  </div>
                </div>

                {/* Patient Name & Quick Chips */}
                <div className="p-3 bg-abyssal/60 border-b border-white/10 flex flex-col gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-bold text-titanium-400 uppercase tracking-wide">Paciente:</span>
                    <input
                      type="text"
                      value={simSender}
                      onChange={e => setSimSender(e.target.value)}
                      className="bg-sapphire-900/60 border border-white/20 rounded-lg px-2.5 py-1 text-xs font-semibold text-white focus:outline-none focus:ring-1 focus:ring-cyan-bright"
                      placeholder="Nombre del paciente"
                    />
                    <span className="text-[11px] text-titanium-400">Canal: <strong className="uppercase text-cyan-bright">{simChannel}</strong></span>
                  </div>

                  {/* Quick Prompts */}
                  <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
                    <span className="text-[10px] font-bold text-titanium-400 whitespace-nowrap">Ejemplos:</span>
                    {QUICK_PROMPTS.map((p, i) => (
                      <button
                        key={i}
                        onClick={() => selectQuickPrompt(p)}
                        className="text-[10px] font-medium bg-white/5 hover:bg-cyan-bright/20 hover:text-cyan-bright text-titanium-300 border border-white/10 px-2.5 py-1 rounded-full whitespace-nowrap transition cursor-pointer"
                      >
                        {p.length > 35 ? p.substring(0, 35) + '...' : p}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Chat Messages Body */}
                <div className="p-4 sm:p-5 flex-1 overflow-y-auto space-y-4 max-h-[460px] min-h-[380px] bg-abyssal/40">
                  {chatLog.map(msg => (
                    <div key={msg.id} className={`flex flex-col ${msg.isBot ? 'items-start' : 'items-end'}`}>
                      <div className="flex items-center gap-1.5 mb-1 px-1 text-xs text-titanium-400 font-medium">
                        <span>{msg.sender}</span>
                        <span className="text-[10px] text-titanium-500">{msg.timestamp}</span>
                        {msg.agent && (
                          <span className="px-2 py-0.5 rounded-full bg-cyan-bright/10 text-cyan-bright border border-cyan-bright/30 text-[10px] font-mono font-bold">
                            {msg.agent}
                          </span>
                        )}
                        {msg.intent && (
                          <span className="px-2 py-0.5 rounded-full bg-purple-950/80 text-purple-300 border border-purple-500/30 text-[10px] font-mono font-bold">
                            {msg.intent}
                          </span>
                        )}
                      </div>
                      <div className={`p-4 rounded-2xl max-w-[88%] text-sm leading-relaxed whitespace-pre-line shadow-xl ${
                        msg.isBot
                          ? 'bg-sapphire-900/70 border border-white/15 text-white'
                          : 'bg-cyan-bright text-abyssal font-semibold shadow-cyan-glow'
                      }`}>
                        {msg.text}
                      </div>
                    </div>
                  ))}
                  {simLoading && (
                    <div className="flex items-center gap-2 text-xs text-cyan-bright italic p-3 bg-sapphire-900/60 rounded-2xl border border-cyan-bright/30 inline-flex shadow-xl animate-pulse">
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      Groq Llama 3.3 está analizando el caso y verificando Google Calendar...
                    </div>
                  )}
                </div>

                {/* Message Input Form */}
                <form onSubmit={handleSendMessage} className="p-3 sm:p-4 bg-sapphire-950 border-t border-white/10 flex gap-2">
                  <input
                    type="text"
                    value={simMessage}
                    onChange={e => setSimMessage(e.target.value)}
                    placeholder={`Escribe como paciente en ${simChannel.toUpperCase()}...`}
                    className="flex-1 bg-sapphire-900/50 border border-white/15 rounded-xl px-4 py-2.5 text-sm text-white placeholder-titanium-400 focus:outline-none focus:ring-2 focus:ring-cyan-bright transition"
                  />
                  <button
                    type="submit"
                    disabled={simLoading || !simMessage.trim()}
                    className="bg-cyan-bright hover:bg-cyan-bright/90 disabled:opacity-50 text-abyssal px-5 py-2.5 rounded-xl text-sm font-bold flex items-center gap-2 transition shadow-cyan-glow cursor-pointer"
                  >
                    <Send className="w-4 h-4" />
                    Enviar
                  </button>
                </form>
              </section>

              {/* Google Calendar Agenda */}
              <section className="lg:col-span-5 glass-panel rounded-3xl border border-cyan-bright/25 shadow-2xl overflow-hidden flex flex-col bg-sapphire-950/90">
                <div className="p-4 sm:p-5 border-b border-white/10 flex items-center justify-between bg-sapphire-900/40">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-teal-500/20 text-teal-300 flex items-center justify-center border border-teal-500/30">
                      <CalendarIcon className="w-4 h-4" />
                    </div>
                    <div>
                      <h2 className="font-bold text-sm text-white leading-tight">Agenda en Google Calendar</h2>
                      <p className="text-[11px] text-titanium-400">Franjas de 45 min con bloqueo anti-colisión</p>
                    </div>
                  </div>
                  <span className="text-xs font-mono font-bold px-2.5 py-1 bg-cyan-bright/10 text-cyan-bright rounded-full border border-cyan-bright/30">
                    {appointments.length} turnos
                  </span>
                </div>

                {/* Date Selector & Available 45-min slots */}
                <div className="p-4 bg-abyssal/60 border-b border-white/10 space-y-3">
                  <div className="flex items-center justify-between gap-2">
                    <label className="text-xs font-bold text-titanium-300 flex items-center gap-1.5">
                      <CalendarCheck className="w-4 h-4 text-cyan-bright" /> Consultar Día:
                    </label>
                    <input
                      type="date"
                      value={selectedDate}
                      onChange={e => {
                        setSelectedDate(e.target.value);
                        fetchSlots(e.target.value);
                      }}
                      className="text-xs font-semibold bg-sapphire-900/60 border border-white/20 rounded-lg px-2.5 py-1.5 text-white focus:outline-none focus:ring-1 focus:ring-cyan-bright"
                    />
                  </div>

                  {/* Dynamic 45-minute Slots Pill Box */}
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-[11px] font-bold text-titanium-400 uppercase tracking-wide">
                        Horarios Libres (45 min):
                      </span>
                      <span className="text-[10px] font-mono text-cyan-bright font-bold">
                        {loadingSlots ? 'Consultando...' : `${availableSlots.length} disponibles`}
                      </span>
                    </div>

                    <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
                      {loadingSlots ? (
                        <span className="text-xs text-titanium-400 italic">Cargando disponibilidad...</span>
                      ) : availableSlots.length === 0 ? (
                        <span className="text-xs text-titanium-400 italic">No hay horarios libres para esta fecha.</span>
                      ) : (
                        availableSlots.map((slot, i) => (
                          <span
                            key={i}
                            className="text-xs font-mono font-bold px-2.5 py-1 rounded-lg bg-cyan-bright/10 text-cyan-bright border border-cyan-bright/30"
                          >
                            {slot} hs
                          </span>
                        ))
                      )}
                    </div>
                  </div>
                </div>

                {/* Confirmed Appointments List */}
                <div className="p-4 flex-1 overflow-y-auto max-h-[380px] space-y-3">
                  {appointments.length === 0 ? (
                    <div className="text-center py-12 text-titanium-400 text-xs italic">
                      No hay citas agendadas registradas aún.
                    </div>
                  ) : (
                    appointments.map(appt => (
                      <div
                        key={appt.id}
                        className="p-3.5 rounded-xl bg-sapphire-900/40 border border-white/10 hover:border-cyan-bright/40 transition flex items-center justify-between"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-sm text-white">{appt.patient_name}</span>
                            <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded-md bg-white/10 text-cyan-bright">
                              {appt.channel}
                            </span>
                          </div>
                          <p className="text-xs text-titanium-300">{appt.treatment}</p>
                          <div className="flex items-center gap-2 text-[11px] text-titanium-400">
                            <span>📅 {appt.date}</span>
                            <span>⏰ {appt.time} hs</span>
                          </div>
                        </div>
                        <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" /> Confirmado
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </section>

            </div>
          </div>
        )}

        {/* TAB 2: 3-AGENT PIPELINE VISUALIZER */}
        {activeDashboardTab === 'pipeline' && (
          <section className="space-y-6">
            <div className="text-center max-w-3xl mx-auto space-y-2 mb-8">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full glass-badge text-xs font-bold uppercase tracking-wider">
                <BrainCircuit className="w-3.5 h-3.5" />
                <span>Arquitectura Multi-Agente Modular</span>
              </span>
              <h2 className="text-2xl font-extrabold text-white">Pipeline de Decisión Clínica</h2>
              <p className="text-xs text-titanium-400">
                Cada agente opera en su propio directorio con aislamiento estricto, memoria en Neon Postgres (`pgvector`) y límite de 512 MB de RAM.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Agent 1: ReaderAgent */}
              <div className="glass-card rounded-2xl p-6 border border-cyan-bright/30 relative overflow-hidden flex flex-col justify-between">
                <div>
                  <div className="w-12 h-12 rounded-xl bg-cyan-bright/10 border border-cyan-bright/40 text-cyan-bright flex items-center justify-center mb-4">
                    <Smartphone className="w-6 h-6" />
                  </div>
                  <span className="text-[10px] font-mono uppercase tracking-widest text-cyan-bright font-bold">Paso 1 • Ingesta</span>
                  <h3 className="text-lg font-bold text-white mt-1">ReaderAgent ("El que Lee")</h3>
                  <p className="text-xs text-titanium-300 mt-2 leading-relaxed">
                    Normaliza mensajes multicanal (WhatsApp Baileys, Instagram, Facebook, YouTube) en el contrato <code className="text-cyan-bright">OmniChannelMessage</code>.
                  </p>

                  <div className="mt-4 pt-3 border-t border-white/10 space-y-2 text-xs">
                    <div className="flex items-center justify-between text-titanium-400">
                      <span>Módulo de Memoria:</span>
                      <strong className="text-white font-mono">ReaderMemory</strong>
                    </div>
                    <div className="flex items-center justify-between text-titanium-400">
                      <span>Ventana de Contexto:</span>
                      <strong className="text-cyan-bright font-mono">Últimos 4 turnos</strong>
                    </div>
                    <div className="flex items-center justify-between text-titanium-400">
                      <span>Tabla Neon:</span>
                      <strong className="text-purple-300 font-mono">conversation_turns</strong>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-white/10 flex items-center gap-1.5 text-xs text-emerald-400 font-semibold">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Normalización Zero-Loss
                </div>
              </div>

              {/* Agent 2: AnalyzerAgent */}
              <div className="glass-card rounded-2xl p-6 border border-purple-500/30 relative overflow-hidden flex flex-col justify-between">
                <div>
                  <div className="w-12 h-12 rounded-xl bg-purple-950/80 border border-purple-500/40 text-purple-300 flex items-center justify-center mb-4">
                    <Cpu className="w-6 h-6" />
                  </div>
                  <span className="text-[10px] font-mono uppercase tracking-widest text-purple-300 font-bold">Paso 2 • Semántica</span>
                  <h3 className="text-lg font-bold text-white mt-1">AnalyzerAgent ("El que Analiza")</h3>
                  <p className="text-xs text-titanium-300 mt-2 leading-relaxed">
                    Clasifica la intención clínica, detecta niveles de dolor (urgencia vs rutina) y busca contexto en la base de conocimientos RAG.
                  </p>

                  <div className="mt-4 pt-3 border-t border-white/10 space-y-2 text-xs">
                    <div className="flex items-center justify-between text-titanium-400">
                      <span>Módulo de Memoria:</span>
                      <strong className="text-white font-mono">AnalyzerMemory</strong>
                    </div>
                    <div className="flex items-center justify-between text-titanium-400">
                      <span>Búsqueda Vectorial:</span>
                      <strong className="text-purple-300 font-mono">pgvector Cosine Sim</strong>
                    </div>
                    <div className="flex items-center justify-between text-titanium-400">
                      <span>Tabla Neon:</span>
                      <strong className="text-purple-300 font-mono">treatment_embeddings</strong>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-white/10 flex items-center gap-1.5 text-xs text-purple-300 font-semibold">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Clasificación de Intención
                </div>
              </div>

              {/* Agent 3: SolverAgent */}
              <div className="glass-card rounded-2xl p-6 border border-teal-500/30 relative overflow-hidden flex flex-col justify-between">
                <div>
                  <div className="w-12 h-12 rounded-xl bg-teal-950/80 border border-teal-500/40 text-teal-300 flex items-center justify-center mb-4">
                    <Stethoscope className="w-6 h-6" />
                  </div>
                  <span className="text-[10px] font-mono uppercase tracking-widest text-teal-300 font-bold">Paso 3 • Resolución</span>
                  <h3 className="text-lg font-bold text-white mt-1">SolverAgent ("El que Resuelve")</h3>
                  <p className="text-xs text-titanium-300 mt-2 leading-relaxed">
                    Aplica triage clínico sin prescripción indebida, valida disponibilidad en Google Calendar, previene colisiones y responde al paciente.
                  </p>

                  <div className="mt-4 pt-3 border-t border-white/10 space-y-2 text-xs">
                    <div className="flex items-center justify-between text-titanium-400">
                      <span>Módulo de Memoria:</span>
                      <strong className="text-white font-mono">SolverMemory</strong>
                    </div>
                    <div className="flex items-center justify-between text-titanium-400">
                      <span>Auto-Pruning:</span>
                      <strong className="text-teal-300 font-mono">Conserva top 4 turnos</strong>
                    </div>
                    <div className="flex items-center justify-between text-titanium-400">
                      <span>Inferencia LLM:</span>
                      <strong className="text-cyan-bright font-mono">Groq Llama 3.3 70B</strong>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-white/10 flex items-center gap-1.5 text-xs text-teal-300 font-semibold">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Agenda Google Calendar
                </div>
              </div>
            </div>
          </section>
        )}

        {/* TAB 3: MEDIA GALLERY & PROMO VIDEO REEL */}
        {activeDashboardTab === 'media' && (
          <section className="space-y-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-extrabold text-white tracking-tight flex items-center gap-2">
                  <Film className="w-5 h-5 text-cyan-bright" />
                  Centro de Activos Visuales & Video Reel
                </h2>
                <p className="text-xs text-titanium-400">
                  Activos generados para redes sociales y el nuevo video promocional de alta definición.
                </p>
              </div>
              <span className="text-xs font-mono font-bold text-cyan-bright bg-cyan-bright/10 px-3 py-1 rounded-xl border border-cyan-bright/30">
                5 Activos • 2 Videos HD
              </span>
            </div>

            {/* Video Showcase Cards Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* 1:1 Reel Showcase Card */}
              <div className="glass-panel rounded-3xl p-6 border border-cyan-bright/35 shadow-2xl bg-sapphire-950/90 space-y-4 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-mono text-cyan-bright font-bold uppercase tracking-wider">
                      ✦ Reel Cuadrado (1:1)
                    </span>
                    <span className="px-2.5 py-0.5 rounded-lg bg-cyan-bright/10 border border-cyan-bright/30 text-[11px] font-mono text-cyan-bright font-bold">
                      2.90 MB • Web & Feed
                    </span>
                  </div>
                  <h3 className="text-lg font-extrabold text-white mt-1">Lumina Promo Reel (1080x1080)</h3>
                  <p className="text-xs text-titanium-300 mt-1">
                    Cámara Ken Burns 3D, disolvencias cruzadas, pista ambiental AAC y streaming web.
                  </p>
                </div>

                <div className="relative w-full aspect-square rounded-2xl overflow-hidden border border-cyan-bright/40 shadow-2xl bg-abyssal">
                  <video
                    src="/social-kit/lumina-promo-reel.mp4"
                    poster="/social-kit/lumina-cover.png"
                    controls
                    loop
                    playsInline
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>

              {/* 9:16 Vertical Short Showcase Card */}
              <div className="glass-panel rounded-3xl p-6 border border-teal-400/35 shadow-2xl bg-sapphire-950/90 space-y-4 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-mono text-teal-300 font-bold uppercase tracking-wider">
                      ✦ Short / Reel Vertical (9:16)
                    </span>
                    <span className="px-2.5 py-0.5 rounded-lg bg-teal-400/10 border border-teal-400/30 text-[11px] font-mono text-teal-300 font-bold">
                      3.70 MB • Shorts & Reels
                    </span>
                  </div>
                  <h3 className="text-lg font-extrabold text-white mt-1">Lumina Vertical Short (1080x1920)</h3>
                  <p className="text-xs text-titanium-300 mt-1">
                    Formato vertical cinematográfico para Instagram Reels, YouTube Shorts y Facebook Reels.
                  </p>
                </div>

                <div className="relative w-full max-w-[280px] mx-auto aspect-[9/16] rounded-2xl overflow-hidden border border-teal-400/40 shadow-2xl bg-abyssal">
                  <video
                    src="/social-kit/lumina-short-9x16.mp4"
                    poster="/social-kit/lumina-cover.png"
                    controls
                    loop
                    playsInline
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>
            </div>

            {/* Visual Assets Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {CLINICAL_ASSETS.map((asset, idx) => (
                <div
                  key={idx}
                  className="glass-card rounded-2xl overflow-hidden border border-white/10 hover:border-cyan-bright/40 transition-all duration-300 flex flex-col justify-between group shadow-xl"
                >
                  <div className="relative w-full aspect-square overflow-hidden bg-abyssal">
                    <Image
                      src={`/social-kit/${asset.filename}`}
                      alt={asset.name}
                      fill
                      sizes="(max-width: 768px) 100vw, 33vw"
                      className="object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute top-3 left-3">
                      <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-abyssal/80 text-cyan-bright border border-cyan-bright/30 backdrop-blur-md">
                        {asset.type}
                      </span>
                    </div>
                  </div>

                  <div className="p-4 space-y-2 bg-sapphire-950/80">
                    <h4 className="font-bold text-sm text-white group-hover:text-cyan-bright transition-colors">
                      {asset.name}
                    </h4>
                    <p className="text-xs text-titanium-400">
                      {asset.desc}
                    </p>
                    <div className="pt-2 border-t border-white/10 flex items-center justify-between text-[11px] text-titanium-500 font-mono">
                      <span>/social-kit/{asset.filename}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

      </main>

      {/* WhatsApp QR Modal */}
      {showQrModal && (
        <div className="fixed inset-0 z-50 bg-abyssal/90 backdrop-blur-md flex items-center justify-center p-4">
          <div className="glass-panel rounded-3xl p-6 sm:p-8 max-w-md w-full border border-cyan-bright/40 shadow-2xl relative bg-sapphire-950">
            <div className="text-center space-y-3 mb-6">
              <div className="w-12 h-12 mx-auto rounded-2xl bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 flex items-center justify-center">
                <QrCode className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-white">Vincular WhatsApp de la Clínica</h3>
              <p className="text-xs text-titanium-300">
                Abre WhatsApp en tu teléfono, ve a <strong>Dispositivos vinculados</strong> y escanea el código.
              </p>
            </div>

            <div className="bg-white p-4 rounded-2xl flex items-center justify-center min-h-[260px] shadow-inner">
              {qrCode ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={qrCode} alt="WhatsApp QR Code" className="w-60 h-60 object-contain" />
              ) : waData.status === 'connected' ? (
                <div className="text-center space-y-2 text-emerald-600">
                  <CheckCircle2 className="w-12 h-12 mx-auto" />
                  <p className="font-bold text-sm">¡WhatsApp ya está conectado!</p>
                  <p className="text-xs text-slate-500">{waData.user}</p>
                </div>
              ) : (
                <div className="text-center space-y-3 text-slate-500">
                  <RefreshCw className="w-8 h-8 animate-spin mx-auto text-teal-600" />
                  <p className="text-xs font-semibold">Generando código QR...</p>
                  <button
                    onClick={handleConnectWhatsApp}
                    disabled={isConnectingWA}
                    className="text-xs bg-teal-600 text-white px-3 py-1.5 rounded-lg font-bold"
                  >
                    Iniciar Conexión
                  </button>
                </div>
              )}
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setShowQrModal(false)}
                className="w-full py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold transition cursor-pointer"
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
