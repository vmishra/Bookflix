import { BookOpen } from 'lucide-react';
import { cn } from '@/lib/utils';

interface BookCoverProps {
  bookId: number;
  coverPath: string | null;
  title: string;
  className?: string;
}

export function BookCover({ bookId, coverPath, title, className }: BookCoverProps) {
  if (coverPath) {
    return (
      <img
        src={`/api/v1/books/${bookId}/cover`}
        alt={title}
        className={cn('rounded-md object-cover', className)}
        loading="lazy"
      />
    );
  }

  // Placeholder cover with color based on title
  const hue = title.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0) % 360;
  return (
    <div
      className={cn('flex items-center justify-center rounded-md', className)}
      style={{ background: `hsl(${hue}, 40%, 25%)` }}
    >
      <div className="flex flex-col items-center p-2 text-center">
        <BookOpen className="h-8 w-8 text-white/60 mb-2" />
        <span className="text-xs font-medium text-white/80 line-clamp-3">{title}</span>
      </div>
    </div>
  );
}
