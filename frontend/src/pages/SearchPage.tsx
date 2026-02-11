import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useSearch } from '@/hooks/use-search';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LoadingState } from '@/components/common/LoadingState';
import { EmptyState } from '@/components/common/EmptyState';
import { Search, BookOpen } from 'lucide-react';
import { Link } from 'react-router-dom';

export function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') || '');
  const { data, isLoading } = useSearch(query);

  useEffect(() => {
    if (query) setSearchParams({ q: query });
  }, [query]);

  return (
    <div className="space-y-6">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search books, concepts, passages..."
          className="h-12 pl-10 text-lg"
          autoFocus
        />
      </div>

      {isLoading && <LoadingState message="Searching..." />}

      {data && data.results.length === 0 && query && (
        <EmptyState icon={Search} title="No results" description={`No results found for "${query}"`} />
      )}

      {data && data.results.length > 0 && (
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">{data.total} results for &ldquo;{data.query}&rdquo;</p>
          {data.results.map((result: any) => (
            <Link key={result.chunk_id} to={`/book/${result.book_id}`}>
              <Card className="transition-colors hover:bg-accent">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <BookOpen className="h-4 w-4 text-primary" />
                        <span className="font-medium text-sm">{result.book_title}</span>
                        {result.book_author && (
                          <span className="text-xs text-muted-foreground">by {result.book_author}</span>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-3">{result.content}</p>
                      <div className="mt-2 flex gap-2">
                        {result.chapter && <Badge variant="outline" className="text-xs">{result.chapter}</Badge>}
                        {result.page_number && <Badge variant="outline" className="text-xs">p. {result.page_number}</Badge>}
                      </div>
                    </div>
                    <Badge variant="secondary" className="shrink-0">{(result.score * 100).toFixed(0)}%</Badge>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
