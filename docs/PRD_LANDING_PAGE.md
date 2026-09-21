# PRD & Arquitectura Técnica: Landing Page "Lumina Dental Studio"

> **Documento:** Especificación Técnica (PRD) y Arquitectura de Componentes  
> **Skills Aplicadas:** `spec-driven-development`, `frontend-ui-engineering`  
> **Estado:** Listo para Revisión y Aprobación  
> **Fecha:** 2026-09-20  

---

## 1. Suposiciones Iniciales (Assumptions)

1. **Rutas y Coexistencia:** La Landing Page pública de alta conversión residirá en la ruta raíz `/` de Next.js, mientras que el panel operativo multi-agente y simulador se ubicará en `/dashboard` (o accesible vía botón de navegación interno para odontólogos y personal).
2. **Framework y Estilos:** Next.js 15 (App Router), React 19, Tailwind CSS 3.4+, Lucide React e imágenes optimizadas vía `next/image`.
3. **Generador de Assets 3D:** Nano Bana2 generará imágenes en formato PNG con canal alfa (fondo transparente) y WebP para compresión de alto rendimiento en web.
4. **Cumplimiento Ético Sanitario:** La landing enfatiza la agilidad del triage 24/7 y la agenda inmediata, pero preserva el aviso legal de que el diagnóstico clínico formal se emite presencialmente en el consultorio.

---

## 2. Objetivo y Criterios de Éxito

### 2.1. Objetivo del Producto
Diseñar e implementar una Landing Page médica y tecnológica de última generación para **"Lumina Dental Studio"**, orientada a maximizar la conversión de pacientes hacia el canal de WhatsApp y el agendador inteligente de Google Calendar, transmitiendo autoridad clínica, modernidad y confianza absoluta.

### 2.2. Usuarios Objetivo
* **Nuevos Pacientes:** Buscan atención odontológica premium (blanqueamiento, ortodoncia, estética o urgencias por dolor) y prefieren agendar al instante sin esperas telefónicas.
* **Pacientes Existentes:** Desean consultar horarios o resolver dudas rápidas 24/7.
* **Equipo Clínico:** Requiere que los pacientes lleguen con turno pre-agendado y triaje preliminar.

### 2.3. Criterios de Éxito (Medibles)
* **Performance Web (Core Web Vitals):** LCP < 2.0s, CLS < 0.05, FID/INP < 100ms.
* **Accesibilidad:** Cumplimiento estricto **WCAG 2.1 AA** (contraste mínimo 4.5:1 en textos, navegación por teclado completa, semántica ARIA).
* **Conversión Visual:** Contraste nítido de llamadas a la acción (CTA) en **Cian Brillante (`#00E5FF`)** sobre fondo **Azul Zafiro (`#0F3D56`)** con estética *glassmorphism* pulida y sin clichés de "diseño genérico de IA".

---

## 3. Tech Stack y Comandos Ejecutables

```bash
# Desarrollo local
npm --prefix frontend run dev

# Verificación estricta de TypeScript (0 errores)
npm --prefix frontend run typecheck

# Compilación de producción
npm --prefix frontend run build

# Prueba de rendimiento local (Lighthouse)
npx lighthouse http://localhost:3000 --view
```

---

## 4. Sistema de Diseño Tailwind: "Lumina Sapphire Glass"

### 4.1. Paleta Cromática y Tokens Semánticos

| Token | Hex | Rol en la Interfaz | Ratio Contraste WCAG |
|---|---|---|:---:|
| `sapphire-900` | `#0F3D56` | **Azul Zafiro Primario:** Fondo hero, contrastes oscuros, confianza clínica | 9.2:1 con blanco |
| `sapphire-950` | `#082231` | **Zafiro Profundo:** Fondos alternos, footer, gradientes sutiles | 14.1:1 con blanco |
| `cyan-bright` | `#00E5FF` | **Cian Brillante:** Acentos luminosos, botones primarios, glows, halos 3D | 4.8:1 con sapphire-900 |
| `cyan-glow` | `rgba(0, 229, 255, 0.35)` | Halo de iluminación volumétrica para renders 3D | — |
| `white-pure` | `#FFFFFF` | Fondos de tarjetas limpias, tipografía principal | 12.5:1 con sapphire |
| `glass-surface` | `rgba(255, 255, 255, 0.07)` | Tarjetas con blur en modo oscuro | — |
| `glass-border` | `rgba(255, 255, 255, 0.15)` | Bordes sutiles ultra-delgados con brillo superior | — |

