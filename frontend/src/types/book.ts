export interface Book {
  id: number;
  title: string;
  author: string | null;
  isbn: string | null;
  description: string | null;
  publisher: string | null;
  published_date: string | null;
  language: string;
  page_count: number | null;
  file_hash: string;
  cover_path: string | null;
  processing_status: string;
  processing_progress: number;
  rating: number | null;
  created_at: string;
  updated_at: string;
}

export interface BookFile {
  id: number;
  file_path: string;
  file_type: 'pdf' | 'epub';
  file_size: number | null;
}

export interface BookDetail extends Book {
  files: BookFile[];
}
