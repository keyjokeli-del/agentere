# Declaración de Intención: Sistema Multi-Agente para Clínica Dental

- **Outcome:** Sistema multi-agente omnicanal para clínica dental que atiende e interactúa en tiempo real en **WhatsApp (vía Baileys), Facebook, Instagram y YouTube**, respondiendo consultas odontológicas, orientando precios y agendando citas en **Google Calendar**.
- **User:** Personal y odontólogos de la clínica dental (para gestión de turnos, escaneo de QR de WhatsApp y supervisión desde el panel web) y pacientes (atención y reservas 24/7 en cualquier red social).
- **Why now:** Centralizar y automatizar la atención y captación de pacientes en todas las redes de la clínica simultáneamente sin costos operativos ni suscripciones de pago.
- **Success:** Un paciente escribe por WhatsApp, Facebook, Instagram o comenta en YouTube; el agente impulsado por Groq interpreta la consulta, verifica disponibilidad en tiempo real, agenda el turno en Google Calendar y confirma la cita, visualizándose en el panel web de Next.js.
- **Constraint:** **Costo $0 absoluto** (herramientas gratuitas: Groq API free tier, Baileys open-source, Google Cloud free quota para Calendar y YouTube Data API, Meta Developer free tier para FB/IG), desarrollado con **Python** (backend de agentes) y **Next.js** (frontend/dashboard).
- **Out of scope:** Servicios o herramientas de pago de terceros (Twilio, Zapier, Make, WABA de pago) y diagnósticos clínicos vinculantes (el agente brinda información, precios orientativos y agenda turnos, pero aclara que la evaluación médica definitiva se realiza en el consultorio).