### 4.2. Especificación de Efecto "Glassmorphism"
Para evitar el "AI Look" genérico y lograr acabado de producción:
* **Fórmula Glass:**
  ```css
  /* Tarjeta Glassmorphism Lumina */
  background: rgba(15, 61, 86, 0.45);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(0, 229, 255, 0.2);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
  ```
* **Luz de Borde Refractiva:** Gradiente de borde con brillo cian concentrado en la esquina superior izquierda.

### 4.3. Tipografía y Escala de Espaciado
* **Fuente Primaria:** Inter / System Sans, pesos `400`, `500`, `600`, `700`, `800`.
* **Escala Vertical:** Uso estricto de múltiplos de 4px (`space-y-4`, `py-16`, `py-24`). Cero valores arbitrarios desalineados.

---

## 5. Arquitectura de Componentes en Next.js

### 5.1. Jerarquía de Archivos

```
frontend/src/
├── app/
│   ├── page.tsx                       # Landing Page de Lumina Dental Studio
│   ├── dashboard/                     # Monitor Multi-agente y Simulador existente
│   │   └── page.tsx
│   ├── layout.tsx                     # Layout global con metadatos y fuentes
│   └── globals.css                    # Clases utilitarias y variables CSS
├── components/
│   └── landing/
│       ├── Navbar.tsx                 # Header glass sticky con logo y botón WhatsApp
│       ├── Hero.tsx                   # Titular principal, CTA directo y viewport Mascota 3D
│       ├── Features.tsx               # 4 Pilares (Triage IA, Anti-colisión, Omnicanal, Odontología)
│       ├── OmniChannelMockup.tsx      # Showcase interactivo con Arte Conceptual 3D
│       ├── TrustMetrics.tsx           # Indicadores de credibilidad y tecnología clínica
│       ├── BookingCTA.tsx             # Banner de conversión hacia WhatsApp y Google Calendar
│       └── Footer.tsx                 # Horarios, ubicación, descargo ético y créditos
├── types/
│   └── landing.ts                     # Contratos TypeScript de props y secciones
└── public/
    └── images/
        └── 3d/
            ├── lumina-mascot-3d.webp   # Render 3D Mascota Nano Bana2
            └── omnichannel-core-3d.webp # Render 3D Arte Conceptual Nano Bana2
```

---

## 6. Especificación Detallada de Componentes

### 6.1. `Navbar.tsx`
* **Estilo:** Barra flotante fija con `sticky top-4 mx-auto max-w-6xl backdrop-blur-xl bg-slate-900/60 border border-white/10 rounded-2xl`.
* **Elementos:**
  - Isotipo dental con halo cian brillante (`#00E5FF`).
  - Nombre: **Lumina Dental Studio**.
  - Enlaces ancla: `#tratamientos`, `#tecnologia`, `#agendar`.
  - Botón CTA directo: *"Acceso a Consultorio"* o *"Abrir WhatsApp"* con icono de WhatsApp pulsante.

### 6.2. `Hero.tsx`
* **Composición:** Grid asimétrico de 2 columnas (`lg:grid-cols-12`).
  - **Columna Izquierda (7 cols):**
    - Badge: `✦ Odontología de Precisión & Asistente IA 24/7`.
    - Titular H1: *"Tu sonrisa en manos expertas. Tu turno agendado en segundos."*
    - Párrafo descriptivo destacando atención sin esperas y agenda en tiempo real.
    - Acciones duales: Botón principal Cian `#00E5FF` con hover luminoso hacia WhatsApp, y botón secundario Glass hacia selector de turnos.
    - Prueba social en vivo: `★ 4.9/5 • Más de 1,200 pacientes atendidos este mes`.
  - **Columna Derecha (5 cols):** **Viewport dedicado para la Mascota Dental 3D** (ver Sección 7.1).

### 6.3. `Features.tsx`
* **Layout:** Grid de 4 tarjetas glassmorphism con acentos lumínicos:
  1. **Triaje Inmediato 24/7 (Groq Llama 3.3):** Clasificación empática de urgencias, dolor agudo y consultas frecuentes.
  2. **Google Calendar Sin Colisiones:** Franjas de 45 minutos sincronizadas en tiempo real con rechazo estricto de duplicados.
  3. **Omnicanalidad $0 Costo:** Atención unificada en WhatsApp, Instagram, Facebook y YouTube.
  4. **Atención Odontológica Premium:** Odontólogos certificados, tecnología de punta y presupuesto transparente.

