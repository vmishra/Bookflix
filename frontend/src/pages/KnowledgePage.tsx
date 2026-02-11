import { useQuery } from '@tanstack/react-query';
import { getKnowledgeConnections, getLearningPaths, getKnowledgeMap } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LoadingState } from '@/components/common/LoadingState';
import { EmptyState } from '@/components/common/EmptyState';
import { Brain, Link2, Map, GraduationCap } from 'lucide-react';

export function KnowledgePage() {
  const { data: connections } = useQuery({
    queryKey: ['knowledge-connections'],
    queryFn: () => getKnowledgeConnections().then((r) => r.data),
  });
  const { data: paths } = useQuery({
    queryKey: ['learning-paths'],
    queryFn: () => getLearningPaths().then((r) => r.data),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Second Brain</h1>

      <Tabs defaultValue="connections">
        <TabsList>
          <TabsTrigger value="connections">
            <Link2 className="mr-1 h-4 w-4" /> Connections
          </TabsTrigger>
          <TabsTrigger value="paths">
            <GraduationCap className="mr-1 h-4 w-4" /> Learning Paths
          </TabsTrigger>
          <TabsTrigger value="map">
            <Map className="mr-1 h-4 w-4" /> Knowledge Map
          </TabsTrigger>
        </TabsList>

        <TabsContent value="connections" className="space-y-4">
          {!connections || connections.length === 0 ? (
            <EmptyState icon={Link2} title="No connections yet" description="Cross-book connections are discovered as more books are processed" />
          ) : (
            connections.map((conn: any, i: number) => (
              <Card key={i}>
                <CardContent className="flex items-center gap-4 p-4">
                  <div className="flex-1 text-right">
                    <p className="font-medium text-sm">{conn.insight_a?.title}</p>
                    <p className="text-xs text-muted-foreground">{conn.insight_a?.book_title}</p>
                  </div>
                  <div className="flex flex-col items-center">
                    <Link2 className="h-5 w-5 text-primary" />
                    <span className="text-xs text-muted-foreground">{conn.connection_type}</span>
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-sm">{conn.insight_b?.title}</p>
                    <p className="text-xs text-muted-foreground">{conn.insight_b?.book_title}</p>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        <TabsContent value="paths" className="space-y-4">
          {!paths || paths.length === 0 ? (
            <EmptyState icon={GraduationCap} title="No learning paths yet" description="Learning paths are generated as your library grows" />
          ) : (
            paths.map((path: any) => (
              <Card key={path.id}>
                <CardHeader>
                  <CardTitle className="text-base">{path.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{path.description}</p>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>

        <TabsContent value="map">
          <Card className="flex h-96 items-center justify-center">
            <EmptyState icon={Brain} title="Knowledge Map" description="Interactive knowledge graph visualization (requires processed books with connections)" />
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
