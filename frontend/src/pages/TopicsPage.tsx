import { useQuery } from '@tanstack/react-query';
import { getTopics, getTopicGraph } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LoadingState } from '@/components/common/LoadingState';
import { EmptyState } from '@/components/common/EmptyState';
import { Network, BookOpen } from 'lucide-react';
import { Link } from 'react-router-dom';

export function TopicsPage() {
  const { data: topics, isLoading } = useQuery({
    queryKey: ['topics'],
    queryFn: () => getTopics().then((r) => r.data),
  });

  if (isLoading) return <LoadingState />;
  if (!topics || topics.length === 0) {
    return <EmptyState icon={Network} title="No topics yet" description="Topics are generated automatically as books are processed" />;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Topics & Knowledge Graph</h1>

      {/* Topic Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {topics.map((topic: any) => (
          <Link key={topic.id} to={`/topics/${topic.id}`}>
            <Card className="transition-colors hover:bg-accent">
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div
                    className="h-4 w-4 rounded-full"
                    style={{ backgroundColor: topic.color || '#666' }}
                  />
                  <div>
                    <h3 className="font-medium">{topic.name}</h3>
                    <p className="text-xs text-muted-foreground flex items-center gap-1">
                      <BookOpen className="h-3 w-3" /> {topic.book_count} books
                    </p>
                  </div>
                </div>
                {topic.description && (
                  <p className="mt-2 text-sm text-muted-foreground line-clamp-2">{topic.description}</p>
                )}
                {topic.keywords?.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {topic.keywords.slice(0, 5).map((kw: string) => (
                      <Badge key={kw} variant="outline" className="text-xs">{kw}</Badge>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
