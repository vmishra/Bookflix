import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getReadingProgress, updateReadingProgress, getReadingStats } from '@/lib/api';

export function useReadingProgress(bookId: number) {
  return useQuery({
    queryKey: ['reading-progress', bookId],
    queryFn: () => getReadingProgress(bookId).then((r) => r.data),
    enabled: !!bookId,
  });
}

export function useUpdateReadingProgress(bookId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => updateReadingProgress(bookId, data).then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['reading-progress', bookId] }),
  });
}

export function useReadingStats() {
  return useQuery({
    queryKey: ['reading-stats'],
    queryFn: () => getReadingStats().then((r) => r.data),
  });
}
