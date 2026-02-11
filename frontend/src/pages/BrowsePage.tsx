import { useState } from 'react';
import { useBooks } from '@/hooks/use-books';
import { BookGrid } from '@/components/books/BookGrid';
import { LoadingState } from '@/components/common/LoadingState';
import { EmptyState } from '@/components/common/EmptyState';
import { Button } from '@/components/ui/button';
import { BookOpen, Grid, List } from 'lucide-react';

export function BrowsePage() {
  const [page, setPage] = useState(0);
  const [sortBy, setSortBy] = useState('created_at');
  const { data, isLoading } = useBooks({ skip: page * 24, limit: 24, sort_by: sortBy, sort_order: 'desc' });

  if (isLoading) return <LoadingState message="Loading books..." />;
  if (!data || data.items.length === 0) {
    return <EmptyState icon={BookOpen} title="No books yet" description="Go to Library to scan and import your books." />;
  }

  const totalPages = Math.ceil(data.total / 24);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Browse Library</h1>
        <div className="flex gap-2">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="rounded-md border bg-background px-3 py-2 text-sm"
          >
            <option value="created_at">Date Added</option>
            <option value="title">Title</option>
            <option value="author">Author</option>
          </select>
        </div>
      </div>

      <BookGrid books={data.items} />

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button variant="outline" disabled={page === 0} onClick={() => setPage(page - 1)}>
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page + 1} of {totalPages}
          </span>
          <Button variant="outline" disabled={page >= totalPages - 1} onClick={() => setPage(page + 1)}>
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
