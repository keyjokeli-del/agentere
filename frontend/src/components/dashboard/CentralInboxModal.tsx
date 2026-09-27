'use client';

import React, { useState, useMemo } from 'react';
import {
  X,
  Search,
  Send,
  Sparkles,
  Volume2,
  Image as ImageIcon,
  CheckCheck,
  Check,
  Trash2,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  BrainCircuit,
  Lock,
  MapPin,
  FileText,
  Clock,
  AlertTriangle,
  Smile,
  ShieldAlert,
  Zap,
  PhoneCall,
  UserCheck,
  Copy
} from 'lucide-react';
import { ChannelInboxData, ChannelInboxThread, ChannelInboxMessage } from '@/types';

interface CentralInboxModalProps {
  isOpen: boolean;
  onClose: () => void;
  channelKey: string | null;
  channelsInbox: Record<string, ChannelInboxData>;
  backendUrl: string;
  getAuthHeaders: (extra?: Record<string, string>) => Record<string, string>;
  onRefreshData: () => Promise<void>;
  onOpenOdontogram?: (patientName: string, teeth: string[]) => void;
  onCloneToSimulator?: (sender: string, channel: string, message: string) => void;
}

const SHORTCUT_TEMPLATES = [
  {
    title: '📍 Ubicación y Cómo Llegar',
    text: '📍 Estamos ubicados en Av. Libertador 1234, CABA (entre Calles Sol y Luna). Contamos con estacionamiento propio para pacientes. Ver en Google Maps: https://maps.google.com/?q=Lumina+Dental+Studio'
  },
  {
    title: '💳 Seña y Medios de Pago',
    text: '💳 Para confirmar tu turno reservado solicitamos una seña de $15 USD o equivalente en pesos. Alias CBU: lumina.dental.studio | Enviar comprobante por aquí.'
  },
  {
    title: '🦷 Indicaciones Pre-Quirúrgicas',
    text: '🦷 Indicaciones preoperatorias: Venir con ropa cómoda, haber desayunado/almorzado ligero 2 horas antes y traer estudios radiográficos previos si dispone de ellos.'
  },
  {
    title: '✨ Cuidados Post-Blanqueamiento',
    text: '✨ Cuidados Post-Blanqueamiento: Mantener "dieta blanca" estricta por 48 horas (evitar café, té, mate, vino tinto y salsas oscuras). Si presenta sensibilidad, use la pasta desensibilizante indicada.'
  }
];

