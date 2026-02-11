import { BookCard } from './BookCard';
import type { Book } from '@/types/book';

interface BookGridProps {
  books: Book[];
  showProgress?: boolean;
}

export function BookGrid({ books, showProgress }: BookGridProps) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
      {books.map((book) => (
        <BookCard key={book.id} book={book} showProgress={showProgress} />
      ))}
    </div>
  );
}
