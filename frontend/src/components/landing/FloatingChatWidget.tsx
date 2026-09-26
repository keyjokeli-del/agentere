'use client';

import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Bot, User, Sparkles, AlertCircle } from 'lucide-react';

interface ChatMsg {
  sender: 'user' | 'bot';
  text: string;
  time: string;
}

export default function FloatingChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [inputMsg, setInputMsg] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMsg[]>([
    {
      sender: 'bot',
      text: '👋 ¡Hola! Soy el asistente clínico de Lumina Dental Studio. ¿En qué tratamiento o consulta sobre aranceles te puedo ayudar hoy?',
      time: 'Ahora'
    }
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const query = inputMsg.trim();
    if (!query || isLoading) return;

    const userEntry: ChatMsg = {
      sender: 'user',
      text: query,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userEntry]);
    setInputMsg('');
    setIsLoading(true);

    try {
      const res = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: query,
          sender_id: 'web-visitor-' + (typeof window !== 'undefined' ? window.navigator.userAgent.slice(0, 8) : '1'),
          channel: 'web',
          sender_name: 'Visitante Web'
        })
      });

      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [
          ...prev,
          {
            sender: 'bot',
            text: data.reply || 'Gracias por tu consulta. Un especialista te atenderá a la brevedad.',
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ]);
      } else {
        throw new Error('Respuesta no válida del servidor');
      }
    } catch {
      setMessages(prev => [
        ...prev,
        {
          sender: 'bot',
          text: 'Disculpa, nuestro asistente está en mantenimiento momentáneo. Puedes contactarnos por WhatsApp al +54 9 11 2345-6789 o consultar en la clínica.',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Floating Trigger Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="group relative flex items-center gap-3 px-5 py-3.5 rounded-full bg-gradient-to-r from-cyan-bright via-teal-400 to-cyan-500 text-abyssal-950 font-bold shadow-[0_0_30px_rgba(0,229,255,0.45)] hover:shadow-[0_0_40px_rgba(0,229,255,0.7)] hover:scale-105 transition-all duration-300"
          aria-label="Abrir chat de asistencia odontológica"
        >
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
          </span>
          <MessageSquare className="w-5 h-5 text-abyssal-950" />
          <span className="text-sm font-extrabold tracking-wide hidden sm:inline">
            Consultar con IA Lumina
          </span>
        </button>
      )}

      {/* Floating Chat Modal */}
      {isOpen && (
        <div className="w-[92vw] sm:w-[390px] h-[520px] rounded-3xl bg-abyssal-950/95 border border-cyan-bright/40 shadow-[0_15px_50px_rgba(0,0,0,0.8),0_0_35px_rgba(0,229,255,0.2)] backdrop-blur-2xl flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-5 duration-300">
          {/* Header */}
          <div className="p-4 bg-gradient-to-r from-sapphire-900 to-abyssal-900 border-b border-cyan-bright/20 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-cyan-bright/15 border border-cyan-bright/40 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-cyan-bright" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-1.5">
                  Lumina Clinical AI
                  <span className="inline-block w-2 h-2 rounded-full bg-emerald-400"></span>
                </h3>
                <p className="text-[11px] text-teal-200/70">Triaje, Precios y Citas en Tiempo Real</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition"
              aria-label="Cerrar chat"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages Feed */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3 scrollbar-thin scrollbar-thumb-cyan-bright/20">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.sender === 'bot' && (
                  <div className="w-7 h-7 rounded-lg bg-cyan-bright/20 border border-cyan-bright/30 flex items-center justify-center shrink-0 mt-1">
                    <Bot className="w-4 h-4 text-cyan-bright" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-2xl p-3 text-xs leading-relaxed ${
                    m.sender === 'user'
                      ? 'bg-gradient-to-r from-cyan-bright to-teal-400 text-abyssal-950 font-medium rounded-tr-none'
                      : 'bg-sapphire-900/70 border border-cyan-bright/20 text-slate-100 rounded-tl-none'
                  }`}
                >
                  <p className="whitespace-pre-line">{m.text}</p>
                  <span className={`block text-[10px] mt-1 text-right ${m.sender === 'user' ? 'text-abyssal-950/70' : 'text-slate-400'}`}>
                    {m.time}
                  </span>
                </div>
                {m.sender === 'user' && (
                  <div className="w-7 h-7 rounded-lg bg-teal-400/20 border border-teal-400/30 flex items-center justify-center shrink-0 mt-1">
                    <User className="w-4 h-4 text-teal-300" />
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="flex gap-2.5 items-center text-xs text-cyan-bright/80 italic">
                <div className="w-7 h-7 rounded-lg bg-cyan-bright/10 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-cyan-bright animate-pulse" />
                </div>
                <span>Consultando memoria clínica y agenda...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick suggestions */}
          <div className="px-3 py-1.5 bg-sapphire-950/40 border-t border-cyan-bright/10 flex gap-2 overflow-x-auto text-[11px] whitespace-nowrap">
            <button
              type="button"
              onClick={() => { setInputMsg('¿Cuánto cuesta un blanqueamiento?'); }}
              className="px-2.5 py-1 rounded-full bg-cyan-bright/10 hover:bg-cyan-bright/20 border border-cyan-bright/20 text-cyan-300 transition"
            >
              💰 Precio blanqueamiento
            </button>
            <button
              type="button"
              onClick={() => { setInputMsg('¿Atienden urgencias hoy?'); }}
              className="px-2.5 py-1 rounded-full bg-cyan-bright/10 hover:bg-cyan-bright/20 border border-cyan-bright/20 text-cyan-300 transition"
            >
              🚨 Urgencias
            </button>
            <button
              type="button"
              onClick={() => { setInputMsg('Quiero agendar para limpieza'); }}
              className="px-2.5 py-1 rounded-full bg-cyan-bright/10 hover:bg-cyan-bright/20 border border-cyan-bright/20 text-cyan-300 transition"
            >
              📅 Agendar limpieza
            </button>
          </div>

          {/* Input form */}
          <form
            onSubmit={handleSendMessage}
            className="p-3 bg-abyssal-950 border-t border-cyan-bright/20 flex gap-2"
          >
            <input
              type="text"
              value={inputMsg}
              onChange={e => setInputMsg(e.target.value)}
              placeholder="Escribe tu consulta médica..."
              className="flex-1 bg-sapphire-950/80 border border-cyan-bright/30 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-cyan-bright transition"
            />
            <button
              type="submit"
              disabled={isLoading || !inputMsg.trim()}
              className="p-2.5 rounded-xl bg-gradient-to-r from-cyan-bright to-teal-400 text-abyssal-950 font-bold hover:scale-105 active:scale-95 disabled:opacity-50 disabled:pointer-events-none transition"
              aria-label="Enviar mensaje"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
