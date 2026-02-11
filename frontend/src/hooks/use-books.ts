import { useQuery } from '@tanstack/react-query';
import { getBooks, getBook, getRecentBooks, getContinueReading } from '@/lib/api';

export function useBooks(params?: Record<string, any>) {
  return useQuery({
    queryKey: ['books', params],
    queryFn: () => getBooks(params).then((r) => r.data),
  });
}

export function useBook(id: number) {
  return useQuery({
    queryKey: ['book', id],
    queryFn: () => getBook(id).then((r) => r.data),
    enabled: !!id,
  });
}

export function useRecentBooks(limit = 10) {
  return useQuery({
    queryKey: ['books', 'recent', limit],
    queryFn: () => getRecentBooks(limit).then((r) => r.data),
  });
}

export function useContinueReading(limit = 10) {
  return useQuery({
    queryKey: ['books', 'continue-reading', limit],
    queryFn: () => getContinueReading(limit).then((r) => r.data),
  });
}
