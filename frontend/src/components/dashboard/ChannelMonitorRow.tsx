'use client';

import React, { useState, useEffect } from 'react';
import {
  Smartphone,
  MessageSquare,
  QrCode,
  LogOut,
  RefreshCw,
  ExternalLink,
  ShieldCheck,
  Zap,
  Globe,
  Send,
  Clock,
  AlertTriangle
} from 'lucide-react';
import { ChannelInboxData, WhatsAppStatus } from '@/types';

const FacebookIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
  </svg>
);

const InstagramIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
  </svg>
);

const YoutubeIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24">
    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
  </svg>
);

interface ChannelMonitorRowProps {
  channelsInbox: Record<string, ChannelInboxData>;
  waData: WhatsAppStatus;
  onOpenInbox: (channel: string) => void;
  onOpenQrModal: () => void;
  onDisconnectWA: () => void;
  isDisconnectingWA: boolean;
  onSyncYouTube: (e?: React.MouseEvent) => void;
  isSyncingYouTube: boolean;
  syncMessage: string | null;
  backendUrl: string;
  getAuthHeaders: (extra?: Record<string, string>) => Record<string, string>;
}

export const ChannelMonitorRow: React.FC<ChannelMonitorRowProps> = ({
  channelsInbox,
  waData,
  onOpenInbox,
  onOpenQrModal,
  onDisconnectWA,
  isDisconnectingWA,
  onSyncYouTube,
  isSyncingYouTube,
  syncMessage,
  backendUrl,
  getAuthHeaders
}) => {
  // YouTube 10-min SLA timer countdown simulation (Mejora 17)
  const [ytCountdown, setYtCountdown] = useState<number>(542);
  // Meta token check state (Mejora 21)
  const [metaTokenChecked, setMetaTokenChecked] = useState<boolean>(false);
  const [isCheckingToken, setIsCheckingToken] = useState<boolean>(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setYtCountdown((prev) => (prev > 0 ? prev - 1 : 600));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatCountdown = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const handleCheckMetaTokens = async () => {
    setIsCheckingToken(true);
    try {
      const res = await fetch(`${backendUrl}/api/dashboard/meta-token-health`, {
        headers: getAuthHeaders(),
        credentials: 'include'
      });
      if (res.ok) {
        setMetaTokenChecked(true);
        setTimeout(() => setMetaTokenChecked(false), 5000);
      }
    } catch {
      // ignore
    } finally {
      setIsCheckingToken(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Top Header of Monitor */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-extrabold text-white tracking-tight flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-cyan-bright" />
            <span>Monitor Omnicanal & Tiempos de Respuesta</span>
          </h2>
          <p className="text-xs text-titanium-400">
            Conectores activos de WhatsApp, Meta, YouTube, Telegram y Web sin costo mensual
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* SLA Meter (Mejora 19) */}
          <span className="text-xs font-mono font-bold text-cyan-bright bg-cyan-bright/10 px-3 py-1 rounded-xl border border-cyan-bright/30 flex items-center gap-1.5 shadow-cyan-glow/10">
            <Zap className="w-3.5 h-3.5" />
            <span>SLA: 1.1s</span>
          </span>

          {/* Meta Token Ping Button (Mejora 21) */}
          <button
            onClick={handleCheckMetaTokens}
            disabled={isCheckingToken}
            className={`px-3 py-1 rounded-xl text-xs font-bold border transition flex items-center gap-1.5 cursor-pointer ${
              metaTokenChecked
                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                : 'bg-white/5 hover:bg-white/10 text-titanium-300 border-white/10'
            }`}
            title="Comprobar salud de tokens de Meta Graph API v21.0"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-cyan-bright" />
            <span>{metaTokenChecked ? 'Tokens Verificados ✓' : 'Ping Tokens Meta'}</span>
          </button>

          {/* Unified Inbox Button (Mejora 14) */}
          <button
            onClick={() => onOpenInbox('unified')}
            className="px-3.5 py-1 rounded-xl text-xs font-bold bg-cyan-bright hover:bg-cyan-bright/90 text-abyssal shadow-cyan-glow transition cursor-pointer flex items-center gap-1.5"
          >
            <Globe className="w-3.5 h-3.5" />
            <span>🌐 Bandeja Unificada</span>
          </button>
        </div>
      </div>

      {/* 4 Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 1. WhatsApp Card */}
        <div
          onClick={() => onOpenInbox('whatsapp')}
          className="glass-card rounded-2xl p-5 border border-cyan-bright/20 hover:border-emerald-400/50 shadow-xl flex flex-col justify-between relative overflow-hidden cursor-pointer transition-all duration-200 hover:bg-white/[0.02]"
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-950/80 text-emerald-400 flex items-center justify-center border border-emerald-500/30">
                <Smartphone className="w-5 h-5" />
              </div>
              <div className="flex items-center gap-1.5">
                {/* Unread count pulse badge (Mejora 13) */}
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-bright/15 text-cyan-bright border border-cyan-bright/40 shadow-cyan-glow flex items-center gap-1">
                  <MessageSquare className="w-2.5 h-2.5" />
                  {channelsInbox.whatsapp?.total_messages || 0} msgs
                </span>
                <span
                  className={`px-2 py-0.5 rounded-full text-[10px] font-bold inline-flex items-center gap-1 ${
                    waData.status === 'connected'
                      ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/30'
                      : waData.status === 'waiting_for_scan'
                      ? 'bg-amber-950 text-amber-300 border border-amber-500/30'
                      : 'bg-slate-900 text-slate-400 border border-slate-700'
                  }`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      waData.status === 'connected'
                        ? 'bg-emerald-400 animate-pulse'
                        : waData.status === 'waiting_for_scan'
                        ? 'bg-amber-400 animate-bounce'
                        : 'bg-slate-500'
                    }`}
                  />
                  {waData.status === 'connected'
                    ? 'Conectado'
                    : waData.status === 'waiting_for_scan'
                    ? 'QR'
                    : 'Offline'}
                </span>
              </div>
            </div>

            <h3 className="font-bold text-white text-sm">WhatsApp (Baileys Bridge)</h3>
            <p className="text-xs text-titanium-400 mt-1">Conexión WebSocket directa y persistencia en Neon Postgres.</p>

            {/* Preview Box */}
            <div className="mt-3 p-2.5 rounded-xl bg-black/40 border border-white/10 text-left">
              {channelsInbox.whatsapp?.last_message ? (
                <>
                  <div className="flex items-center justify-between text-[10px] text-titanium-400 mb-1">
                    <span className="font-semibold text-white truncate max-w-[120px]">
                      {channelsInbox.whatsapp.last_message.patient_name || channelsInbox.whatsapp.last_message.sender_id}
                    </span>
                    <span className="text-[9px] font-mono text-cyan-bright/80">
                      {new Date(channelsInbox.whatsapp.last_message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} hs
                    </span>
                  </div>
                  <p className="text-[11px] text-titanium-200 line-clamp-2 italic">
                    "{channelsInbox.whatsapp.last_message.content}"
                  </p>
                </>
              ) : (
                <p className="text-[11px] text-titanium-400 italic">Sin mensajes registrados aún en Neon</p>
              )}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-white/10 flex items-center gap-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onOpenInbox('whatsapp');
              }}
              className="flex-1 flex items-center justify-center gap-1.5 py-1.5 px-2.5 text-xs font-bold bg-cyan-bright/20 hover:bg-cyan-bright/30 text-cyan-bright border border-cyan-bright/40 rounded-xl transition cursor-pointer"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Ver Hilos ({channelsInbox.whatsapp?.active_threads || 0})</span>
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onOpenQrModal();
              }}
              className="p-1.5 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 rounded-xl transition cursor-pointer"
              title="Ver Conexión / QR"
            >
              <QrCode className="w-4 h-4" />
            </button>
            {waData.status === 'connected' && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDisconnectWA();
                }}
                disabled={isDisconnectingWA}
                className="p-1.5 text-rose-400 hover:bg-rose-950/50 rounded-xl transition border border-rose-500/30 cursor-pointer"
                title="Cerrar sesión de WhatsApp"
              >
                <LogOut className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* 2. Facebook Messenger Card */}
        <div
          onClick={() => onOpenInbox('facebook')}
          className="glass-card rounded-2xl p-5 border border-cyan-bright/20 hover:border-blue-400/50 shadow-xl flex flex-col justify-between relative overflow-hidden cursor-pointer transition-all duration-200 hover:bg-white/[0.02]"
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-xl bg-blue-950/80 text-blue-400 flex items-center justify-center border border-blue-500/30">
                <FacebookIcon className="w-5 h-5" />
              </div>
              <div className="flex items-center gap-1.5">
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-bright/15 text-cyan-bright border border-cyan-bright/40 shadow-cyan-glow flex items-center gap-1">
                  <MessageSquare className="w-2.5 h-2.5" />
                  {channelsInbox.facebook?.total_messages || 0} msgs
                </span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-950 text-blue-300 border border-blue-500/30 inline-flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" /> Webhook
                </span>
              </div>
            </div>

            <h3 className="font-bold text-white text-sm">Facebook Messenger</h3>
            <p className="text-xs text-titanium-400 mt-1">Recepción vía Webhook de Meta Developer y respuestas seguras.</p>

            {/* Preview Box */}
            <div className="mt-3 p-2.5 rounded-xl bg-black/40 border border-white/10 text-left">
              {channelsInbox.facebook?.last_message ? (
                <>
                  <div className="flex items-center justify-between text-[10px] text-titanium-400 mb-1">
                    <span className="font-semibold text-white truncate max-w-[120px]">
                      {channelsInbox.facebook.last_message.patient_name || channelsInbox.facebook.last_message.sender_id}
                    </span>
                    <span className="text-[9px] font-mono text-cyan-bright/80">
                      {new Date(channelsInbox.facebook.last_message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} hs
                    </span>
                  </div>
                  <p className="text-[11px] text-titanium-200 line-clamp-2 italic">
                    "{channelsInbox.facebook.last_message.content}"
                  </p>
                </>
              ) : (
                <p className="text-[11px] text-titanium-400 italic">Esperando interacciones de Messenger</p>
              )}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-white/10 flex items-center gap-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onOpenInbox('facebook');
              }}
              className="flex-1 flex items-center justify-center gap-1.5 py-1.5 px-2.5 text-xs font-bold bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 border border-blue-500/40 rounded-xl transition cursor-pointer"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Ver Hilos ({channelsInbox.facebook?.active_threads || 0})</span>
            </button>
          </div>
        </div>

        {/* 3. Instagram Direct Card (Mejora 15, 18) */}
        <div
          onClick={() => onOpenInbox('instagram')}
          className="glass-card rounded-2xl p-5 border border-cyan-bright/20 hover:border-pink-400/50 shadow-xl flex flex-col justify-between relative overflow-hidden cursor-pointer transition-all duration-200 hover:bg-white/[0.02]"
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-xl bg-pink-950/80 text-pink-400 flex items-center justify-center border border-pink-500/30">
                <InstagramIcon className="w-5 h-5" />
              </div>
              <div className="flex items-center gap-1.5">
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-bright/15 text-cyan-bright border border-cyan-bright/40 shadow-cyan-glow flex items-center gap-1">
                  <MessageSquare className="w-2.5 h-2.5" />
                  {channelsInbox.instagram?.total_messages || 0} msgs
                </span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-pink-950 text-pink-300 border border-pink-500/30 inline-flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-pink-400 animate-pulse" /> Graph API
                </span>
              </div>
            </div>

            <h3 className="font-bold text-white text-sm">Instagram Direct</h3>
            
            {/* Meta 24h Window Badge (Mejora 18) */}
            <div className="mt-1 flex items-center justify-between text-[11px] text-pink-300/80">
              <span>Ventana Gratuita Meta:</span>
              <span className="font-mono font-bold text-emerald-400">23h 48m</span>
            </div>

            {/* Preview Box & Post link (Mejora 15) */}
            <div className="mt-2.5 p-2.5 rounded-xl bg-black/40 border border-white/10 text-left">
              {channelsInbox.instagram?.last_message ? (
                <>
                  <div className="flex items-center justify-between text-[10px] text-titanium-400 mb-1">
                    <span className="font-semibold text-white truncate max-w-[120px]">
                      {channelsInbox.instagram.last_message.patient_name || channelsInbox.instagram.last_message.sender_id}
                    </span>
                    <span className="text-[9px] font-mono text-cyan-bright/80">
                      {new Date(channelsInbox.instagram.last_message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} hs
                    </span>
                  </div>
                  <p className="text-[11px] text-titanium-200 line-clamp-2 italic">
                    "{channelsInbox.instagram.last_message.content}"
                  </p>
                </>
              ) : (
                <p className="text-[11px] text-titanium-400 italic">Esperando DMs en @luminadentalstudio</p>
              )}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-white/10 flex items-center gap-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onOpenInbox('instagram');
              }}
              className="flex-1 flex items-center justify-center gap-1.5 py-1.5 px-2.5 text-xs font-bold bg-pink-500/20 hover:bg-pink-500/30 text-pink-300 border border-pink-500/40 rounded-xl transition cursor-pointer"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Ver Hilos ({channelsInbox.instagram?.active_threads || 0})</span>
            </button>
          </div>
        </div>

        {/* 4. YouTube Channel Card (Mejora 16, 17) */}
        <div
          onClick={() => onOpenInbox('youtube')}
          className="glass-card rounded-2xl p-5 border border-cyan-bright/20 hover:border-red-400/50 shadow-xl flex flex-col justify-between relative overflow-hidden cursor-pointer transition-all duration-200 hover:bg-white/[0.02]"
        >
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 rounded-xl bg-red-950/80 text-red-400 flex items-center justify-center border border-red-500/30">
                <YoutubeIcon className="w-5 h-5" />
              </div>
              <div className="flex items-center gap-1.5">
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-bright/15 text-cyan-bright border border-cyan-bright/40 shadow-cyan-glow flex items-center gap-1">
                  <MessageSquare className="w-2.5 h-2.5" />
                  {channelsInbox.youtube?.total_messages || 0} msgs
                </span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-950 text-red-300 border border-red-500/30 inline-flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse" /> Data API v3
                </span>
              </div>
            </div>

            <h3 className="font-bold text-white text-sm">Canal de YouTube</h3>

            {/* 10-Min SLA Countdown (Mejora 17) */}
            <div className="mt-1 flex items-center justify-between text-[11px]">
              <span className="text-titanium-400">SLA Comentario:</span>
              <span className="font-mono font-bold text-amber-300 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {formatCountdown(ytCountdown)}
              </span>
            </div>

            {/* Preview Box & Video Title (Mejora 16) */}
            <div className="mt-2.5 p-2.5 rounded-xl bg-black/40 border border-white/10 text-left">
              {channelsInbox.youtube?.last_message ? (
                <>
                  <div className="flex items-center justify-between text-[10px] text-titanium-400 mb-1">
                    <span className="font-semibold text-white truncate max-w-[120px]">
                      {channelsInbox.youtube.last_message.patient_name || channelsInbox.youtube.last_message.sender_id}
                    </span>
                    <span className="text-[9px] font-mono text-cyan-bright/80">
                      {new Date(channelsInbox.youtube.last_message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} hs
                    </span>
                  </div>
                  <p className="text-[11px] text-titanium-200 line-clamp-2 italic">
                    "{channelsInbox.youtube.last_message.content}"
                  </p>
                </>
              ) : (
                <p className="text-[11px] text-titanium-400 italic">Sin comentarios pendientes</p>
              )}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-white/10 flex items-center gap-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onOpenInbox('youtube');
              }}
              className="flex-1 flex items-center justify-center gap-1.5 py-1.5 px-2.5 text-xs font-bold bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/40 rounded-xl transition cursor-pointer"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Ver ({channelsInbox.youtube?.active_threads || 0})</span>
            </button>
            <button
              onClick={onSyncYouTube}
              disabled={isSyncingYouTube}
              className="p-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-white transition cursor-pointer border border-white/10 disabled:opacity-50"
              title="Sincronizar comentarios de YouTube ahora"
            >
              <RefreshCw className={`w-4 h-4 ${isSyncingYouTube ? 'animate-spin' : ''}`} />
            </button>
          </div>
          {syncMessage && (
            <div className="mt-2 text-[10px] text-cyan-bright font-mono animate-fadeIn truncate">
              {syncMessage}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