### 6.4. `OmniChannelMockup.tsx`
* **Propósito:** Demostrar visualmente cómo interactúan los pacientes en redes sociales y cómo el agente inteligente responde y sincroniza la cita en Google Calendar.
* **Composición:**
  - Fondo: **Arte Conceptual Omnicanal 3D** integrado en canvas con efecto parallax sutil y viñeta en Azul Zafiro.
  - Frente: Interfaz flotante de chat simulado con burbujas de WhatsApp, Instagram y Calendar Notification con micro-animaciones CSS.

### 6.5. `BookingCTA.tsx`
* **Diseño:** Sección de alto impacto visual envuelta en gradiente radial de Azul Zafiro (`#0F3D56`) a `#082231`, con borde exterior cian fluorescente.
* **Interacción:** Permite al paciente seleccionar fecha rápida o abrir el chat de WhatsApp con un mensaje pre-armado.

### 6.6. `Footer.tsx`
* **Contenido:**
  - Ubicación física de Lumina Dental Studio y teléfono de emergencias.
  - Horarios de atención clínica (09:00 a 19:00 hs).
  - **Descargo Médico Obligatorio:** *"La información provista por nuestros canales de IA es orientativa y no reemplaza la evaluación clínica odontológica presencial."*
  - Enlace al `/dashboard` administrativo para el personal.

---

## 7. Inyección de Renders 3D (Nano Bana2): Ubicaciones y Dimensiones

```
┌────────────────────────────────────────────────────────────────────────────┐
│ NAVBAR (Sticky Glassmorphism)                                             │
├─────────────────────────────────────┬──────────────────────────────────────┤
│ HERO (Text, Badges, CTAs)           │ [RENDER 1: MASCOTA DENTAL 3D]        │
│                                     │ Aspect Ratio: 1:1 (Square)           │
│                                     │ Contenedor: max-w-[480px]            │
│                                     │ Fondo: Glow radial Cian #00E5FF      │
├─────────────────────────────────────┴──────────────────────────────────────┤
│ FEATURES (4 Pilares en Tarjetas Glassmorphism)                             │
├────────────────────────────────────────────────────────────────────────────┤
│ OMNICHANNEL MOCKUP SECTION                                                 │
│ [RENDER 2: ARTE CONCEPTUAL OMNICANAL 3D]                                   │
│ Aspect Ratio: 16:9 (Widescreen)                                            │
│ Contenedor: max-w-[960px] con chat bubbles flotantes superpuestas         │
├────────────────────────────────────────────────────────────────────────────┤
│ BOOKING CTA & CALENDAR PICKER                                              │
├────────────────────────────────────────────────────────────────────────────┤
│ FOOTER & AVISO ÉTICO SANITARIO                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### 7.1. Render 3D #1: Mascota Dental "Lumi" (Nano Bana2)
* **Ubicación Exacta:** Componente `Hero.tsx`, columna derecha (`lg:col-span-5`).
* **Aspect Ratio:** **`1:1` (Cuadrado estricto)**.
* **Dimensiones CSS:**
  - Desktop (`lg`): `w-full max-w-[460px] aspect-square mx-auto`.
  - Tablet (`md`): `w-[360px] aspect-square mx-auto`.
  - Mobile: `w-[280px] aspect-square mx-auto mb-6`.
* **Resolución Recomendada del Render:** `1024 x 1024 px` (WebP optimizado, < 180 KB).
* **Dirección de Arte para Nano Bana2:**
  > *"Personaje 3D de un diente estilizado, moderno y amigable llamado Lumi. Acabado de porcelana translúcida suave con reflejos sutiles, ojos expresivos tiernos, portando un pequeño visor holográfico o halo flotante en cian brillante (#00E5FF). Iluminación de estudio cinematográfica con luz de recorte sapphire (#0F3D56). Fondo transparente 100% (PNG/RGBA). Render 8k estilo Pixar/Blender."*
* **Contenedor Glass & Fallback:**
  ```tsx
  <div className="relative w-full max-w-[460px] aspect-square mx-auto flex items-center justify-center">
    {/* Radial Glow */}
    <div className="absolute inset-0 bg-gradient-to-tr from-[#00E5FF]/20 to-[#0F3D56]/40 rounded-full blur-3xl -z-10" />
    <Image
      src="/images/3d/lumina-mascot-3d.webp"
      alt="Lumi - Asistente Dental 3D de Lumina Dental Studio"
      width={1024}
      height={1024}
      priority
      className="w-full h-full object-contain drop-shadow-[0_20px_40px_rgba(0,229,255,0.25)] animate-float"
    />
  </div>
  ```

### 7.2. Render 3D #2: Arte Conceptual Omnicanal "Lumina Core" (Nano Bana2)
* **Ubicación Exacta:** Componente `OmniChannelMockup.tsx`, pieza central de fondo tras la maqueta interactiva.
* **Aspect Ratio:** **`16:9` (Widescreen)** o alternativa `3:2`.
* **Dimensiones CSS:**
  - Desktop (`lg`): `w-full max-w-[960px] aspect-[16/9] mx-auto rounded-3xl`.
  - Mobile: `w-full aspect-[16/9] rounded-2xl`.
* **Resolución Recomendada del Render:** `1920 x 1080 px` (WebP progresivo, < 260 KB).
* **Dirección de Arte para Nano Bana2:**
  > *"Arte conceptual isométrico 3D de un núcleo de comunicación dental futurista. Un cristal dental geométrico central brillante en zafiro (#0F3D56) del que emergen haces de luz y partículas de datos en cian brillante (#00E5FF) que se conectan a nodos flotantes transparentes que representan WhatsApp, mensajes y calendarios. Iluminación volumétrica dramática sobre fondo oscuro limpio y pulcro. Estilo minimalista de alta tecnología médica."*
* **Integración en la Maqueta:**
  ```tsx
  <div className="relative w-full max-w-5xl mx-auto aspect-[16/9] rounded-3xl overflow-hidden border border-white/15 shadow-2xl bg-gradient-to-b from-[#0F3D56]/30 to-[#082231]">
    {/* 3D Conceptual Background */}
    <Image
      src="/images/3d/omnichannel-core-3d.webp"
      alt="Núcleo Omnicanal Inteligente de Lumina Dental Studio"
      fill
      className="object-cover opacity-60 mix-blend-luminosity hover:opacity-80 transition duration-700"
    />
    {/* Floating Glassmorphism Message Overlays */}
    <div className="absolute inset-0 p-6 md:p-12 flex flex-col justify-between pointer-events-none">
      {/* Dynamic interactive overlay elements */}
    </div>
  </div>
  ```

---

## 8. Contratos de Datos y Tipado Estricto (TypeScript)

Archivo [`frontend/src/types/landing.ts`](file:///c:/Users/herct/Desktop/agentere/frontend/src/types/landing.ts):

```typescript
export interface NavItem {
  label: string;
  href: string;
}