export const CentralInboxModal: React.FC<CentralInboxModalProps> = ({
  isOpen,
  onClose,
  channelKey,
  channelsInbox,
  backendUrl,
  getAuthHeaders,
  onRefreshData,
  onOpenOdontogram,
  onCloneToSimulator
}) => {
  const [selectedThreadId, setSelectedThreadId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [filterPill, setFilterPill] = useState<'all' | 'unread' | 'urgency' | 'paused'>('all');
  const [replyText, setReplyText] = useState<string>('');
  const [isInternalMode, setIsInternalMode] = useState<boolean>(false);
  const [replyTone, setReplyTone] = useState<'clinical' | 'empathic' | 'social'>('empathic');
  const [isSending, setIsSending] = useState<boolean>(false);
  const [showShortcuts, setShowShortcuts] = useState<boolean>(false);
  const [expandedRagId, setExpandedRagId] = useState<string | null>(null);
  const [trainRagModal, setTrainRagModal] = useState<{ isOpen: boolean; query: string; solution: string } | null>(null);
  const [lightboxImage, setLightboxImage] = useState<string | null>(null);
  const [audioSpeed, setAudioSpeed] = useState<number>(1);
  const [isPlayingAudio, setIsPlayingAudio] = useState<string | null>(null);
  const [translations, setTranslations] = useState<Record<string, boolean>>({});

  // 1. Compile threads: If channelKey is 'unified', combine all channels
  const allThreads = useMemo(() => {
    if (!channelKey || channelKey === 'unified') {
      const combined: ChannelInboxThread[] = [];
      Object.values(channelsInbox).forEach((chData) => {
        if (chData?.threads) {
          combined.push(...chData.threads);
        }
      });
      combined.sort((a, b) => new Date(b.last_activity).getTime() - new Date(a.last_activity).getTime());
      return combined;
    }
    return channelsInbox[channelKey]?.threads || [];
  }, [channelKey, channelsInbox]);

  // 2. Filter threads
  const filteredThreads = useMemo(() => {
    return allThreads.filter((t) => {
      // Search query
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const matchesName = t.patient_name?.toLowerCase().includes(q);
        const matchesId = t.sender_id?.toLowerCase().includes(q);
        const matchesMsg = t.messages?.some((m) => m.content?.toLowerCase().includes(q));
        if (!matchesName && !matchesId && !matchesMsg) return false;
      }
      // Filter pills
      if (filterPill === 'unread' && (!t.unread_count || t.unread_count === 0)) return false;
      if (filterPill === 'urgency' && t.urgency !== 'high') return false;
      if (filterPill === 'paused' && !t.is_ai_paused) return false;

      return true;
    });
  }, [allThreads, searchQuery, filterPill]);

  // Active selected thread
  const activeThread = useMemo(() => {
    if (selectedThreadId) {
      return allThreads.find((t) => t.sender_id === selectedThreadId) || filteredThreads[0] || null;
    }
    return filteredThreads[0] || null;
  }, [selectedThreadId, allThreads, filteredThreads]);

  if (!isOpen) return null;

  // Handle send message (manual reply or internal note)
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!replyText.trim() || !activeThread) return;

    setIsSending(true);
    try {
      const endpoint = isInternalMode ? '/api/dashboard/internal-note' : '/api/dashboard/reply';
      const payload = isInternalMode
        ? {
            sender_id: activeThread.sender_id,
            channel: activeThread.channel,
            note: replyText.trim(),
            author: 'Equipo Clínico / Recepción'
          }
        : {
            sender_id: activeThread.sender_id,
            channel: activeThread.channel,
            message: replyText.trim(),
            sender_name: activeThread.patient_name
          };

      const res = await fetch(`${backendUrl}${endpoint}`, {
        method: 'POST',
        headers: getAuthHeaders(),
        credentials: 'include',
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        setReplyText('');
        await onRefreshData();
      }
    } catch (err) {
      console.error('[CentralInboxModal] Send error:', err);
    } finally {
      setIsSending(false);
    }
  };

  // Handle Train RAG
  const handleTrainRagSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!trainRagModal) return;

    try {
      const res = await fetch(`${backendUrl}/api/dashboard/train-rag`, {
        method: 'POST',
        headers: getAuthHeaders(),
        credentials: 'include',
        body: JSON.stringify({
          query: trainRagModal.query,
          corrected_solution: trainRagModal.solution,
          category: 'Entrenamiento Dashboard Clínico'
        })
      });
      if (res.ok) {
        setTrainRagModal(null);
        await onRefreshData();
      }
    } catch (err) {
      console.error('[TrainRag] Error:', err);
    }
  };

  // Handle Purge Patient Data (GDPR / HIPAA)
  const handlePurgePatient = async () => {
    if (!activeThread) return;
    const confirmPurge = window.confirm(
      `⚠️ ATENCIÓN CLÍNICA (RGPD/HIPAA):\n¿Deseas purgar de forma permanente todos los mensajes, audios y vectores del paciente ${activeThread.patient_name} (${activeThread.sender_id})? Esta acción no se puede deshacer.`
    );
    if (!confirmPurge) return;

    try {
      const res = await fetch(`${backendUrl}/api/patient/purge/${encodeURIComponent(activeThread.sender_id)}`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
        credentials: 'include'
      });
      if (res.ok) {
        setSelectedThreadId(null);
        await onRefreshData();
      }
    } catch (err) {
      console.error('[Purge] Error:', err);
    }
  };

  // Follow-up generator
  const handleRescuePatient = () => {
    if (!activeThread) return;
    const rescueText = `👋 Hola ${activeThread.patient_name}, ¿cómo estás? Te escribimos de Lumina Dental Studio para saber si pudiste evaluar el presupuesto y si te quedó alguna duda. Esta semana tenemos un beneficio especial de bonificación en tu diagnóstico 3D si agendas antes del viernes. ¿Te reservamos un lugar?`;
    setReplyText(rescueText);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="w-full max-w-[1400px] h-[90vh] glass-panel rounded-3xl border border-cyan-bright/40 bg-sapphire-950/95 shadow-2xl flex flex-col overflow-hidden relative">
        {/* Header */}
        <div className="p-4 sm:px-6 border-b border-white/10 flex items-center justify-between gap-4 bg-sapphire-900/50 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-bright/20 text-cyan-bright flex items-center justify-center border border-cyan-bright/40 shadow-cyan-glow">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-extrabold text-white tracking-tight">
                  {channelKey === 'unified' ? '🌐 Bandeja de Entrada Unificada (Omnicanal)' : `Bandeja de Entrada: ${(channelKey || 'WHATSAPP').toUpperCase()}`}
                </h2>
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-cyan-bright/15 text-cyan-bright border border-cyan-bright/30">
                  {filteredThreads.length} hilos
                </span>
                <span className="text-[10px] font-mono text-emerald-400 font-semibold hidden sm:inline">
                  ⚡ Neon PGVector AES-256
                </span>
              </div>
              <p className="text-xs text-titanium-400">
                Intervención manual en vivo • Pausa de IA por 30m • Trazabilidad RAG completa
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-white/10 hover:bg-white/20 text-titanium-300 hover:text-white transition cursor-pointer border border-white/10"
              title="Cerrar Bandeja"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* 2-Column Body */}
        <div className="flex-1 flex overflow-hidden">
          {/* Left Column: Thread List */}
          <div className="w-80 sm:w-96 border-r border-white/10 flex flex-col bg-abyssal/60 shrink-0">
            {/* Search & Pills */}
            <div className="p-3 border-b border-white/10 space-y-2">
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-titanium-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Buscar paciente, teléfono, síntoma..."
                  className="w-full text-xs pl-8 pr-3 py-2 rounded-xl bg-sapphire-900/60 border border-white/10 text-white placeholder-titanium-400 focus:outline-none focus:border-cyan-bright"
                />
              </div>

              {/* Filter Pills */}
              <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-[10px] font-semibold custom-scrollbar">
                <button
                  onClick={() => setFilterPill('all')}
                  className={`px-2.5 py-1 rounded-lg transition cursor-pointer shrink-0 ${
                    filterPill === 'all' ? 'bg-cyan-bright text-abyssal font-bold' : 'bg-white/5 text-titanium-300 hover:bg-white/10'
                  }`}
                >
                  Todos ({allThreads.length})
                </button>
                <button
                  onClick={() => setFilterPill('unread')}
                  className={`px-2.5 py-1 rounded-lg transition cursor-pointer shrink-0 ${
                    filterPill === 'unread' ? 'bg-cyan-bright text-abyssal font-bold' : 'bg-white/5 text-titanium-300 hover:bg-white/10'
                  }`}
                >
                  Sin Leer
                </button>
                <button
                  onClick={() => setFilterPill('urgency')}
                  className={`px-2.5 py-1 rounded-lg transition cursor-pointer shrink-0 ${
                    filterPill === 'urgency' ? 'bg-rose-500 text-white font-bold' : 'bg-white/5 text-rose-300 hover:bg-white/10'
                  }`}
                >
                  🚨 Urgencias
                </button>
                <button
                  onClick={() => setFilterPill('paused')}
                  className={`px-2.5 py-1 rounded-lg transition cursor-pointer shrink-0 ${
                    filterPill === 'paused' ? 'bg-amber-500 text-abyssal font-bold' : 'bg-white/5 text-amber-300 hover:bg-white/10'
                  }`}
                >
                  ⏸️ IA Pausada
                </button>
              </div>
            </div>

            {/* Threads scrollable list */}
            <div className="flex-1 overflow-y-auto divide-y divide-white/5 custom-scrollbar">
              {filteredThreads.length > 0 ? (
                filteredThreads.map((t) => {
                  const isSelected = activeThread?.sender_id === t.sender_id;
                  const lastMsg = t.messages && t.messages.length > 0 ? t.messages[t.messages.length - 1] : null;

                  return (
                    <div
                      key={t.sender_id}
                      onClick={() => setSelectedThreadId(t.sender_id)}
                      className={`p-3.5 transition cursor-pointer flex flex-col gap-1.5 relative ${
                        isSelected ? 'bg-sapphire-900/80 border-l-4 border-l-cyan-bright' : 'hover:bg-white/[0.03]'
                      } ${t.urgency === 'high' ? 'ring-1 ring-rose-500/40' : ''}`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2 min-w-0">
                          <div className="w-7 h-7 rounded-full bg-cyan-bright/20 text-cyan-bright font-bold flex items-center justify-center text-xs shrink-0">
                            {t.patient_name ? t.patient_name.charAt(0).toUpperCase() : 'P'}
                          </div>
                          <span className="font-bold text-xs text-white truncate">{t.patient_name}</span>
                        </div>
                        <span className="text-[10px] font-mono text-titanium-400 shrink-0">
                          {t.last_activity ? new Date(t.last_activity).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                        </span>
                      </div>

                      {/* Snippet */}
                      <p className="text-[11px] text-titanium-300 line-clamp-1 italic">
                        {lastMsg ? lastMsg.content : 'Sin mensajes'}
                      </p>

                      {/* Badges strip */}
                      <div className="flex flex-wrap items-center gap-1.5 mt-1">
                        {/* Channel Badge */}
                        <span className="text-[9px] font-mono font-bold uppercase px-1.5 py-0.5 rounded bg-white/10 text-titanium-300">
                          {t.channel}
                        </span>

                        {/* Urgency */}
                        {t.urgency === 'high' && (
                          <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40 animate-pulse">
                            🚨 Urgencia
                          </span>
                        )}

                        {/* CRM stage */}
                        {t.crm_stage && (
                          <span className="text-[9px] font-medium px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                            {t.crm_stage}
                          </span>
                        )}

                        {/* FDI Teeth */}
                        {t.fdi_teeth && t.fdi_teeth.length > 0 && (
                          <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                            🦷 FDI {t.fdi_teeth.join(', ')}
                          </span>
                        )}

                        {/* Cross channel badges */}
                        {t.cross_channels && t.cross_channels.length > 1 && (
                          <span className="text-[9px] font-mono px-1 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">
                            {t.cross_channels.map((c) => c.substring(0, 2).toUpperCase()).join('+')}
                          </span>
                        )}

                        {/* Paused */}
                        {t.is_ai_paused && (
                          <span className="text-[9px] font-bold px-1 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40">
                            ⏸️ IA Pausada
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="p-8 text-center text-titanium-400 text-xs">
                  No se encontraron conversaciones con los filtros aplicados.
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Active Conversation */}
          {activeThread ? (
            <div className="flex-1 flex flex-col bg-abyssal/90 overflow-hidden">
              {/* Chat Header */}
              <div className="p-3 sm:px-6 border-b border-white/10 flex flex-wrap items-center justify-between gap-3 bg-sapphire-900/40 shrink-0">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full bg-cyan-bright/20 text-cyan-bright font-extrabold flex items-center justify-center text-sm border border-cyan-bright/40">
                    {activeThread.patient_name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-extrabold text-sm text-white">{activeThread.patient_name}</h3>
                      <span className="text-[11px] font-mono text-cyan-bright">({activeThread.sender_id})</span>
                      {activeThread.is_ai_paused && (
                        <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                          ⏸️ IA Pausada (30m)
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-3 text-[11px] text-titanium-400 mt-0.5">
                      <span>Canal: <strong className="text-white uppercase">{activeThread.channel}</strong></span>
                      <span>•</span>
                      <span>Etapa: <strong className="text-cyan-300">{activeThread.crm_stage || 'Consulta'}</strong></span>
                      {activeThread.fdi_teeth && activeThread.fdi_teeth.length > 0 && (
                        <>
                          <span>•</span>
                          <span className="text-rose-300 font-mono">Piezas FDI: {activeThread.fdi_teeth.join(', ')}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                {/* Top Action Buttons */}
                <div className="flex flex-wrap items-center gap-1.5 text-xs font-semibold">
                  {/* Pasar a WhatsApp */}
                  {activeThread.channel !== 'whatsapp' && (
                    <a
                      href={`https://wa.me/?text=${encodeURIComponent(`Hola ${activeThread.patient_name}, te contactamos desde Lumina Dental Studio en seguimiento a tu consulta.`)}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-2.5 py-1 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 flex items-center gap-1 transition"
                    >
                      <PhoneCall className="w-3 h-3" />
                      <span>Pasar a WA</span>
                    </a>
                  )}

                  {/* Odontograma */}
                  <button
                    onClick={() => onOpenOdontogram?.(activeThread.patient_name, activeThread.fdi_teeth || [])}
                    className="px-2.5 py-1 rounded-xl bg-cyan-bright/15 hover:bg-cyan-bright/25 text-cyan-bright border border-cyan-bright/30 flex items-center gap-1 transition cursor-pointer"
                  >
                    <span>🦷 Odontograma FDI</span>
                  </button>

                  {/* Clonar al Simulador */}
                  {onCloneToSimulator && (
                    <button
                      onClick={() => {
                        const lastMsg = activeThread.messages[activeThread.messages.length - 1]?.content || '';
                        onCloneToSimulator(activeThread.patient_name, activeThread.channel, lastMsg);
                        onClose();
                      }}
                      className="px-2.5 py-1 rounded-xl bg-teal-500/20 hover:bg-teal-500/30 text-teal-300 border border-teal-500/40 flex items-center gap-1 transition cursor-pointer"
                      title="Clonar este paciente y mensaje al simulador clínico"
                    >
                      <Copy className="w-3 h-3" />
                      <span>Clonar a Sim</span>
                    </button>
                  )}

                  {/* Rescatar Indeciso */}
                  <button
                    onClick={handleRescuePatient}
                    className="px-2.5 py-1 rounded-xl bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/40 flex items-center gap-1 transition cursor-pointer"
                    title="Generar mensaje de seguimiento personalizado"
                  >
                    <Sparkles className="w-3 h-3" />
                    <span>Rescatar</span>
                  </button>

                  {/* Purgar GDPR */}
                  <button
                    onClick={handlePurgePatient}
                    className="p-1.5 rounded-xl text-rose-400 hover:bg-rose-950/50 border border-rose-500/30 transition cursor-pointer"
                    title="Purgar datos (RGPD / HIPAA)"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Patient Long-term memory banner */}
              {activeThread.patient_memory && (
                <div className="p-2.5 px-4 bg-purple-950/40 border-b border-purple-500/20 flex items-center gap-2 text-xs text-purple-200 shrink-0">
                  <BrainCircuit className="w-4 h-4 text-purple-400 shrink-0" />
                  <span className="font-semibold text-purple-300 shrink-0">Memoria Clínica RAG:</span>
                  <p className="truncate text-[11px] text-purple-100">{activeThread.patient_memory}</p>
                </div>
              )}

              {/* Chat Message Scroll */}
              <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 custom-scrollbar">
                {activeThread.messages.map((m, mIdx) => {
                  const isUser = m.role === 'user';
                  const isInternal = m.is_internal || m.status === 'internal' || m.agent === 'InternalNote';

                  return (
                    <div
                      key={m.id || mIdx}
                      className={`flex flex-col ${isUser ? 'items-start' : 'items-end'}`}
                    >
                      <div
                        className={`max-w-[85%] rounded-2xl p-3.5 text-xs leading-relaxed relative ${
                          isInternal
                            ? 'bg-amber-950/80 border border-amber-500/50 text-amber-100 shadow-lg shadow-amber-500/10'
                            : isUser
                            ? 'bg-sapphire-900/80 border border-sapphire-700/60 text-slate-100 rounded-tl-sm'
                            : 'bg-cyan-950/70 border border-cyan-bright/40 text-cyan-50 shadow-cyan-glow/10 rounded-tr-sm'
                        }`}
                      >
                        {/* Message Header */}
                        <div className="flex items-center justify-between gap-4 mb-1.5 text-[10px] font-bold">
                          <span className={isInternal ? 'text-amber-400' : isUser ? 'text-cyan-300' : 'text-emerald-400'}>
                            {isInternal
                              ? '📝 NOTA INTERNA DEL EQUIPO'
                              : isUser
                              ? `👤 ${m.sender_name || 'Paciente'}`
                              : `🤖 ${m.agent || 'SolverAgent'}`}
                          </span>

                          <div className="flex items-center gap-2">
                            {/* RAG cognitive trace toggle */}
                            {!isUser && !isInternal && m.rag_trace && m.rag_trace.length > 0 && (
                              <button
                                onClick={() => setExpandedRagId((prev) => (prev === m.id ? null : m.id))}
                                className="text-[9px] font-mono text-cyan-bright hover:underline flex items-center gap-0.5 cursor-pointer"
                              >
                                <BrainCircuit className="w-2.5 h-2.5" />
                                RAG Trace ({m.rag_trace.length})
                                {expandedRagId === m.id ? <ChevronUp className="w-2.5 h-2.5" /> : <ChevronDown className="w-2.5 h-2.5" />}
                              </button>
                            )}

                            {/* Train RAG button */}
                            {!isUser && !isInternal && (
                              <button
                                onClick={() =>
                                  setTrainRagModal({
                                    isOpen: true,
                                    query: 'Consulta previa del paciente',
                                    solution: m.content
                                  })
                                }
                                className="text-[9px] text-amber-300 hover:text-amber-200 border border-amber-500/30 px-1.5 py-0.5 rounded transition cursor-pointer"
                                title="Corregir y entrenar memoria RAG con esta respuesta"
                              >
                                ✏️ Entrenar
                              </button>
                            )}

                            {/* Translation toggle */}
                            <button
                              onClick={() => setTranslations((prev) => ({ ...prev, [m.id]: !prev[m.id] }))}
                              className="text-[9px] text-titanium-400 hover:text-white cursor-pointer"
                              title="Alternar traducción"
                            >
                              🌐
                            </button>
                          </div>
                        </div>

                        {/* RAG trace dropdown */}
                        {expandedRagId === m.id && m.rag_trace && (
                          <div className="mb-2 p-2 rounded-xl bg-black/40 border border-cyan-bright/30 text-[10px] text-cyan-200 font-mono animate-fadeIn">
                            <span className="font-bold text-cyan-bright">Fuentes Clínicas RAG Consultadas:</span>
                            <ul className="list-disc list-inside mt-0.5">
                              {m.rag_trace.map((src, sIdx) => (
                                <li key={sIdx}>{src}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Text Content */}
                        <p className="whitespace-pre-wrap">{m.content}</p>

                        {/* Inline Voice Note Player */}
                        {m.audio_url && (
                          <div className="mt-2.5 p-2 rounded-xl bg-black/50 border border-white/10 flex items-center justify-between gap-2">
                            <div className="flex items-center gap-2 text-cyan-bright">
                              <Volume2 className="w-4 h-4 animate-pulse" />
                              <span className="text-[11px] font-mono">Nota de Voz Paciente</span>
                            </div>
                            <div className="flex items-center gap-1">
                              {[1, 1.5, 2].map((spd) => (
                                <button
                                  key={spd}
                                  onClick={() => setAudioSpeed(spd)}
                                  className={`px-1.5 py-0.5 rounded text-[9px] font-mono font-bold ${
                                    audioSpeed === spd ? 'bg-cyan-bright text-abyssal' : 'bg-white/10 text-titanium-300'
                                  }`}
                                >
                                  {spd}x
                                </button>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Clinical Photo Preview & Lightbox trigger */}
                        {m.image_url && (
                          <div className="mt-2.5 space-y-1.5">
                            <div
                              onClick={() => setLightboxImage(m.image_url || null)}
                              className="relative h-36 rounded-xl overflow-hidden border border-cyan-bright/40 cursor-pointer group"
                            >
                              <img
                                src={m.image_url}
                                alt="Foto Clínica"
                                className="w-full h-full object-cover group-hover:scale-105 transition duration-200"
                              />
                              <div className="absolute inset-0 bg-black/30 flex items-center justify-center opacity-0 group-hover:opacity-100 transition">
                                <span className="text-xs font-bold text-white bg-black/60 px-2 py-1 rounded-lg">
                                  🔍 Ampliar Foto
                                </span>
                              </div>
                            </div>
                            {m.vision_analysis && (
                              <div className="p-2 rounded-lg bg-cyan-950/80 border border-cyan-bright/30 text-[10px] text-cyan-200">
                                <span className="font-bold text-cyan-bright">🔬 Gemini Vision:</span> {m.vision_analysis}
                              </div>
                            )}
                          </div>
                        )}

                        {/* Footer status & timestamp */}
                        <div className="mt-2 flex items-center justify-end gap-1.5 text-[9px] text-titanium-400 font-mono">
                          <span>{new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} hs</span>
                          <CheckCheck className="w-3 h-3 text-cyan-bright" />
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Bottom Reply Bar */}
              <div className="p-3 sm:p-4 border-t border-white/10 bg-sapphire-900/60 shrink-0 space-y-2">
                {/* Tone and Mode Selector Strip */}
                <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                  <div className="flex items-center gap-1 bg-black/40 p-1 rounded-xl border border-white/10">
                    <button
                      onClick={() => setIsInternalMode(false)}
                      className={`px-2.5 py-1 rounded-lg transition cursor-pointer font-bold ${
                        !isInternalMode ? 'bg-cyan-bright text-abyssal' : 'text-titanium-400 hover:text-white'
                      }`}
                    >
                      💬 Mensaje Paciente
                    </button>
                    <button
                      onClick={() => setIsInternalMode(true)}
                      className={`px-2.5 py-1 rounded-lg transition cursor-pointer font-bold ${
                        isInternalMode ? 'bg-amber-500 text-abyssal' : 'text-titanium-400 hover:text-white'
                      }`}
                    >
                      📝 Nota Interna
                    </button>
                  </div>

                  {/* Quick Shortcut Buttons */}
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => setShowShortcuts((prev) => !prev)}
                      className="px-2.5 py-1 rounded-xl bg-cyan-bright/15 text-cyan-bright border border-cyan-bright/30 hover:bg-cyan-bright/25 transition cursor-pointer font-bold flex items-center gap-1"
                    >
                      <span>⚡ /atajos</span>
                    </button>
                    <button
                      onClick={() =>
                        setReplyText(
                          '📍 Ubicación de la clínica: Av. Libertador 1234, CABA. Link en mapa: https://maps.google.com/?q=Lumina+Dental+Studio'
                        )
                      }
                      className="p-1.5 rounded-xl bg-white/5 text-titanium-300 hover:text-white hover:bg-white/10 transition cursor-pointer"
                      title="Insertar Ubicación GPS"
                    >
                      <MapPin className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                {/* Shortcuts Popover */}
                {showShortcuts && (
                  <div className="p-3 rounded-2xl bg-sapphire-950 border border-cyan-bright/40 shadow-xl grid grid-cols-1 sm:grid-cols-2 gap-2 animate-fadeIn text-xs">
                    {SHORTCUT_TEMPLATES.map((tmpl, idx) => (
                      <button
                        key={idx}
                        onClick={() => {
                          setReplyText(tmpl.text);
                          setShowShortcuts(false);
                        }}
                        className="p-2 rounded-xl bg-black/40 hover:bg-cyan-bright/20 border border-white/10 text-left transition cursor-pointer"
                      >
                        <span className="font-bold text-white block">{tmpl.title}</span>
                        <span className="text-[11px] text-titanium-300 line-clamp-1">{tmpl.text}</span>
                      </button>
                    ))}
                  </div>
                )}

                {/* Textarea & Send Button */}
                <form onSubmit={handleSendMessage} className="flex gap-2">
                  <textarea
                    rows={2}
                    value={replyText}
                    onChange={(e) => setReplyText(e.target.value)}
                    placeholder={
                      isInternalMode
                        ? 'Escribe una nota interna para el equipo médico (invisible al paciente)...'
                        : 'Escribe un mensaje manual al paciente (pausará la IA por 30m)...'
                    }
                    className={`flex-1 text-xs p-3 rounded-2xl border resize-none focus:outline-none transition ${
                      isInternalMode
                        ? 'bg-amber-950/30 border-amber-500/50 text-amber-100 placeholder-amber-400/50 focus:border-amber-400'
                        : 'bg-black/50 border-white/15 text-white placeholder-titanium-400 focus:border-cyan-bright'
                    }`}
                  />
                  <button
                    type="submit"
                    disabled={isSending || !replyText.trim()}
                    className={`px-5 rounded-2xl font-bold text-xs flex items-center justify-center gap-2 transition cursor-pointer disabled:opacity-50 ${
                      isInternalMode
                        ? 'bg-amber-500 hover:bg-amber-400 text-abyssal shadow-lg shadow-amber-500/20'
                        : 'bg-cyan-bright hover:bg-cyan-bright/90 text-abyssal shadow-cyan-glow'
                    }`}
                  >
                    <Send className="w-4 h-4" />
                    <span className="hidden sm:inline">{isInternalMode ? 'Guardar Nota' : 'Enviar'}</span>
                  </button>
                </form>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center p-8 text-center text-titanium-400">
              Selecciona una conversación del panel izquierdo para ver los mensajes y responder.
            </div>
          )}
        </div>
      </div>

      {/* Lightbox Modal */}
      {lightboxImage && (
        <div
          onClick={() => setLightboxImage(null)}
          className="fixed inset-0 z-60 bg-black/90 flex items-center justify-center p-4 cursor-zoom-out animate-fadeIn"
        >
          <img src={lightboxImage} alt="Foto Ampliada" className="max-w-full max-h-[85vh] rounded-2xl border border-cyan-bright/40 shadow-2xl" />
        </div>
      )}

      {/* Train RAG Modal */}
      {trainRagModal && (
        <div className="fixed inset-0 z-60 bg-black/80 flex items-center justify-center p-4 animate-fadeIn">
          <div className="max-w-md w-full glass-panel rounded-3xl p-6 border border-amber-500/40 bg-sapphire-950 shadow-2xl space-y-4">
            <h3 className="font-extrabold text-sm text-white flex items-center gap-2">
              <span>✏️ Corregir y Entrenar IA (RAG)</span>
            </h3>
            <p className="text-xs text-titanium-300">
              Esta corrección se indexará en los vectores de Neon PostgreSQL para que los agentes futuros den la respuesta correcta.
            </p>
            <form onSubmit={handleTrainRagSubmit} className="space-y-3">
              <div>
                <label className="block text-[11px] font-bold text-titanium-300 mb-1">Consulta Clínica o Pregunta</label>
                <input
                  type="text"
                  value={trainRagModal.query}
                  onChange={(e) => setTrainRagModal({ ...trainRagModal, query: e.target.value })}
                  className="w-full text-xs p-2.5 rounded-xl bg-black/50 border border-white/15 text-white"
                />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-titanium-300 mb-1">Solución Clínica Verificada</label>
                <textarea
                  rows={3}
                  value={trainRagModal.solution}
                  onChange={(e) => setTrainRagModal({ ...trainRagModal, solution: e.target.value })}
                  className="w-full text-xs p-2.5 rounded-xl bg-black/50 border border-white/15 text-white"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setTrainRagModal(null)}
                  className="px-3 py-1.5 rounded-xl bg-white/10 text-white text-xs font-bold"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-xl bg-amber-500 hover:bg-amber-400 text-abyssal text-xs font-bold"
                >
                  Entrenar Modelo
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
