import { useParams, useNavigate } from 'react-router-dom';
import { useBook } from '@/hooks/use-books';
import { useUpdateReadingProgress } from '@/hooks/use-reading';
import { useState, useCallback, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Settings } from 'lucide-react';
import { LoadingState } from '@/components/common/LoadingState';
import { getBookFileUrl } from '@/lib/api';

export function ReaderPage() {
  const { bookId } = useParams<{ bookId: string }>();
  const navigate = useNavigate();
  const id = Number(bookId);
  const { data: book, isLoading } = useBook(id);
  const updateProgress = useUpdateReadingProgress(id);
  const [currentPage, setCurrentPage] = useState(1);

  const handlePageChange = useCallback(
    (page: number, total?: number) => {
      setCurrentPage(page);
      updateProgress.mutate({ current_page: page, total_pages: total });
    },
    [updateProgress]
  );

  if (isLoading) return <LoadingState />;
  if (!book) return <div>Book not found</div>;

  const fileType = book.files?.[0]?.file_type || 'pdf';
  const fileUrl = getBookFileUrl(id);

  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Toolbar */}
      <header className="flex h-12 items-center justify-between border-b bg-card px-4">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => navigate(`/book/${id}`)}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-sm font-medium line-clamp-1">{book.title}</h1>
            <p className="text-xs text-muted-foreground">Page {currentPage}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon">
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </header>

      {/* Reader Content */}
      <div className="flex-1 overflow-auto">
        {fileType === 'pdf' ? (
          <div className="flex h-full items-center justify-center">
            <iframe
              src={fileUrl}
              className="h-full w-full"
              title={book.title}
            />
          </div>
        ) : (
          <div className="flex h-full items-center justify-center">
            <iframe
              src={fileUrl}
              className="h-full w-full"
              title={book.title}
            />
          </div>
        )}
      </div>
    </div>
  );
}