export interface FeatureItem {
  id: string;
  title: string;
  description: string;
  icon: string;
  tag: string;
  highlightColor?: string;
}

export interface MetricItem {
  value: string;
  label: string;
  detail: string;
}

export interface TestimonialItem {
  patient: string;
  treatment: string;
  comment: string;
  rating: number;
}
```

---

## 9. Límites y Fronteras de Implementación (Boundaries)

* **Siempre:**
  - Mantener contraste accesible en todos los botones y títulos según WCAG 2.1 AA.
  - Colocar atributos `alt` descriptivos y `width`/`height` explícitos en imágenes para prevenir Layout Shift (CLS).
  - Utilizar clases de Tailwind semánticas extendidas en `tailwind.config.js`.
* **Consultar primero:**
  - Modificar la estructura de rutas existentes (`/dashboard` vs `/`).
  - Instalar dependencias pesadas de animación (e.g. Three.js o Framer Motion si Tailwind + CSS nativo pueden resolverlo de forma liviana).
* **Nunca:**
  - Utilizar gradientes violetas/índigo genéricos típicos de plantillas de IA.
  - Dejar cajas de imágenes rotas sin placeholder o fallback visual.
  - Prescribir dosis farmacológicas en textos de la landing.

---

## 10. Plan de Verificación de la Landing Page

1. **Compilación y Tipado:**
   - `npm run typecheck` reporta 0 errores.
   - `npm run build` genera las páginas estáticas optimizadas en < 3s.
2. **Navegación y Responsividad:**
   - Verificar en resoluciones de 320px (móvil pequeño), 768px (tablet), 1024px (laptop) y 1440px (desktop).
3. **Comprobación de Renders 3D:**
   - Contenedores con `aspect-square` y `aspect-[16/9]` renderizan sin deformar ni generar CLS.
