export type ChannelType = 'whatsapp' | 'facebook' | 'instagram' | 'youtube';

export interface Appointment {
  id: string;
  patient_name: string;
  contact: string;
  treatment: string;
  date: string;
  time: string;
  channel: ChannelType | string;
  status: 'confirmed' | 'pending' | 'cancelled' | string;
}

export interface Activity {
  id: string;
  channel: ChannelType | string;
  sender_id?: string;
  sender_name: string;
  message: string;
  reply: string;
  agent: string;
  intent: string;
  timestamp: string;
}

export interface WhatsAppStatus {
  status: 'connected' | 'waiting_for_scan' | 'connecting' | 'disconnected';
  user: string | null;
  hasQR: boolean;
  storage: 'neon_postgres' | 'local_disk';
  neonConfigured: boolean;
}

export interface WhatsAppQRResponse {
  qr: string | null;
  status: 'connected' | 'waiting_for_scan' | 'connecting' | 'disconnected';
  storage: 'neon_postgres' | 'local_disk';
}

export interface BackendHealth {
  status: string;
  clinic: string;
  channels: Record<string, string>;
  calendar: string;
  ai: string;
}

export interface SlotsResponse {
  date: string;
  slots: string[];
  total_available: number;
}

export interface ChatMessage {
  id: string;
  sender: string;
  text: string;
  isBot: boolean;
  channel?: ChannelType;
  agent?: string;
  intent?: string;
  timestamp: string;
}
