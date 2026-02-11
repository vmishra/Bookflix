import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getLibraryStats, getProcessingStatus, scanLibrary, importBooks } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { LoadingState } from '@/components/common/LoadingState';
import { Library, FolderOpen, Upload, RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react';
import { toast } from 'sonner';

export function LibraryPage() {
  const queryClient = useQueryClient();
  const [scanPath, setScanPath] = useState('/books');

  const { data: stats } = useQuery({
    queryKey: ['library-stats'],
    queryFn: () => getLibraryStats().then((r) => r.data),
    refetchInterval: 10000,
  });

  const { data: processing } = useQuery({
    queryKey: ['processing-status'],
    queryFn: () => getProcessingStatus().then((r) => r.data),
    refetchInterval: 5000,
  });

  const scan = useMutation({
    mutationFn: () => scanLibrary(scanPath),
    onSuccess: (res) => {
      toast.success(`Scan started: ${res.data.task_id}`);
      queryClient.invalidateQueries({ queryKey: ['library-stats'] });
    },
    onError: () => toast.error('Scan failed'),
  });

  const doImport = useMutation({
    mutationFn: () => importBooks(scanPath),
    onSuccess: (res) => {
      toast.success(`Imported ${res.data.imported} books (${res.data.skipped} skipped)`);
      queryClient.invalidateQueries({ queryKey: ['library-stats'] });
    },
    onError: () => toast.error('Import failed'),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Library Management</h1>

      {/* Scan & Import */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FolderOpen className="h-5 w-5" />
            Scan & Import Books
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              value={scanPath}
              onChange={(e) => setScanPath(e.target.value)}
              placeholder="/path/to/books"
            />
            <Button onClick={() => scan.mutate()} disabled={scan.isPending}>
              {scan.isPending ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <FolderOpen className="mr-2 h-4 w-4" />}
              Scan
            </Button>
            <Button variant="secondary" onClick={() => doImport.mutate()} disabled={doImport.isPending}>
              <Upload className="mr-2 h-4 w-4" />
              Import
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-3xl font-bold">{stats.total_books}</p>
              <p className="text-sm text-muted-foreground">Total Books</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-3xl font-bold text-green-500">{stats.processed_books}</p>
              <p className="text-sm text-muted-foreground">Processed</p>
              {stats.total_books > 0 && (
                <Progress value={(stats.processed_books / stats.total_books) * 100} className="mt-2 h-2" />
              )}
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <p className="text-3xl font-bold text-yellow-500">{stats.pending_books}</p>
              <p className="text-sm text-muted-foreground">Pending</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Processing Status */}
      {processing && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Processing Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              {Object.entries(processing.status_counts || {}).map(([status, count]: any) => (
                <div key={status} className="flex items-center gap-2">
                  {status === 'completed' && <CheckCircle className="h-4 w-4 text-green-500" />}
                  {status === 'failed' && <XCircle className="h-4 w-4 text-red-500" />}
                  {status === 'pending' && <Clock className="h-4 w-4 text-yellow-500" />}
                  {status === 'running' && <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />}
                  <span className="text-sm">{status}: {count}</span>
                </div>
              ))}
            </div>
            {processing.recent_failures?.length > 0 && (
              <div className="mt-4 space-y-2">
                <h4 className="text-sm font-medium text-destructive">Recent Failures</h4>
                {processing.recent_failures.map((f: any) => (
                  <div key={f.id} className="rounded bg-destructive/10 p-2 text-xs">
                    Book #{f.book_id} - {f.stage}: {f.error}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
