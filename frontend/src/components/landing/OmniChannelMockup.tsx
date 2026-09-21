'use client';

import React, { useState } from 'react';
import { Smartphone, CheckCircle2, Calendar, Sparkles, Send, ShieldCheck } from 'lucide-react';

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

export default function OmniChannelMockup() {
  const [activeTab, setActiveTab] = useState<'whatsapp' | 'instagram' | 'meta'>('whatsapp');

  return (
    <section 
      id="tecnologia"
      aria-label="Demostración de la tecnología omnicanal de Lumina"
      className="py-16 md:py-24 relative overflow-hidden"
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Title */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-12">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-sapphire-900/80 border border-cyan-bright/30 text-cyan-bright text-xs font-bold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Infraestructura Omnicanal en Tiempo Real</span>
          </span>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            Escribe desde tu aplicación favorita.{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-bright via-teal-300 to-white">
              Nuestros agentes se encargan del resto.
            </span>
          </h2>
          <p className="text-slate-400 text-sm sm:text-base">
            El sistema multi-agente interpreta la intención, valida la agenda médica en Google Calendar y confirma tu turno sin intermediarios.
          </p>
        </div>

        {/* Channel Switcher Pills */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <button
            onClick={() => setActiveTab('whatsapp')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'whatsapp'
                ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20'
                : 'bg-white/5 text-slate-300 hover:bg-white/10 border border-white/10'
            }`}
          >
            <Smartphone className="w-4 h-4" />
            <span>WhatsApp Directo</span>
          </button>
          <button
            onClick={() => setActiveTab('instagram')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'instagram'
                ? 'bg-gradient-to-r from-pink-500 to-rose-500 text-white shadow-lg shadow-pink-500/20'
                : 'bg-white/5 text-slate-300 hover:bg-white/10 border border-white/10'
            }`}
          >
            <InstagramIcon className="w-4 h-4" />
            <span>Instagram Direct</span>
          </button>
          <button
            onClick={() => setActiveTab('meta')}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              activeTab === 'meta'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                : 'bg-white/5 text-slate-300 hover:bg-white/10 border border-white/10'
            }`}
          >
            <FacebookIcon className="w-4 h-4" />
            <span>Facebook Messenger</span>
          </button>
        </div>

        {/* 3D ARTWORK CONTAINER WITH FLOATING OVERLAYS (16:9 Widescreen) */}
        <div className="relative w-full max-w-5xl mx-auto rounded-3xl overflow-hidden border border-cyan-bright/20 shadow-2xl bg-gradient-to-b from-sapphire-900/40 via-sapphire-950 to-slate-950">
          
          {/* Ambient Glow */}
          <div className="absolute inset-0 bg-radial from-cyan-bright/10 via-transparent to-transparent pointer-events-none -z-10" />

          {/* RENDER 3D NANO BANA2: Arte Conceptual Omnicanal (Aspect Ratio 16:9) */}
          {/* INSTRUCCIÓN: Cuando generes el render 3D con Nano Bana2, guárdalo en /public/images/3d/omnichannel-core-3d.webp y sustituye este placeholder con <Image src="/images/3d/omnichannel-core-3d.webp" alt="Núcleo Omnicanal Lumina 3D" fill className="object-cover opacity-60" priority /> */}
          <div 
            className="w-full aspect-[16/9] min-h-[380px] md:min-h-[480px] bg-slate-900/80 border border-cyan-bright/30 animate-pulse flex flex-col items-center justify-center text-center p-6 relative overflow-hidden"
            role="img"
            aria-label="Render 3D Nano Bana2: Núcleo geométrico 3D de cristal dental en Sapphire #0F3D56 emitiendo haces lumínicos en Cyan #00E5FF conectados a redes y Google Calendar"
          >
            <div className="w-20 h-20 rounded-3xl bg-cyan-bright/10 border border-cyan-bright/40 flex items-center justify-center text-cyan-bright mb-3">
              <Sparkles className="w-10 h-10 drop-shadow-[0_0_15px_rgba(0,229,255,0.8)]" />
            </div>
            <p className="font-bold text-sm text-white uppercase tracking-wider">
              Render 3D Nano Bana2: [Arte Conceptual Omnicanal "Lumina Core"]
            </p>
            <p className="text-xs text-slate-400 mt-1 max-w-md">
              Aspect Ratio: <strong>16:9</strong> (Widescreen 1920x1080px, perspectiva isométrica futurista)
            </p>
            <span className="mt-3 text-xs font-mono text-cyan-bright/90 bg-cyan-bright/10 px-3 py-1 rounded border border-cyan-bright/20">
              /public/images/3d/omnichannel-core-3d.webp
            </span>
          </div>

          {/* Floating Live Conversation Overlays (Glassmorphism) */}
          <div className="absolute inset-0 p-4 sm:p-8 md:p-10 flex flex-col justify-between pointer-events-none">
            
            {/* Top Left Floating Chat: Patient Message */}
            <div className="self-start max-w-xs sm:max-w-sm rounded-2xl p-4 bg-sapphire-950/80 border border-white/20 backdrop-blur-xl shadow-xl space-y-1.5 animate-float pointer-events-auto">
              <div className="flex items-center justify-between text-[11px] text-slate-400 font-semibold">
                <span className="flex items-center gap-1.5 text-emerald-400">
                  <Smartphone className="w-3.5 h-3.5" /> Paciente vía WhatsApp
                </span>
                <span>Hoy 10:14 hs</span>
              </div>
              <p className="text-xs sm:text-sm text-slate-100 font-medium">
                "Hola! Me duele una muela del juicio, ¿tienen turno disponible hoy o mañana por la mañana?"
              </p>
            </div>

            {/* Bottom Right Floating Chat: Agent Intelligent Resolution */}
            <div className="self-end max-w-xs sm:max-w-md rounded-2xl p-4 bg-sapphire-900/90 border border-cyan-bright/40 backdrop-blur-xl shadow-2xl space-y-2 pointer-events-auto">
              <div className="flex items-center justify-between text-[11px] text-cyan-bright font-bold">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-cyan-bright animate-ping" />
                  Asistente IA • Triage Clínico
                </span>
                <span className="bg-cyan-bright/20 text-cyan-bright px-2 py-0.5 rounded text-[10px]">
                  Groq 70B
                </span>
              </div>
              <p className="text-xs sm:text-sm text-slate-100 leading-relaxed">
                "Lamentamos tu dolor. Por la urgencia, tenemos un espacio prioritario mañana a las <strong>09:45 hs</strong> o <strong>11:15 hs</strong>. ¿Deseas que reservemos alguno a tu nombre?"
              </p>
              <div className="pt-2 border-t border-white/10 flex items-center justify-between text-[11px] text-slate-300 font-medium">
                <span className="flex items-center gap-1 text-teal-300 font-semibold">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Horario verificado en Google Calendar
                </span>
                <span className="text-[10px] text-slate-400 font-mono">45 min</span>
              </div>
            </div>

          </div>

        </div>

      </div>
    </section>
  );
}
