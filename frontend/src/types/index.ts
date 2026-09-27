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
  delivery_status?: 'sent' | 'delivered' | 'read' | string;
  latency_ms?: number;
  urgency?: 'RUTINA' | 'MODERADO' | 'URGENCIA' | string;
  handoff_active?: boolean;
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

export interface ChannelInboxMessage {
  id: string;
  role: 'user' | 'assistant';
  sender_name?: string;
  agent?: string;
  intent?: string;
  content: string;
  timestamp: string;
  status?: string;
  is_internal?: boolean;
  audio_url?: string | null;
  image_url?: string | null;
  vision_analysis?: string | null;
  rag_trace?: string[] | null;
  sla_seconds?: number;
}

export interface ChannelInboxThread {
  sender_id: string;
  patient_name: string;
  channel: string;
  last_activity: string;
  message_count: number;
  patient_memory?: string | null;
  messages: ChannelInboxMessage[];
  fdi_teeth?: string[];
  urgency?: 'high' | 'normal';
  crm_stage?: string;
  sla_seconds?: number;
  unread_count?: number;
  is_ai_paused?: boolean;
  cross_channels?: string[];
}

export interface ChannelInboxData {
  channel: string;
  title: string;
  total_messages: number;
  active_threads: number;
  last_message: {
    sender_id: string;
    patient_name: string;
    content: string;
    role: string;
    timestamp: string;
  } | null;
  threads: ChannelInboxThread[];
}

