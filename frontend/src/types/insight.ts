export interface Insight {
  id: number;
  book_id: number;
  insight_type: string;
  title: string;
  content: string;
  supporting_quote: string | null;
  importance: number;
  refinement_level: number;
  created_at: string;
}

export interface BookInsights {
  book_id: number;
  concepts: Insight[];
  frameworks: Insight[];
  takeaways: Insight[];
}
