'use client';

import React, { useState } from 'react';
import { X, Sparkles, AlertCircle, CheckCircle2 } from 'lucide-react';

interface OdontogramDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  patientName?: string;
  detectedTeeth?: string[];
  onInsertToothIntoChat?: (tooth: string) => void;
}

export const OdontogramDrawer: React.FC<OdontogramDrawerProps> = ({
  isOpen,
  onClose,
  patientName = 'Paciente Activo',
  detectedTeeth = [],
  onInsertToothIntoChat
}) => {
  const [selectedTooth, setSelectedTooth] = useState<string | null>(null);

  if (!isOpen) return null;

  // FDI quadrants
  const q1 = ['18', '17', '16', '15', '14', '13', '12', '11'];
  const q2 = ['21', '22', '23', '24', '25', '26', '27', '28'];
  const q4 = ['48', '47', '46', '45', '44', '43', '42', '41'];
  const q3 = ['31', '32', '33', '34', '35', '36', '37', '38'];

  const getToothStatus = (tooth: string) => {
    if (detectedTeeth.includes(tooth)) return 'detected';
    if (['18', '28', '38', '48'].includes(tooth)) return 'wisdom';
    return 'normal';
  };

  const renderTooth = (tooth: string) => {
    const status = getToothStatus(tooth);
    const isSelected = selectedTooth === tooth;

    let baseBg = 'bg-sapphire-900/60 border-white/20 text-slate-200 hover:border-cyan-bright/50';
    if (status === 'detected') {
      baseBg = 'bg-rose-500/20 border-rose-500 text-rose-300 shadow-lg shadow-rose-500/20 font-bold animate-pulse';
    } else if (status === 'wisdom') {
      baseBg = 'bg-amber-500/15 border-amber-500/40 text-amber-300 font-semibold';
    }

    if (isSelected) {
      baseBg = 'bg-cyan-bright text-abyssal border-cyan-bright font-black ring-2 ring-cyan-bright/50 scale-105';
    }

    return (
      <button
        key={tooth}
        onClick={() => setSelectedTooth(tooth)}
        className={`w-9 h-11 rounded-lg border text-xs flex flex-col items-center justify-between p-1 transition-all duration-150 cursor-pointer ${baseBg}`}
        title={`Pieza FDI ${tooth}`}
      >
        <span className="text-[9px] font-mono opacity-70">{tooth}</span>
        <div className="w-2.5 h-2.5 rounded-full border border-current opacity-60" />
      </button>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-fadeIn">
      <div className="w-full max-w-2xl glass-panel rounded-3xl p-6 border border-cyan-bright/30 bg-sapphire-950/95 shadow-2xl relative overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/10">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl">🦷</span>
              <h2 className="text-base font-extrabold text-white">Odontograma Clínico FDI</h2>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-cyan-bright/20 text-cyan-bright border border-cyan-bright/40">
                Sistema FDI Internacional
              </span>
            </div>
            <p className="text-xs text-titanium-400 mt-0.5">
              Paciente: <span className="font-semibold text-white">{patientName}</span>
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-titanium-300 hover:text-white transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 py-3 text-[11px] text-titanium-400 border-b border-white/5 font-medium">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
            <span>Mencionada en Chat / Urgencia</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
            <span>Tercer Molar / Juicio</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-bright" />
            <span>Seleccionada</span>
          </div>
        </div>

        {/* FDI Quadrants Grid */}
        <div className="my-6 space-y-6">
          {/* Maxilar Superior */}
          <div>
            <div className="text-[10px] font-mono text-cyan-bright uppercase tracking-wider text-center mb-2 font-bold">
              ── MAXILAR SUPERIOR (Arcada Superior) ──
            </div>
            <div className="flex justify-center gap-1 sm:gap-2">
              <div className="flex gap-1 bg-black/30 p-2 rounded-xl border border-white/5">
                {q1.map(renderTooth)}
              </div>
              <div className="w-px bg-white/20 my-1" />
              <div className="flex gap-1 bg-black/30 p-2 rounded-xl border border-white/5">
                {q2.map(renderTooth)}
              </div>
            </div>
          </div>

          {/* Mandíbula Inferior */}
          <div>
            <div className="flex justify-center gap-1 sm:gap-2">
              <div className="flex gap-1 bg-black/30 p-2 rounded-xl border border-white/5">
                {q4.map(renderTooth)}
              </div>
              <div className="w-px bg-white/20 my-1" />
              <div className="flex gap-1 bg-black/30 p-2 rounded-xl border border-white/5">
                {q3.map(renderTooth)}
              </div>
            </div>
            <div className="text-[10px] font-mono text-cyan-bright uppercase tracking-wider text-center mt-2 font-bold">
              ── MANDÍBULA INFERIOR (Arcada Inferior) ──
            </div>
          </div>
        </div>

        {/* Selected Tooth Action Bar */}
        {selectedTooth && (
          <div className="p-3.5 rounded-2xl bg-cyan-950/60 border border-cyan-bright/30 flex items-center justify-between gap-3 animate-fadeIn">
            <div>
              <p className="text-xs font-bold text-white">Pieza FDI {selectedTooth} seleccionada</p>
              <p className="text-[11px] text-titanium-300">
                {['18', '28', '38', '48'].includes(selectedTooth) ? 'Tercer molar (muela de juicio)' : 'Pieza dental permanente'}
              </p>
            </div>
            {onInsertToothIntoChat && (
              <button
                onClick={() => {
                  onInsertToothIntoChat(selectedTooth);
                  onClose();
                }}
                className="px-3.5 py-1.5 rounded-xl bg-cyan-bright hover:bg-cyan-bright/90 text-abyssal font-bold text-xs shadow-cyan-glow transition cursor-pointer"
              >
                Insertar en Chat 💬
              </button>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="mt-4 pt-3 border-t border-white/10 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/15 text-white font-bold text-xs transition cursor-pointer"
          >
            Cerrar Odontograma
          </button>
        </div>
      </div>
    </div>
  );
};
