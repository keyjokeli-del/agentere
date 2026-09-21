import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Lumina Dental Studio | Odontología de Precisión & Asistente IA 24/7",
  description: "Atención odontológica de alta precisión y agendamiento inteligente 24/7 en WhatsApp, Facebook, Instagram y YouTube.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className="scroll-smooth">
      <body className="antialiased min-h-screen bg-sapphire-950 text-slate-100 selection:bg-cyan-bright selection:text-sapphire-950">
        {children}
      </body>
    </html>
  );
}
