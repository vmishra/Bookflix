export interface ChatSession {
  id: number;
  title: string;
  book_ids: number[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: number;
  session_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  source_chunks: SourceChunk[];
  model_used: string | null;
  created_at: string;
}

export interface SourceChunk {
  chunk_id: number;
  book_title: string | null;
  page_number: number | null;
  snippet: string;
}
