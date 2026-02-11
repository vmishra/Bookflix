import { useQuery } from '@tanstack/react-query';
import { search, searchSuggest } from '@/lib/api';

export function useSearch(query: string, params?: Record<string, any>) {
  return useQuery({
    queryKey: ['search', query, params],
    queryFn: () => search(query, params).then((r) => r.data),
    enabled: query.length > 0,
  });
}

export function useSearchSuggest(query: string) {
  return useQuery({
    queryKey: ['search-suggest', query],
    queryFn: () => searchSuggest(query).then((r) => r.data),
    enabled: query.length > 1,
  });
}
