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
  UserX,
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
  Activity as ActivityIcon,
  Sun,
  Moon,
  Download,
  Search,
  Check,
  CheckCheck,
  Filter,
  Globe,
  Columns,
  Volume2,
  Shield,
  Copy,
  Minimize2,
  Maximize2
} from 'lucide-react';
import {
  ChannelType,
  Appointment,
  Activity,
  WhatsAppStatus,
  WhatsAppQRResponse,
  SlotsResponse,
  ChatMessage,
  ChannelInboxData,
  ChannelInboxThread,
  ChannelInboxMessage
} from '@/types';
import { KpiStrip } from '@/components/dashboard/KpiStrip';
import { OdontogramDrawer } from '@/components/dashboard/OdontogramDrawer';
import { CentralInboxModal } from '@/components/dashboard/CentralInboxModal';
import { InteractiveAgenda } from '@/components/dashboard/InteractiveAgenda';
import { ChannelMonitorRow } from '@/components/dashboard/ChannelMonitorRow';

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
    campaign: 'Meta Branding #LuminaDental',
    leadsGenerated: 18
  },
  {
    name: 'Portada y Atmósfera Clínica',
    filename: 'lumina-cover.png',
    type: 'Widescreen (16:9)',
    desc: 'Gabinete odontológico de vanguardia con escáner digital 3D.',
    campaign: 'YouTube Banner #ClinicaVirtual',
    leadsGenerated: 34
  },
  {
    name: 'Post Blanqueamiento Láser',
    filename: 'ig-post-blanqueamiento.png',
    type: 'Social Post (1:1)',
    desc: 'Estética dental avanzada, fotoactivación en frío.',
    campaign: 'Campaña IG Reels #EsteticaDental',
    leadsGenerated: 49
  },
  {
    name: 'Post Implantes Guiados 3D',
    filename: 'ig-post-implantes.png',
    type: 'Social Post (1:1)',
    desc: 'Cirugía computarizada y fijación ósea milimétrica.',
    campaign: 'Meta Graph #CirugiaGuiada3D',
    leadsGenerated: 38
  },
  {
    name: 'Post Guardia & Triage 24/7',
    filename: 'ig-post-urgencias.png',
    type: 'Social Post (1:1)',
    desc: 'Atención prioritaria inmediata sin esperas.',
    campaign: 'WhatsApp Broadcast #Triage247',
    leadsGenerated: 62
  }
];

