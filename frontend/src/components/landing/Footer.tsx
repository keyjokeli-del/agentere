'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { MapPin, Phone, Clock, AlertTriangle, LayoutDashboard, Heart } from 'lucide-react';

export default function Footer() {
  return (
    <footer 
      aria-label="Pie de página e información institucional"
      className="border-t border-cyan-bright/20 bg-abyssal text-titanium-400 text-xs pt-14 pb-12 relative overflow-hidden"
    >
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        
        {/* Main Footer Grid */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
          
          {/* Brand Col (5 cols) */}
          <div className="md:col-span-5 space-y-4">
            <div className="flex items-center gap-3">
              <div className="relative w-8 h-8 rounded-xl overflow-hidden border border-cyan-bright/40 shadow-cyan-glow bg-abyssal">
                <Image
                  src="/social-kit/lumina-logo.png"
                  alt="Lumina Dental Studio Logo"
                  fill
                  sizes="32px"
                  className="object-cover"
                />
              </div>
              <span className="font-extrabold text-base text-white">
                Lumina <span className="text-cyan-bright text-xs tracking-widest uppercase">Dental Studio</span>
              </span>
            </div>
            <p className="text-titanium-400 text-xs leading-relaxed max-w-sm">
              Odontología de alta precisión combinada con agentes de inteligencia artificial para una atención ágil, empática y continua las 24 horas.
            </p>
            <div className="pt-2">
              <Link 
                href="/dashboard"
                className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-cyan-bright/15 text-titanium-300 hover:text-cyan-bright border border-white/10 hover:border-cyan-bright/30 transition-all font-medium text-xs"
              >
                <LayoutDashboard className="w-3.5 h-3.5 text-cyan-bright" />
                <span>Portal Personal Clínico (Dashboard)</span>
              </Link>
            </div>
          </div>

          {/* Clinic Hours & Contact (4 cols) */}
          <div className="md:col-span-4 space-y-3">
            <h3 className="font-bold text-sm text-white uppercase tracking-wider">
              Consultorio & Atención
            </h3>
            <ul className="space-y-2.5 text-titanium-300">
              <li className="flex items-start gap-2">
                <MapPin className="w-4 h-4 text-cyan-bright shrink-0 mt-0.5" />
                <span>Av. Santa Fe 2450, Piso 3, Consultorio B, CABA</span>
              </li>
              <li className="flex items-center gap-2">
                <Phone className="w-4 h-4 text-cyan-bright shrink-0" />
                <span>+54 9 11 4567-8900 (Guardia & Triage 24/7)</span>
              </li>
              <li className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-cyan-bright shrink-0" />
                <span>Lunes a Sábado: 09:00 a 19:00 hs (Franjas de 45 min)</span>
              </li>
            </ul>
          </div>

          {/* Quick Anchor Links (3 cols) */}
          <div className="md:col-span-3 space-y-3">
            <h3 className="font-bold text-sm text-white uppercase tracking-wider">
              Navegación
            </h3>
            <ul className="space-y-2">
              <li>
                <a href="#tratamientos" className="hover:text-cyan-bright transition-colors">Tratamientos Odontológicos</a>
              </li>
              <li>
                <a href="#tecnologia" className="hover:text-cyan-bright transition-colors">Tecnología Omnicanal</a>
              </li>
              <li>
                <a href="#agendar" className="hover:text-cyan-bright transition-colors">Agendador de Citas</a>
              </li>
              <li>
                <Link href="/dashboard" className="hover:text-cyan-bright transition-colors">Portal Clínico 2026</Link>
              </li>
            </ul>
          </div>

        </div>

        {/* Ethical Sanitary & Medical Disclaimer (WCAG 2.1 AA Compliant) */}
        <div className="p-4 rounded-2xl glass-card flex items-start gap-3 text-titanium-300 text-[11px] leading-relaxed border border-cyan-bright/20">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <p>
            <strong className="text-white">Aviso Médico Sanitario Obligatorio:</strong> La información, estimaciones de aranceles y orientación preliminar provistas por nuestros canales de inteligencia artificial tienen fines organizativos y de triaje previo. No constituyen un diagnóstico médico vinculante ni prescripción de medicamentos. El plan de tratamiento y diagnóstico definitivo se establecen exclusivamente en la evaluación clínica odontológica presencial.
          </p>
        </div>

        {/* Copyright & Sign-off */}
        <div className="pt-6 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-3 text-titanium-400 text-[11px]">
          <p>© {new Date().getFullYear()} Lumina Dental Studio. Todos los derechos reservados.</p>
          <p className="flex items-center gap-1">
            Diseñado con precisión <Heart className="w-3 h-3 text-rose-500 fill-current" /> y tecnología multi-agente a costo $0 USD.
          </p>
        </div>

      </div>
    </footer>
  );
}
