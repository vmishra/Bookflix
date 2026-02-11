export interface FeedItem {
  id: number;
  item_type: string;
  title: string;
  content: string;
  book_ids: number[];
  metadata_json: Record<string, any>;
  is_read: boolean;
  is_pinned: boolean;
  created_at: string;
}
