export interface SearchResult {
  chunk_id: number;
  book_id: number;
  book_title: string | null;
  book_author: string | null;
  content: string;
  page_number: number | null;
  chapter: string | null;
  score: number;
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
  total: number;
}
