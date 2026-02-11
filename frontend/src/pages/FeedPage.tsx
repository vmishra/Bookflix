import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getFeed, updateFeedItem, generateFeed } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { LoadingState } from '@/components/common/LoadingState';
import { EmptyState } from '@/components/common/EmptyState';
import { Newspaper, Lightbulb, Link2, Quote, RefreshCw, Pin, Check } from 'lucide-react';
import { toast } from 'sonner';

const typeIcons: Record<string, any> = {
  til: Lightbulb,
  connection: Link2,
  quote: Quote,
  concept: Lightbulb,
  recommendation: Newspaper,
};

export function FeedPage() {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ['feed'],
    queryFn: () => getFeed().then((r) => r.data),
  });

  const markRead = useMutation({
    mutationFn: (id: number) => updateFeedItem(id, { is_read: true }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['feed'] }),
  });

  const togglePin = useMutation({
    mutationFn: (item: any) => updateFeedItem(item.id, { is_pinned: !item.is_pinned }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['feed'] }),
  });

  const generate = useMutation({
    mutationFn: () => generateFeed(),
    onSuccess: () => {
      toast.success('Feed generation started');
      queryClient.invalidateQueries({ queryKey: ['feed'] });
    },
  });

  if (isLoading) return <LoadingState />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Your Feed</h1>
          {data && <p className="text-sm text-muted-foreground">{data.unread_count} unread items</p>}
        </div>
        <Button variant="outline" onClick={() => generate.mutate()} disabled={generate.isPending}>
          <RefreshCw className={`mr-2 h-4 w-4 ${generate.isPending ? 'animate-spin' : ''}`} />
          Generate New
        </Button>
      </div>

      {(!data || data.items.length === 0) ? (
        <EmptyState
          icon={Newspaper}
          title="Your feed is empty"
          description="Feed items will appear as your books are processed"
          action={{ label: 'Generate Feed', onClick: () => generate.mutate() }}
        />
      ) : (
        <div className="space-y-4">
          {data.items.map((item: any) => {
            const Icon = typeIcons[item.item_type] || Lightbulb;
            return (
              <Card key={item.id} className={item.is_read ? 'opacity-60' : ''}>
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <Icon className="h-5 w-5 shrink-0 text-primary mt-1" />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium">{item.title}</h3>
                        <Badge variant="outline" className="text-xs">{item.item_type}</Badge>
                        {item.is_pinned && <Pin className="h-3 w-3 text-primary" />}
                      </div>
                      <p className="text-sm text-muted-foreground">{item.content}</p>
                      <div className="mt-2 flex gap-2">
                        {!item.is_read && (
                          <Button variant="ghost" size="sm" onClick={() => markRead.mutate(item.id)}>
                            <Check className="mr-1 h-3 w-3" /> Mark Read
                          </Button>
                        )}
                        <Button variant="ghost" size="sm" onClick={() => togglePin.mutate(item)}>
                          <Pin className="mr-1 h-3 w-3" /> {item.is_pinned ? 'Unpin' : 'Pin'}
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
