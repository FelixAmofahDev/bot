export interface Sentence {
  id: number;
  sentence_id: string;
  text: string;
  created_at: string;
}

export interface Participant {
  id: number;
  speaker_id: string;
  name: string;
  age: string;
  gender: string;
  region: string;
  telegram_id: number | null;
  created_at: string;
}

export interface Recording {
  id: number;
  speaker_id: string;
  telegram_id: number;
  sentence_id: number;
  sentence_code: string;
  twi_text: string;
  audio_path: string;
  created_at: string;
}

export interface DashboardStats {
  total_participants: number;
  total_recordings: number;
  total_sentences: number;
  total_completed: number;
  submitted_today: number;
}

export interface CompletionStat {
  speaker_id: string;
  recordings_count: number;
  completed_count: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  limit: number;
  offset: number;
}
