'use client';

import React, { useState, useRef } from 'react';
import { Smartphone, CheckCircle2, Sparkles, Send, Play, Pause, Volume2, VolumeX, Film } from 'lucide-react';

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

export default function OmniChannelMockup() {
  const [activeTab, setActiveTab] = useState<'whatsapp' | 'instagram' | 'meta'>('whatsapp');
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [isMuted, setIsMuted] = useState<boolean>(true);
  const videoRef = useRef<HTMLVideoElement>(null);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
        setIsPlaying(false);
      } else {
        videoRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const channelInfo = {
    whatsapp: {
      patientChannel: 'WhatsApp Directo',
      patientColor: 'text-emerald-400',
      patientIcon: Smartphone,
      patientMsg: '¡Hola! Me duele una muela del juicio, ¿tienen turno disponible hoy o mañana por la mañana?',
      botMsg: 'Lamentamos tu molestia. Por la urgencia, tenemos un espacio prioritario reservado mañana a las 09:45 hs o 11:15 hs. ¿Deseas que confirmemos alguno a tu nombre?',
    },
    instagram: {
      patientChannel: 'Instagram Direct',
      patientColor: 'text-pink-400',
      patientIcon: InstagramIcon,
      patientMsg: 'Buenas tardes! Vi su reel de blanqueamiento láser, ¿cuál es el precio y cuánto dura la sesión?',
      botMsg: '¡Hola! El tratamiento se completa en 1 sesión de 45 minutos ($90 a $150 USD). El costo incluye profilaxis previa. ¿Te gustaría agendar una evaluación para este viernes a las 15:00 hs?',
    },
    meta: {
      patientChannel: 'Facebook Messenger',
      patientColor: 'text-blue-400',
      patientIcon: FacebookIcon,
      patientMsg: 'Hola, quisiera consultar si realizan implantes guiados en 3D para una rehabilitación completa.',
      botMsg: '¡Hola! Sí, contamos con tomografía digital y cirugía guiada por ordenador en titanio y zafiro ($350 a $600 USD). Tenemos disponibilidad diagnóstica el lunes a las 10:30 hs.',
    }
  };

  const current = channelInfo[activeTab];
  const CurrentIcon = current.patientIcon;

  return (
    <section 
      id="tecnologia"
      aria-label="Demostración de la tecnología omnicanal de Lumina"
      className="py-16 md:py-24 relative overflow-hidden"
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Title */}
        <div className="text-center max-w-3xl mx-auto space-y-4 mb-12">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full glass-badge text-xs font-bold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Infraestructura Omnicanal en Tiempo Real</span>
          </span>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            Escribe desde tu aplicación favorita.{' '}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-bright via-teal-300 to-white">
              Nuestros agentes se encargan del resto.
            </span>
          </h2>
          <p className="text-titanium-300 text-sm sm:text-base">
            El sistema multi-agente interpreta la intención, valida la agenda médica en Google Calendar y confirma tu turno sin intermediarios ni demoras.
          </p>
        </div>

        {/* Channel Switcher Pills */}
        <div className="flex items-center justify-center gap-2 mb-8">
          <button
            onClick={() => setActiveTab('whatsapp')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'whatsapp'
                ? 'bg-emerald-500 text-abyssal shadow-lg shadow-emerald-500/25 scale-102'
                : 'bg-sapphire-900/40 text-titanium-300 hover:bg-sapphire-900/70 border border-white/10'
            }`}
          >
            <Smartphone className="w-4 h-4" />
            <span>WhatsApp Directo</span>
          </button>
          <button
            onClick={() => setActiveTab('instagram')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'instagram'
                ? 'bg-gradient-to-r from-pink-500 to-rose-500 text-white shadow-lg shadow-pink-500/25 scale-102'
                : 'bg-sapphire-900/40 text-titanium-300 hover:bg-sapphire-900/70 border border-white/10'
            }`}
          >
            <InstagramIcon className="w-4 h-4" />
            <span>Instagram Direct</span>
          </button>
          <button
            onClick={() => setActiveTab('meta')}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
              activeTab === 'meta'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/25 scale-102'
                : 'bg-sapphire-900/40 text-titanium-300 hover:bg-sapphire-900/70 border border-white/10'
            }`}
          >
            <FacebookIcon className="w-4 h-4" />
            <span>Facebook Messenger</span>
          </button>
        </div>

        {/* HOLOGRAPHIC VIDEO PLAYER CONTAINER */}
        <div className="relative w-full max-w-5xl mx-auto rounded-3xl overflow-hidden border border-cyan-bright/30 shadow-[0_0_50px_rgba(0,229,255,0.15)] bg-gradient-to-b from-sapphire-900/60 via-sapphire-950 to-abyssal-950">
          
          {/* Ambient Glow */}
          <div className="absolute inset-0 bg-radial from-cyan-bright/10 via-transparent to-transparent pointer-events-none -z-10" />

          {/* Video Reel Showcase */}
          <div className="relative w-full aspect-video min-h-[360px] md:min-h-[480px] bg-abyssal flex items-center justify-center overflow-hidden">
            <video
              ref={videoRef}
              src="/social-kit/lumina-promo-reel.mp4"
              poster="/social-kit/lumina-cover.png"
              autoPlay
              muted
              loop
              playsInline
              preload="metadata"
              className="w-full h-full object-cover opacity-85"
            />
            {/* Holographic Scanline Overlay */}
            <div className="absolute inset-0 bg-gradient-to-b from-cyan-bright/5 via-transparent to-abyssal/80 pointer-events-none" />
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_40%,rgba(5,19,32,0.6)_100%)] pointer-events-none" />
            
            {/* Top Video Header Tag & Interactive Controls */}
            <div className="absolute top-4 left-4 right-4 sm:top-6 sm:left-6 sm:right-6 flex items-center justify-between pointer-events-auto">
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-sapphire-950/85 border border-cyan-bright/30 backdrop-blur-md text-xs font-semibold text-white">
                <Film className="w-3.5 h-3.5 text-cyan-bright" />
                <span>Lumina Cinematic Reel • 1080p</span>
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse ml-1" />
              </div>

              {/* Optional playback controls */}
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={togglePlay}
                  className="p-2 rounded-xl bg-sapphire-950/85 border border-cyan-bright/30 text-white hover:text-cyan-bright backdrop-blur-md transition cursor-pointer"
                  title={isPlaying ? 'Pausar video' : 'Reproducir video'}
                  aria-label="Reproducir o pausar video"
                >
                  {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                </button>
                <button
                  type="button"
                  onClick={toggleMute}
                  className="p-2 rounded-xl bg-sapphire-950/85 border border-cyan-bright/30 text-white hover:text-cyan-bright backdrop-blur-md transition cursor-pointer"
                  title={isMuted ? 'Activar audio ambiental' : 'Silenciar audio'}
                  aria-label="Silenciar o activar audio"
                >
                  {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                </button>
              </div>
            </div>
          </div>

          {/* Floating Live Conversation Overlays (Glassmorphism) */}
          <div className="absolute inset-0 p-4 sm:p-8 md:p-10 flex flex-col justify-between pointer-events-none">
            
            {/* Top Left Floating Chat: Patient Message */}
            <div className="self-start max-w-xs sm:max-w-sm rounded-2xl p-4 bg-sapphire-950/90 border border-white/20 backdrop-blur-xl shadow-2xl space-y-1.5 animate-float gpu-layer pointer-events-auto mt-12 sm:mt-14">
              <div className="flex items-center justify-between text-[11px] text-titanium-400 font-semibold">
                <span className={`flex items-center gap-1.5 ${current.patientColor}`}>
                  <CurrentIcon className="w-3.5 h-3.5" /> {current.patientChannel}
                </span>
                <span>Hoy 10:14 hs</span>
              </div>
              <p className="text-xs sm:text-sm text-slate-100 font-medium">
                "{current.patientMsg}"
              </p>
            </div>

            {/* Bottom Right Floating Chat: Agent Intelligent Resolution */}
            <div className="self-end max-w-xs sm:max-w-md rounded-2xl p-4 bg-sapphire-900/95 border border-cyan-bright/50 backdrop-blur-xl shadow-[0_0_30px_rgba(0,229,255,0.2)] space-y-2 gpu-layer pointer-events-auto">
              <div className="flex items-center justify-between text-[11px] text-cyan-bright font-bold">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-cyan-bright animate-ping" />
                  Asistente IA • Triage Clínico
                </span>
                <span className="bg-cyan-bright/20 text-cyan-bright px-2 py-0.5 rounded text-[10px] font-mono border border-cyan-bright/30">
                  Groq Llama 3.3
                </span>
              </div>
              <p className="text-xs sm:text-sm text-slate-100 leading-relaxed">
                "{current.botMsg}"
              </p>
              <div className="pt-2 border-t border-white/10 flex items-center justify-between text-[11px] text-slate-300 font-medium">
                <span className="flex items-center gap-1 text-cyan-bright font-semibold">
                  <CheckCircle2 className="w-3.5 h-3.5 text-cyan-bright" /> Horario verificado en Google Calendar
                </span>
                <span className="text-[10px] text-titanium-400 font-mono">45 min</span>
              </div>
            </div>

          </div>

        </div>

      </div>
    </section>
  );
}
