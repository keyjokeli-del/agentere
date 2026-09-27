'use client';

import React from 'react';
import { Users, CalendarCheck, AlertTriangle, DollarSign, Zap } from 'lucide-react';

interface KpiData {
  patients_today: number;
  appointments_confirmed: number;
  urgent_cases: number;
  estimated_pipeline_usd: number;
  avg_sla_seconds: number;
}

interface KpiStripProps {
  kpis: KpiData;
  backendOnline: boolean;
}

export const KpiStrip: React.FC<KpiStripProps> = ({ kpis, backendOnline }) => {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 mb-6">
      {/* 1. Pacientes Hoy */}
      <div className="glass-card rounded-2xl p-3.5 border border-cyan-bright/20 bg-sapphire-950/70 shadow-lg relative overflow-hidden flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-cyan-bright/15 text-cyan-bright flex items-center justify-center border border-cyan-bright/30 shrink-0">
          <Users className="w-5 h-5" />
        </div>
        <div className="min-w-0">
          <p className="text-[11px] font-medium text-titanium-400 truncate">Pacientes Hoy</p>
          <div className="flex items-baseline gap-1.5">
            <span className="text-xl font-black text-white font-mono">{kpis.patients_today}</span>
            <span className="text-[10px] text-cyan-bright font-semibold">activos</span>
          </div>
        </div>
      </div>

      {/* 2. Citas Confirmadas */}
      <div className="glass-card rounded-2xl p-3.5 border border-emerald-500/20 bg-emerald-950/40 shadow-lg relative overflow-hidden flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-emerald-500/15 text-emerald-400 flex items-center justify-center border border-emerald-500/30 shrink-0">
          <CalendarCheck className="w-5 h-5" />
        </div>
        <div className="min-w-0">
          <p className="text-[11px] font-medium text-emerald-300/80 truncate">Citas Confirmadas</p>
          <div className="flex items-baseline gap-1.5">
            <span className="text-xl font-black text-emerald-200 font-mono">{kpis.appointments_confirmed}</span>
            <span className="text-[10px] text-emerald-400 font-semibold">en agenda</span>
          </div>
        </div>
      </div>

      {/* 3. Urgencias Activas */}
      <div className="glass-card rounded-2xl p-3.5 border border-coral-500/30 bg-rose-950/40 shadow-lg relative overflow-hidden flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-rose-500/15 text-rose-400 flex items-center justify-center border border-rose-500/30 shrink-0">
          <AlertTriangle className="w-5 h-5 animate-pulse" />
        </div>
        <div className="min-w-0">
          <p className="text-[11px] font-medium text-rose-300/80 truncate">Casos de Urgencia</p>
          <div className="flex items-baseline gap-1.5">
            <span className="text-xl font-black text-rose-200 font-mono">{kpis.urgent_cases}</span>
            <span className="text-[10px] text-rose-400 font-semibold">prioridad</span>
          </div>
        </div>
      </div>

      {/* 4. Pipeline Estimado USD */}
      <div className="glass-card rounded-2xl p-3.5 border border-amber-500/20 bg-amber-950/40 shadow-lg relative overflow-hidden flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-amber-500/15 text-amber-400 flex items-center justify-center border border-amber-500/30 shrink-0">
          <DollarSign className="w-5 h-5" />
        </div>
        <div className="min-w-0">
          <p className="text-[11px] font-medium text-amber-300/80 truncate">Pipeline Estimado</p>
          <div className="flex items-baseline gap-1.5">
            <span className="text-xl font-black text-amber-200 font-mono">
              ${kpis.estimated_pipeline_usd.toLocaleString('en-US', { minimumFractionDigits: 0 })}
            </span>
            <span className="text-[10px] text-amber-400 font-semibold">USD</span>
          </div>
        </div>
      </div>

      {/* 5. SLA Promedio */}
      <div className="glass-card rounded-2xl p-3.5 border border-cyan-bright/20 bg-sapphire-950/70 shadow-lg relative overflow-hidden flex items-center gap-3 col-span-2 sm:col-span-1">
        <div className="w-10 h-10 rounded-xl bg-cyan-bright/15 text-cyan-bright flex items-center justify-center border border-cyan-bright/30 shrink-0">
          <Zap className="w-5 h-5" />
        </div>
        <div className="min-w-0">
          <p className="text-[11px] font-medium text-titanium-400 truncate">SLA Promedio</p>
          <div className="flex items-baseline gap-1.5">
            <span className="text-xl font-black text-cyan-bright font-mono">{kpis.avg_sla_seconds}s</span>
            <span className="text-[10px] text-emerald-400 font-semibold">Groq Llama 3.3</span>
          </div>
        </div>
      </div>
    </div>
  );
};
