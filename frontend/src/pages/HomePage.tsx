import { useRecentBooks, useContinueReading } from '@/hooks/use-books';
import { useQuery } from '@tanstack/react-query';
import { getRecommendations, getFeed, getLibraryStats } from '@/lib/api';
import { BookCarousel } from '@/components/books/BookCarousel';
import { LoadingState } from '@/components/common/LoadingState';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BookOpen, Brain, Lightbulb, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { Book } from '@/types/book';

export function HomePage() {
  const { data: recentBooks, isLoading: loadingRecent } = useRecentBooks(12);
  const { data: continueReading } = useContinueReading(10);
  const { data: recommendations } = useQuery({
    queryKey: ['recommendations'],
    queryFn: () => getRecommendations(12).then((r) => r.data),
  });
  const { data: stats } = useQuery({
    queryKey: ['library-stats'],
    queryFn: () => getLibraryStats().then((r) => r.data),
  });

  if (loadingRecent) return <LoadingState message="Loading your library..." />;

  return (
    <div className="space-y-8">
      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <Card>
            <CardContent className="flex items-center gap-3 p-4">
              <BookOpen className="h-8 w-8 text-primary" />
              <div>
                <p className="text-2xl font-bold">{stats.total_books}</p>
                <p className="text-xs text-muted-foreground">Total Books</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center gap-3 p-4">
              <Brain className="h-8 w-8 text-blue-500" />
              <div>
                <p className="text-2xl font-bold">{stats.processed_books}</p>
                <p className="text-xs text-muted-foreground">Processed</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center gap-3 p-4">
              <Lightbulb className="h-8 w-8 text-yellow-500" />
              <div>
                <p className="text-2xl font-bold">{stats.total_insights}</p>
                <p className="text-xs text-muted-foreground">Insights</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="flex items-center gap-3 p-4">
              <Clock className="h-8 w-8 text-green-500" />
              <div>
                <p className="text-2xl font-bold">{stats.pending_books}</p>
                <p className="text-xs text-muted-foreground">Pending</p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Continue Reading */}
      {continueReading && continueReading.length > 0 && (
        <BookCarousel title="Continue Reading" books={continueReading} subtitle="Pick up where you left off" />
      )}

      {/* Recently Added */}
      {recentBooks && recentBooks.length > 0 && (
        <BookCarousel title="Recently Added" books={recentBooks} />
      )}

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <BookCarousel title="Recommended for You" books={recommendations} subtitle="Based on your reading history" />
      )}
    </div>
  );
}
