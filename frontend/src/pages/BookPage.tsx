import { useParams, useNavigate } from 'react-router-dom';
import { useBook } from '@/hooks/use-books';
import { useQuery } from '@tanstack/react-query';
import { getBookInsights, getSimilarBooks } from '@/lib/api';
import { BookCover } from '@/components/books/BookCover';
import { BookCarousel } from '@/components/books/BookCarousel';
import { LoadingState } from '@/components/common/LoadingState';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { BookOpen, MessageSquare, Star, FileText, Lightbulb, Target, Layers } from 'lucide-react';

export function BookPage() {
  const { bookId } = useParams<{ bookId: string }>();
  const navigate = useNavigate();
  const id = Number(bookId);
  const { data: book, isLoading } = useBook(id);
  const { data: insights } = useQuery({
    queryKey: ['insights', id],
    queryFn: () => getBookInsights(id).then((r) => r.data),
    enabled: !!id,
  });
  const { data: similar } = useQuery({
    queryKey: ['similar', id],
    queryFn: () => getSimilarBooks(id).then((r) => r.data),
    enabled: !!id,
  });

  if (isLoading) return <LoadingState />;
  if (!book) return <div>Book not found</div>;

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="flex flex-col gap-8 md:flex-row">
        <div className="w-48 shrink-0">
          <BookCover bookId={book.id} coverPath={book.cover_path} title={book.title} className="aspect-[2/3] w-full shadow-lg" />
        </div>
        <div className="flex-1 space-y-4">
          <div>
            <h1 className="text-3xl font-bold">{book.title}</h1>
            <p className="text-lg text-muted-foreground">{book.author || 'Unknown Author'}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge>{book.processing_status}</Badge>
            {book.language && <Badge variant="outline">{book.language}</Badge>}
            {book.page_count && <Badge variant="outline">{book.page_count} pages</Badge>}
            {book.rating && (
              <Badge variant="outline" className="flex items-center gap-1">
                <Star className="h-3 w-3 fill-yellow-500 text-yellow-500" />
                {book.rating}
              </Badge>
            )}
          </div>
          {book.description && (
            <p className="text-sm text-muted-foreground line-clamp-4">{book.description}</p>
          )}
          <div className="flex gap-3">
            <Button onClick={() => navigate(`/reader/${book.id}`)}>
              <BookOpen className="mr-2 h-4 w-4" />
              Read
            </Button>
            <Button variant="outline" onClick={() => navigate(`/chat?book=${book.id}`)}>
              <MessageSquare className="mr-2 h-4 w-4" />
              Chat with Book
            </Button>
          </div>
        </div>
      </div>

      {/* Insights Tabs */}
      {insights && (insights.concepts.length > 0 || insights.frameworks.length > 0 || insights.takeaways.length > 0) && (
        <Tabs defaultValue="concepts">
          <TabsList>
            <TabsTrigger value="concepts" className="flex items-center gap-1">
              <Lightbulb className="h-4 w-4" />
              Concepts ({insights.concepts.length})
            </TabsTrigger>
            <TabsTrigger value="frameworks" className="flex items-center gap-1">
              <Layers className="h-4 w-4" />
              Frameworks ({insights.frameworks.length})
            </TabsTrigger>
            <TabsTrigger value="takeaways" className="flex items-center gap-1">
              <Target className="h-4 w-4" />
              Takeaways ({insights.takeaways.length})
            </TabsTrigger>
          </TabsList>
          <TabsContent value="concepts" className="grid gap-4 md:grid-cols-2">
            {insights.concepts.map((i: any) => (
              <Card key={i.id}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">{i.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{i.content}</p>
                  {i.supporting_quote && (
                    <blockquote className="mt-2 border-l-2 border-primary pl-3 text-xs italic text-muted-foreground">
                      &ldquo;{i.supporting_quote}&rdquo;
                    </blockquote>
                  )}
                </CardContent>
              </Card>
            ))}
          </TabsContent>
          <TabsContent value="frameworks" className="grid gap-4 md:grid-cols-2">
            {insights.frameworks.map((i: any) => (
              <Card key={i.id}>
                <CardHeader className="pb-2"><CardTitle className="text-base">{i.title}</CardTitle></CardHeader>
                <CardContent><p className="text-sm text-muted-foreground">{i.content}</p></CardContent>
              </Card>
            ))}
          </TabsContent>
          <TabsContent value="takeaways" className="space-y-3">
            {insights.takeaways.map((i: any) => (
              <Card key={i.id}>
                <CardContent className="flex items-start gap-3 p-4">
                  <Target className="h-5 w-5 shrink-0 text-primary mt-0.5" />
                  <div>
                    <p className="font-medium">{i.title}</p>
                    <p className="text-sm text-muted-foreground mt-1">{i.content}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>
        </Tabs>
      )}

      {/* Similar Books */}
      {similar && similar.length > 0 && (
        <BookCarousel
          title="Similar Books"
          books={similar.map((s: any) => s.book)}
          subtitle="Based on content similarity"
        />
      )}
    </div>
  );
}
