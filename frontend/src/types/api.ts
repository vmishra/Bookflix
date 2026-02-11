export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface LibraryStats {
  total_books: number;
  processed_books: number;
  pending_books: number;
  total_chunks: number;
  total_insights: number;
}

export interface ReadingProgress {
  id: number;
  book_id: number;
  current_page: number;
  total_pages: number | null;
  progress_percent: number;
  status: string;
  total_read_time: number;
  last_read_at: string | null;
  epub_cfi: string | null;
}

export interface ReadingStats {
  total_read_time_seconds: number;
  total_read_time_hours: number;
  books_completed: number;
  books_reading: number;
}

export interface TopicNode {
  id: number;
  name: string;
  book_count: number;
  color: string | null;
}

export interface TopicEdge {
  source: number;
  target: number;
  strength: number;
}

export interface TopicGraph {
  nodes: TopicNode[];
  edges: TopicEdge[];
}
