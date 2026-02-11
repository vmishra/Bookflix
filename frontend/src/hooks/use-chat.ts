import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getChatSessions, getChatMessages, createChatSession, sendChatMessage } from '@/lib/api';

export function useChatSessions() {
  return useQuery({
    queryKey: ['chat-sessions'],
    queryFn: () => getChatSessions().then((r) => r.data),
  });
}

export function useChatMessages(sessionId: number) {
  return useQuery({
    queryKey: ['chat-messages', sessionId],
    queryFn: () => getChatMessages(sessionId).then((r) => r.data),
    enabled: !!sessionId,
  });
}

export function useCreateChatSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { title?: string; book_ids?: number[] }) => createChatSession(data).then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['chat-sessions'] }),
  });
}

export function useSendMessage(sessionId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (content: string) => sendChatMessage(sessionId, content).then((r) => r.data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['chat-messages', sessionId] }),
  });
}
