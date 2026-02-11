import { Link } from 'react-router-dom';
import { BookCover } from './BookCover';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import type { Book } from '@/types/book';

interface BookCardProps {
  book: Book;
  showProgress?: boolean;
  progress?: number;
}

export function BookCard({ book, showProgress, progress }: BookCardProps) {
  return (
    <Link to={`/book/${book.id}`} className="group block">
      <div className="relative overflow-hidden rounded-lg transition-transform group-hover:scale-105">
        <BookCover
          bookId={book.id}
          coverPath={book.cover_path}
          title={book.title}
          className="aspect-[2/3] w-full"
        />
        {book.processing_status !== 'completed' && (
          <Badge
            variant="secondary"
            className="absolute right-2 top-2 text-xs"
          >
            {book.processing_status}
          </Badge>
        )}
      </div>
      <div className="mt-2">
        <h3 className="line-clamp-1 text-sm font-medium group-hover:text-primary transition-colors">
          {book.title}
        </h3>
        <p className="line-clamp-1 text-xs text-muted-foreground">{book.author || 'Unknown Author'}</p>
        {showProgress && progress !== undefined && progress > 0 && (
          <Progress value={progress} className="mt-1 h-1" />
        )}
      </div>
    </Link>
  );
}