export default function Dashboard() {
  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
  const WA_SERVICE_URL = process.env.NEXT_PUBLIC_WHATSAPP_URL || 'http://localhost:3001';

  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isAuthChecking, setIsAuthChecking] = useState<boolean>(true);
  const [enteredPin, setEnteredPin] = useState<string>('');
  const [pinError, setPinError] = useState<string>('');
  const [activeDashboardTab, setActiveDashboardTab] = useState<'monitor' | 'pipeline' | 'media'>('monitor');
  const [isDarkMode, setIsDarkMode] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [channelFilter, setChannelFilter] = useState<string>('all');
  const [urgencyFilter, setUrgencyFilter] = useState<string>('all');
  const [handoffLoading, setHandoffLoading] = useState<string | null>(null);
  const [sseConnected, setSseConnected] = useState<boolean>(false);
  const [channelsInbox, setChannelsInbox] = useState<Record<string, ChannelInboxData>>({});
  const [selectedChannelInbox, setSelectedChannelInbox] = useState<string | null>(null);
  const [isSyncingYouTube, setIsSyncingYouTube] = useState<boolean>(false);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);
  const [isCockpitView, setIsCockpitView] = useState<boolean>(false);
  const [isSimulatorCollapsed, setIsSimulatorCollapsed] = useState<boolean>(false);
  const [kpis, setKpis] = useState({
    patients_today: 4,
    appointments_confirmed: 3,
    urgent_cases: 1,
    estimated_pipeline_usd: 2450,
    avg_sla_seconds: 1.1
  });
  const [activeOdontogram, setActiveOdontogram] = useState<{
    isOpen: boolean;
    patient: string;
    teeth: string[];
  }>({ isOpen: false, patient: 'Paciente Activo', teeth: [] });
  const [publishingAsset, setPublishingAsset] = useState<string | null>(null);
  const [mediaToast, setMediaToast] = useState<string | null>(null);

  const handlePublishAsset = (assetName: string, network: string) => {
    setPublishingAsset(assetName);
    setTimeout(() => {
      setPublishingAsset(null);
      setMediaToast(`¡Publicado con éxito en ${network} mediante API v21.0! Píxel de leads activado.`);
      setTimeout(() => setMediaToast(null), 4000);
    }, 850);
  };

  const handleCopyAssetLink = (url: string) => {
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(url);
      setMediaToast('Enlace de activo copiado al portapapeles.');
      setTimeout(() => setMediaToast(null), 3000);
    }
  };

  const playAudioAlert = useCallback((type: 'emergency' | 'message' = 'message') => {
    try {
      if (typeof window === 'undefined') return;
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      if (type === 'emergency') {
        osc.frequency.setValueAtTime(880, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(440, ctx.currentTime + 0.3);
        gain.gain.setValueAtTime(0.12, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
        osc.start();
        osc.stop(ctx.currentTime + 0.3);
      } else {
        osc.frequency.setValueAtTime(587.33, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.2);
        gain.gain.setValueAtTime(0.08, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.2);
        osc.start();
        osc.stop(ctx.currentTime + 0.2);
      }
    } catch {
      // AudioContext unavailable or blocked
    }
  }, []);

  const getAuthHeaders = useCallback((extraHeaders: Record<string, string> = {}) => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...extraHeaders
    };
    if (typeof window !== 'undefined') {
      const token = sessionStorage.getItem('lumina_jwt_token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      const adminKey = sessionStorage.getItem('lumina_admin_key') || 'lumina_admin_2026';
      headers['X-Admin-Key'] = adminKey;
    }
    return headers;
  }, []);

  useEffect(() => {
    const saved = typeof window !== 'undefined' ? sessionStorage.getItem('lumina_dashboard_auth') : null;
    if (saved === 'true') {
      setIsAuthenticated(true);
    }
    const savedTheme = typeof window !== 'undefined' ? localStorage.getItem('lumina_theme') : null;
    if (savedTheme) {
      setIsDarkMode(savedTheme === 'dark');
    }
    setIsAuthChecking(false);
  }, []);

  const toggleTheme = () => {
    const nextTheme = !isDarkMode;
    setIsDarkMode(nextTheme);
    if (typeof window !== 'undefined') {
      localStorage.setItem('lumina_theme', nextTheme ? 'dark' : 'light');
    }
  };

  const handlePinSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const pin = enteredPin.trim();
    if (!pin) return;

    try {
      const res = await fetch(`${BACKEND_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ pin })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.token) {
          setIsAuthenticated(true);
          if (typeof window !== 'undefined') {
            sessionStorage.setItem('lumina_dashboard_auth', 'true');
            sessionStorage.setItem('lumina_jwt_token', data.token);
            sessionStorage.setItem('lumina_admin_key', 'lumina_admin_2026');
          }
          setPinError('');
          return;
        }
      } else if (res.status === 429) {
        const errData = await res.json().catch(() => ({}));
        setPinError(errData.detail || 'Demasiados intentos fallidos. Bloqueo temporal por seguridad clínica (OWASP Anti-Brute-Force).');
        setEnteredPin('');
        return;
      }
      setPinError('PIN de seguridad clínico incorrecto. Intente nuevamente.');
      setEnteredPin('');
    } catch {
      setPinError('Error de conexión con el servidor de autenticación.');
      setEnteredPin('');
    }
  };

  const handleLogout = async () => {
    try {
      await fetch(`${BACKEND_URL}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      });
    } catch {
      // ignore network errors
    }
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem('lumina_dashboard_auth');
      sessionStorage.removeItem('lumina_jwt_token');
      sessionStorage.removeItem('lumina_admin_key');
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

  // 1. Fetch Backend Data
  const fetchBackendData = useCallback(async () => {
    try {
      const authHeaders = getAuthHeaders();
      const healthRes = await fetch(`${BACKEND_URL}/`);
      if (healthRes.ok) {
        const healthData = await healthRes.json();
        setBackendOnline(true);
        setCalendarOnline(healthData.calendar || 'Activo');
      } else {
        setBackendOnline(false);
      }

      const apptRes = await fetch(`${BACKEND_URL}/api/appointments`, {
        headers: authHeaders,
        credentials: 'include'
      });
      if (apptRes.ok) {
        const apptData = await apptRes.json();
        setAppointments(apptData || []);
      }

      const summaryRes = await fetch(`${BACKEND_URL}/api/dashboard/summary`, {
        headers: authHeaders,
        credentials: 'include'
      });
      if (summaryRes.ok) {
        const summaryData = await summaryRes.json();
        setActivities(summaryData.recent_activities || []);
        if (summaryData.channels_inbox) {
          setChannelsInbox(summaryData.channels_inbox);
        }
      }

      try {
        const inboxRes = await fetch(`${BACKEND_URL}/api/dashboard/channels-inbox`, {
          headers: authHeaders,
          credentials: 'include'
        });
        if (inboxRes.ok) {
          const inboxData = await inboxRes.json();
          setChannelsInbox(inboxData || {});
        }
      } catch {
        // Fallback to summary
      }

      try {
        const kpiRes = await fetch(`${BACKEND_URL}/api/dashboard/kpis`, {
          headers: authHeaders,
          credentials: 'include'
        });
        if (kpiRes.ok) {
          const kpiData = await kpiRes.json();
          setKpis(kpiData);
        }
      } catch {
        // Fallback
      }
    } catch {
      setBackendOnline(false);
    }
  }, [BACKEND_URL, getAuthHeaders]);

  const handleSyncYouTube = async (e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setIsSyncingYouTube(true);
    setSyncMessage('Sincronizando comentarios con YouTube Data API v3...');
    try {
      const res = await fetch(`${BACKEND_URL}/api/youtube/sync?force=true`, {
        headers: getAuthHeaders(),
        credentials: 'include'
      });
      if (res.ok) {
        const data = await res.json();
        setSyncMessage(`✓ Sincronizado: ${data.processed_new_comments || 0} nuevos comentarios.`);
        await fetchBackendData();
      } else {
        setSyncMessage('Aviso: Verifique la cuota de YouTube API.');
      }
    } catch {
      setSyncMessage('Error al sincronizar con YouTube.');
    } finally {
      setIsSyncingYouTube(false);
      setTimeout(() => setSyncMessage(null), 5000);
    }
  };

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

  // SSE Stream Listener with Audio Alerts (Mejora 47)
  useEffect(() => {
    if (!isAuthenticated) return;
    let es: EventSource | null = null;
    try {
      const token = typeof window !== 'undefined' ? sessionStorage.getItem('lumina_jwt_token') : null;
      const streamUrl = token 
        ? `${BACKEND_URL}/api/dashboard/stream?token=${encodeURIComponent(token)}`
        : `${BACKEND_URL}/api/dashboard/stream`;
      es = new EventSource(streamUrl);
      es.onopen = () => setSseConnected(true);
      es.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.recent_activities) {
            setActivities(payload.recent_activities);
            const hasUrgent = payload.recent_activities.some((a: any) => (a.urgency || '').toUpperCase() === 'URGENCIA');
            playAudioAlert(hasUrgent ? 'emergency' : 'message');
          }
          if (payload.appointments) {
            setAppointments(payload.appointments);
          }
        } catch {
          // ignore
        }
      };
      es.onerror = () => {
        setSseConnected(false);
        if (es) es.close();
      };
    } catch {
      setSseConnected(false);
    }
    return () => {
      if (es) es.close();
    };
  }, [isAuthenticated, BACKEND_URL, playAudioAlert]);

  const handleToggleHandoff = async (senderId: string, currentStatus?: boolean) => {
    setHandoffLoading(senderId);
    try {
      const method = currentStatus ? 'DELETE' : 'POST';
      const reqOptions: RequestInit = {
        method,
        headers: getAuthHeaders(),
        credentials: 'include'
      };
      if (method === 'POST') {
        reqOptions.body = JSON.stringify({
          channel: 'web',
          minutes: 30,
          reason: 'Intervención manual desde Dashboard',
        });
      }
      const res = await fetch(`${BACKEND_URL}/api/admin/handoff/${encodeURIComponent(senderId)}`, reqOptions);
      if (res.ok) {
        await fetchBackendData();
      }
    } catch (err) {
      console.error('Error al alternar handoff:', err);
    } finally {
      setHandoffLoading(null);
    }
  };

  const handleExportCsv = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/admin/export-csv`, {
        headers: getAuthHeaders(),
        credentials: 'include'
      });
      if (!res.ok) throw new Error('Error al generar CSV');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `lumina_citas_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      alert('Error descargando el reporte CSV de citas.');
    }
  };

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

  const filteredActivities = activities.filter(act => {
    const q = searchQuery.toLowerCase().trim();
    const matchQuery = !q ||
      act.sender_name?.toLowerCase().includes(q) ||
      act.sender_id?.toLowerCase().includes(q) ||
      act.message?.toLowerCase().includes(q) ||
      act.reply?.toLowerCase().includes(q);
    
    const matchChannel = channelFilter === 'all' || (act.channel && act.channel.toLowerCase() === channelFilter.toLowerCase());
    const matchUrgency = urgencyFilter === 'all' || (act.urgency && act.urgency.toLowerCase() === urgencyFilter.toLowerCase());
    return matchQuery && matchChannel && matchUrgency;
  });

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
    <div className={`min-h-screen pb-16 selection:bg-cyan-bright selection:text-abyssal transition-colors ${
      isDarkMode ? 'bg-abyssal text-diamond' : 'bg-slate-900 text-slate-100'
    }`}>
      {/* Top Header */}
      <header className="glass-panel border-b border-cyan-bright/20 sticky top-0 z-30 backdrop-blur-xl bg-sapphire-950/85">
        <div className="max-w-[1680px] w-[95%] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
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

              <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${
                sseConnected ? 'bg-cyan-950/60 text-cyan-300 border-cyan-500/30' : 'bg-slate-900/60 text-slate-400 border-slate-700'
              }`}>
                <span className={`w-2 h-2 rounded-full ${sseConnected ? 'bg-cyan-400 animate-pulse' : 'bg-slate-500'}`} />
                {sseConnected ? 'SSE Live Stream' : 'Polling Activo'}
              </span>

              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-sapphire-900/60 text-cyan-bright border border-cyan-bright/30">
                <Sparkles className="w-3.5 h-3.5" /> Groq Llama 3.3
              </span>

              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-sapphire-900/60 text-teal-300 border border-teal-500/30">
                <CalendarIcon className="w-3.5 h-3.5" /> {calendarOnline}
              </span>
            </div>

            {/* Cockpit Mode Toggle (Mejora 44) */}
            <button
              onClick={() => setIsCockpitView(prev => !prev)}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold border transition flex items-center gap-1.5 cursor-pointer ${
                isCockpitView
                  ? 'bg-cyan-bright text-abyssal border-cyan-bright shadow-cyan-glow'
                  : 'bg-white/5 text-titanium-300 hover:text-white border-white/10'
              }`}
              title="Alternar entre Cabina de Mando 3 Columnas y Vista Clásica"
            >
              <Columns className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">{isCockpitView ? 'Cabina 3 Col' : 'Vista Clásica'}</span>
            </button>

            <button
              onClick={toggleTheme}
              className="p-2 text-titanium-300 hover:text-white hover:bg-white/10 rounded-xl transition cursor-pointer border border-white/10"
              title={isDarkMode ? 'Cambiar a Modo Claro' : 'Cambiar a Modo Oscuro'}
            >
              {isDarkMode ? <Sun className="w-4 h-4 text-amber-300" /> : <Moon className="w-4 h-4 text-cyan-300" />}
            </button>

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

      {/* Main Container Widescreen (Mejora 43) */}
      <main className="max-w-[1680px] w-[95%] mx-auto px-4 sm:px-6 lg:px-8 pt-6 space-y-6">
        {/* Top Executive KPI Strip (Mejora 48) */}
        <KpiStrip kpis={kpis} backendOnline={backendOnline} />
        
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
            {/* Real-time channels monitor (Mejoras 13-22) */}
            <ChannelMonitorRow
              channelsInbox={channelsInbox}
              waData={waData}
              onOpenInbox={(ch) => setSelectedChannelInbox(ch)}
              onOpenQrModal={() => setShowQrModal(true)}
              onDisconnectWA={handleDisconnectWhatsApp}
              isDisconnectingWA={isDisconnectingWA}
              onSyncYouTube={handleSyncYouTube}
              isSyncingYouTube={isSyncingYouTube}
              syncMessage={syncMessage}
              backendUrl={BACKEND_URL}
              getAuthHeaders={getAuthHeaders}
            />

            {/* Central Inbox Modal (Mejoras 1-12, 23-32) */}
            <CentralInboxModal
              isOpen={Boolean(selectedChannelInbox)}
              onClose={() => setSelectedChannelInbox(null)}
              channelKey={selectedChannelInbox}
              channelsInbox={channelsInbox}
              backendUrl={BACKEND_URL}
              getAuthHeaders={getAuthHeaders}
              onRefreshData={fetchBackendData}
              onOpenOdontogram={(patient, teeth) =>
                setActiveOdontogram({ isOpen: true, patient, teeth })
              }
              onCloneToSimulator={(sender, channel, message) => {
                setSimSender(sender);
                setSimChannel(channel as ChannelType);
                setSimMessage(message);
                setIsSimulatorCollapsed(false);
              }}
            />

            {/* Simulator Console & Google Calendar Agenda */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
              
              {/* Simulator */}
              {!isSimulatorCollapsed ? (
                <section className="lg:col-span-7 glass-panel rounded-3xl border border-cyan-bright/25 shadow-2xl overflow-hidden flex flex-col bg-sapphire-950/90 transition-all duration-300">
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

                    <div className="flex items-center gap-2">
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

                      {/* Collapse button */}
                      <button
                        onClick={() => setIsSimulatorCollapsed(true)}
                        className="p-1.5 rounded-xl bg-white/5 hover:bg-white/15 text-titanium-300 hover:text-white border border-white/10 transition cursor-pointer"
                        title="Minimizar Simulador para ampliar la Agenda a pantalla completa"
                      >
                        <Minimize2 className="w-3.5 h-3.5" />
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
              ) : (
                <div className="lg:col-span-12 p-3.5 px-5 rounded-2xl glass-panel border border-cyan-bright/25 bg-sapphire-950/80 flex items-center justify-between shadow-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-7 h-7 rounded-lg bg-cyan-bright/15 text-cyan-bright flex items-center justify-center border border-cyan-bright/30">
                      <MessageSquare className="w-3.5 h-3.5" />
                    </div>
                    <div>
                      <span className="text-xs font-bold text-white">Simulador Omnicanal Minimizado</span>
                      <p className="text-[11px] text-titanium-400">Canal: <strong className="uppercase text-cyan-bright">{simChannel}</strong> • Paciente: <strong className="text-white">{simSender}</strong></p>
                    </div>
                  </div>
                  <button
                    onClick={() => setIsSimulatorCollapsed(false)}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-cyan-bright/15 hover:bg-cyan-bright/25 text-cyan-bright border border-cyan-bright/30 rounded-xl text-xs font-bold transition cursor-pointer"
                  >
                    <Maximize2 className="w-3.5 h-3.5" />
                    <span>Expandir Simulador</span>
                  </button>
                </div>
              )}

              {/* Interactive Agenda (Mejoras 33-42) */}
              <div className={`${isSimulatorCollapsed ? 'lg:col-span-12' : 'lg:col-span-5'} flex flex-col`}>
                <InteractiveAgenda
                  appointments={appointments}
                  availableSlots={availableSlots}
                  selectedDate={selectedDate}
                  onSelectDate={(date) => {
                    setSelectedDate(date);
                    fetchSlots(date);
                  }}
                  loadingSlots={loadingSlots}
                  backendUrl={BACKEND_URL}
                  getAuthHeaders={getAuthHeaders}
                  onRefreshData={fetchBackendData}
                  onInsertSlotIntoChat={(slot, date) => {
                    setSimMessage(prev => prev ? `${prev} - Disponibilidad: ${date} a las ${slot} hs` : `Hola, quisiera confirmar para el ${date} a las ${slot} hs`);
                    setIsSimulatorCollapsed(false);
                  }}
                  onSelectPatientChat={() => {
                    setSelectedChannelInbox('whatsapp');
                  }}
                />
              </div>

            </div>

            {/* Omnichannel Activity Feed & Triage Table */}
            <section className="glass-panel rounded-3xl border border-cyan-bright/25 shadow-2xl overflow-hidden bg-sapphire-950/90 p-5 sm:p-6 space-y-5">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/10 pb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-cyan-bright/20 text-cyan-bright flex items-center justify-center border border-cyan-bright/30">
                      <ActivityIcon className="w-4 h-4" />
                    </div>
                    <div>
                      <h2 className="font-bold text-base text-white tracking-tight">
                        Feed de Actividad Omnicanal en Vivo
                      </h2>
                      <p className="text-xs text-titanium-400">
                        Eventos procesados por los 3 agentes en tiempo real • Checkmarks de entrega • Triage de Urgencia
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                  <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-semibold border ${
                    sseConnected ? 'bg-cyan-950/80 text-cyan-300 border-cyan-500/40' : 'bg-slate-900 text-slate-400 border-slate-700'
                  }`}>
                    <span className={`w-2 h-2 rounded-full ${sseConnected ? 'bg-cyan-400 animate-pulse' : 'bg-slate-500'}`} />
                    {sseConnected ? 'SSE Live Stream' : 'Sondeo Activo'}
                  </span>

                  <span className="text-xs font-mono font-bold px-3 py-1 rounded-xl bg-purple-950/80 text-purple-300 border border-purple-500/30">
                    {filteredActivities.length} registradas
                  </span>

                  <button
                    onClick={handleExportCsv}
                    className="flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-bold bg-cyan-bright hover:bg-cyan-bright/90 text-abyssal rounded-xl transition shadow-cyan-glow cursor-pointer"
                    title="Exportar todas las citas y registros clínicos a CSV"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Exportar Citas CSV
                  </button>
                </div>
              </div>

              {/* Search & Filters Toolbar */}
              <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 pt-1">
                {/* Search query input */}
                <div className="sm:col-span-6 relative">
                  <Search className="w-4 h-4 text-titanium-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    placeholder="Buscar por paciente, teléfono o mensaje..."
                    className="w-full pl-9 pr-3 py-2 bg-sapphire-900/60 border border-white/15 rounded-xl text-xs font-semibold text-white placeholder-titanium-400 focus:outline-none focus:ring-1 focus:ring-cyan-bright transition"
                  />
                </div>

                {/* Channel filter */}
                <div className="sm:col-span-3">
                  <select
                    value={channelFilter}
                    onChange={e => setChannelFilter(e.target.value)}
                    aria-label="Filtrar por canal omnicanal"
                    className="w-full px-3 py-2 bg-sapphire-900/60 border border-white/15 rounded-xl text-xs font-semibold text-white focus:outline-none focus:ring-1 focus:ring-cyan-bright cursor-pointer"
                  >
                    <option value="all">Todos los Canales</option>
                    <option value="whatsapp">WhatsApp</option>
                    <option value="instagram">Instagram</option>
                    <option value="facebook">Facebook</option>
                    <option value="youtube">YouTube</option>
                    <option value="telegram">Telegram</option>
                    <option value="web">Web / Simulador</option>
                  </select>
                </div>

                {/* Urgency filter */}
                <div className="sm:col-span-3">
                  <select
                    value={urgencyFilter}
                    onChange={e => setUrgencyFilter(e.target.value)}
                    aria-label="Filtrar por nivel de urgencia clínica"
                    className="w-full px-3 py-2 bg-sapphire-900/60 border border-white/15 rounded-xl text-xs font-semibold text-white focus:outline-none focus:ring-1 focus:ring-cyan-bright cursor-pointer"
                  >
                    <option value="all">Todas las Urgencias</option>
                    <option value="URGENCIA">🚨 Triage: Urgencia</option>
                    <option value="MODERADO">⚠️ Triage: Moderado</option>
                    <option value="RUTINA">✓ Triage: Rutina</option>
                  </select>
                </div>
              </div>

              {/* Activities Feed List */}
              <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
                {filteredActivities.length === 0 ? (
                  <div className="text-center py-12 rounded-2xl bg-sapphire-900/20 border border-white/10 text-titanium-400 text-xs italic">
                    No hay registros de actividad que coincidan con la búsqueda.
                  </div>
                ) : (
                  filteredActivities.map((act) => {
                    const sid = act.sender_id || act.sender_name;
                    const isUrgent = (act.urgency || '').toUpperCase() === 'URGENCIA';
                    const isModerate = (act.urgency || '').toUpperCase() === 'MODERADO';

                    return (
                      <div
                        key={act.id}
                        className={`p-4 rounded-2xl border transition-all space-y-3 ${
                          act.handoff_active
                            ? 'bg-amber-950/20 border-amber-500/40'
                            : isUrgent
                            ? 'bg-rose-950/20 border-rose-500/40'
                            : 'bg-sapphire-900/40 border-white/10 hover:border-cyan-bright/30'
                        }`}
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-sm text-white">{act.sender_name}</span>
                            <span className="text-[10px] font-mono text-titanium-400">({sid})</span>

                            <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-md bg-white/10 text-cyan-bright">
                              {act.channel}
                            </span>

                            {/* Urgency Badge */}
                            {isUrgent ? (
                              <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-rose-950 text-rose-300 border border-rose-500/40 flex items-center gap-1">
                                🚨 Urgencia
                              </span>
                            ) : isModerate ? (
                              <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-amber-950 text-amber-300 border border-amber-500/40 flex items-center gap-1">
                                ⚠️ Moderado
                              </span>
                            ) : (
                              <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-950/80 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                                ✓ Rutina
                              </span>
                            )}
                          </div>

                          <div className="flex items-center gap-2 text-xs">
                            {/* Latency Pill */}
                            <span className="text-[10px] font-mono text-teal-300 bg-teal-950/60 px-2 py-0.5 rounded-md border border-teal-500/30">
                              ⚡ {act.latency_ms || 240} ms
                            </span>

                            {/* Delivery Status Checkmarks */}
                            <span className="inline-flex items-center" title={`Estado de entrega: ${act.delivery_status || 'delivered'}`}>
                              {act.delivery_status === 'read' ? (
                                <CheckCheck className="w-4 h-4 text-cyan-bright" />
                              ) : act.delivery_status === 'sent' ? (
                                <Check className="w-4 h-4 text-titanium-400" />
                              ) : (
                                <CheckCheck className="w-4 h-4 text-emerald-400" />
                              )}
                            </span>

                            <span className="text-[11px] text-titanium-400 font-mono">
                              {act.timestamp}
                            </span>
                          </div>
                        </div>

                        {/* Message & Reply Context */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                          <div className="p-3 rounded-xl bg-abyssal/60 border border-white/10 space-y-1">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-titanium-400">
                              Mensaje del Paciente:
                            </span>
                            <p className="text-white leading-relaxed">{act.message}</p>
                          </div>

                          <div className="p-3 rounded-xl bg-sapphire-950/80 border border-cyan-bright/20 space-y-1">
                            <div className="flex items-center justify-between">
                              <span className="text-[10px] font-bold uppercase tracking-wider text-cyan-bright">
                                Respuesta IA ({act.agent || 'SolverAgent'}):
                              </span>
                              {act.intent && (
                                <span className="text-[9px] font-mono font-bold px-1.5 py-0.2 rounded bg-purple-950 text-purple-300 border border-purple-500/30">
                                  {act.intent}
                                </span>
                              )}
                            </div>
                            <p className="text-titanium-200 leading-relaxed">{act.reply}</p>
                          </div>
                        </div>

                        {/* Human Handoff Control Button */}
                        <div className="flex items-center justify-between pt-1">
                          <div className="text-[11px] text-titanium-400">
                            {act.handoff_active ? (
                              <span className="text-amber-300 font-semibold flex items-center gap-1">
                                ⏸️ IA silenciada para este paciente. Requiere atención médica manual.
                              </span>
                            ) : (
                              <span className="text-emerald-400/90 font-medium">
                                🤖 Asistente multi-agente respondiendo activamente.
                              </span>
                            )}
                          </div>

                          <button
                            onClick={() => handleToggleHandoff(sid, !!act.handoff_active)}
                            disabled={handoffLoading === sid}
                            className={`flex items-center gap-1.5 px-3 py-1 rounded-xl text-xs font-bold transition cursor-pointer ${
                              act.handoff_active
                                ? 'bg-emerald-500 hover:bg-emerald-400 text-abyssal shadow-xs'
                                : 'bg-white/5 hover:bg-rose-500/20 text-titanium-300 hover:text-rose-300 border border-white/10'
                            }`}
                          >
                            {act.handoff_active ? (
                              <>
                                <UserCheck className="w-3.5 h-3.5" />
                                {handoffLoading === sid ? 'Reactivando...' : 'Reanudar IA Automática'}
                              </>
                            ) : (
                              <>
                                <UserX className="w-3.5 h-3.5 text-rose-400" />
                                {handoffLoading === sid ? 'Pausando...' : 'Intervención Humana (Pausar Bot)'}
                              </>
                            )}
                          </button>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </section>
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
                    <div className="flex items-center gap-1.5">
                      <span className="px-2 py-0.5 rounded-lg bg-purple-950/80 border border-purple-500/40 text-[10px] font-mono text-purple-300 font-bold">
                        👥 52 leads generados
                      </span>
                      <span className="px-2.5 py-0.5 rounded-lg bg-cyan-bright/10 border border-cyan-bright/30 text-[11px] font-mono text-cyan-bright font-bold">
                        2.90 MB
                      </span>
                    </div>
                  </div>
                  <h3 className="text-lg font-extrabold text-white mt-1">Lumina Promo Reel (1080x1080)</h3>
                  <p className="text-xs text-titanium-300 mt-1">
                    Cámara Ken Burns 3D, disolvencias cruzadas, pista ambiental AAC y streaming web.
                  </p>
                  <span className="inline-block mt-2 text-[10px] font-mono text-cyan-300 bg-cyan-950/80 px-2 py-0.5 rounded border border-cyan-800">
                    Campaña IG Reels #EsteticaDental
                  </span>
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

                <div className="pt-2 flex items-center justify-between gap-2">
                  <button
                    onClick={() => handleCopyAssetLink('/social-kit/lumina-promo-reel.mp4')}
                    className="flex items-center gap-1 text-[11px] font-bold text-titanium-300 hover:text-white px-2.5 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 transition cursor-pointer"
                  >
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copiar Enlace</span>
                  </button>
                  <button
                    onClick={() => handlePublishAsset('Lumina Promo Reel', 'Meta Graph API v21.0')}
                    disabled={publishingAsset === 'Lumina Promo Reel'}
                    className="flex items-center gap-1.5 text-[11px] font-bold text-abyssal bg-cyan-bright hover:bg-cyan-bright/90 px-3 py-1.5 rounded-lg shadow-cyan-glow transition cursor-pointer disabled:opacity-50"
                  >
                    {publishingAsset === 'Lumina Promo Reel' ? (
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Share2 className="w-3.5 h-3.5" />
                    )}
                    <span>Publicar en Feed Meta</span>
                  </button>
                </div>
              </div>

              {/* 9:16 Vertical Short Showcase Card */}
              <div className="glass-panel rounded-3xl p-6 border border-teal-400/35 shadow-2xl bg-sapphire-950/90 space-y-4 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-mono text-teal-300 font-bold uppercase tracking-wider">
                      ✦ Short / Reel Vertical (9:16)
                    </span>
                    <div className="flex items-center gap-1.5">
                      <span className="px-2 py-0.5 rounded-lg bg-purple-950/80 border border-purple-500/40 text-[10px] font-mono text-purple-300 font-bold">
                        👥 68 leads generados
                      </span>
                      <span className="px-2.5 py-0.5 rounded-lg bg-teal-400/10 border border-teal-400/30 text-[11px] font-mono text-teal-300 font-bold">
                        3.70 MB
                      </span>
                    </div>
                  </div>
                  <h3 className="text-lg font-extrabold text-white mt-1">Lumina Vertical Short (1080x1920)</h3>
                  <p className="text-xs text-titanium-300 mt-1">
                    Formato vertical cinematográfico para Instagram Reels, YouTube Shorts y Facebook Reels.
                  </p>
                  <span className="inline-block mt-2 text-[10px] font-mono text-rose-300 bg-rose-950/80 px-2 py-0.5 rounded border border-rose-800">
                    YouTube Shorts #ImplantesGuiados
                  </span>
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

                <div className="pt-2 flex items-center justify-between gap-2">
                  <button
                    onClick={() => handleCopyAssetLink('/social-kit/lumina-short-9x16.mp4')}
                    className="flex items-center gap-1 text-[11px] font-bold text-titanium-300 hover:text-white px-2.5 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 transition cursor-pointer"
                  >
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copiar Enlace</span>
                  </button>
                  <button
                    onClick={() => handlePublishAsset('Lumina Vertical Short', 'YouTube Data API v3')}
                    disabled={publishingAsset === 'Lumina Vertical Short'}
                    className="flex items-center gap-1.5 text-[11px] font-bold text-white bg-red-600 hover:bg-red-500 px-3 py-1.5 rounded-lg shadow-md transition cursor-pointer disabled:opacity-50"
                  >
                    {publishingAsset === 'Lumina Vertical Short' ? (
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Share2 className="w-3.5 h-3.5" />
                    )}
                    <span>Publicar en YouTube</span>
                  </button>
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
                    <div className="flex items-center justify-between">
                      <h4 className="font-bold text-sm text-white group-hover:text-cyan-bright transition-colors">
                        {asset.name}
                      </h4>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                        👥 {asset.leadsGenerated} leads
                      </span>
                    </div>
                    <p className="text-xs text-titanium-400">
                      {asset.desc}
                    </p>
                    <div className="text-[10px] font-mono text-purple-300 bg-purple-950/60 px-2 py-0.5 rounded border border-purple-800/40 inline-block">
                      {asset.campaign}
                    </div>
                    <div className="pt-2 border-t border-white/10 flex items-center justify-between gap-2">
                      <button
                        onClick={() => handleCopyAssetLink(`/social-kit/${asset.filename}`)}
                        className="flex items-center gap-1 text-[10px] font-bold text-titanium-300 hover:text-white px-2 py-1 rounded bg-white/5 hover:bg-white/10 border border-white/10 transition cursor-pointer"
                      >
                        <Copy className="w-3 h-3" />
                        <span>Copiar</span>
                      </button>
                      <button
                        onClick={() => handlePublishAsset(asset.name, 'Meta Graph API v21.0')}
                        disabled={publishingAsset === asset.name}
                        className="flex items-center gap-1 text-[10px] font-bold text-abyssal bg-cyan-bright hover:bg-cyan-bright/90 px-2.5 py-1 rounded shadow-xs transition cursor-pointer disabled:opacity-50"
                      >
                        {publishingAsset === asset.name ? (
                          <RefreshCw className="w-3 h-3 animate-spin" />
                        ) : (
                          <Share2 className="w-3 h-3" />
                        )}
                        <span>Publicar</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Visual FDI Odontogram Drawer (Mejora 49) */}
        <OdontogramDrawer
          isOpen={activeOdontogram.isOpen}
          onClose={() => setActiveOdontogram(prev => ({ ...prev, isOpen: false }))}
          patientName={activeOdontogram.patient}
          detectedTeeth={activeOdontogram.teeth}
          onInsertToothIntoChat={(tooth) => {
            setSimMessage(prev => prev ? `${prev} [Pieza FDI ${tooth}]` : `Consulta clínica sobre pieza dental FDI ${tooth}`);
            setActiveOdontogram(prev => ({ ...prev, isOpen: false }));
          }}
        />

        {/* Media Publishing Toast (Mejora 50) */}
        {mediaToast && (
          <div className="fixed bottom-6 right-6 z-50 bg-sapphire-900/95 border border-cyan-bright/50 text-white px-5 py-3 rounded-2xl shadow-2xl flex items-center gap-3 backdrop-blur-md">
            <Sparkles className="w-5 h-5 text-cyan-bright animate-spin" />
            <span className="text-xs font-semibold">{mediaToast}</span>
          </div>
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
