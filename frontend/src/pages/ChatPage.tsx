import { useState, useRef, useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { useChatSessions, useChatMessages, useCreateChatSession, useSendMessage } from '@/hooks/use-chat';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { LoadingState } from '@/components/common/LoadingState';
import { EmptyState } from '@/components/common/EmptyState';
import { MessageSquare, Send, Plus, BookOpen } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export function ChatPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [searchParams] = useSearchParams();
  const bookId = searchParams.get('book');
  const [activeSession, setActiveSession] = useState<number | null>(sessionId ? Number(sessionId) : null);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: sessions } = useChatSessions();
  const { data: messages, isLoading: loadingMessages } = useChatMessages(activeSession || 0);
  const createSession = useCreateChatSession();
  const sendMessage = useSendMessage(activeSession || 0);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleNewChat = async () => {
    const session = await createSession.mutateAsync({
      title: 'New Chat',
      book_ids: bookId ? [Number(bookId)] : [],
    });
    setActiveSession(session.id);
  };

  const handleSend = async () => {
    if (!input.trim() || !activeSession) return;
    const msg = input;
    setInput('');
    await sendMessage.mutateAsync(msg);
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] gap-4">
      {/* Sessions sidebar */}
      <div className="w-64 shrink-0 space-y-2">
        <Button className="w-full" onClick={handleNewChat}>
          <Plus className="mr-2 h-4 w-4" />
          New Chat
        </Button>
        <ScrollArea className="h-[calc(100%-3rem)]">
          {sessions?.map((s: any) => (
            <button
              key={s.id}
              onClick={() => setActiveSession(s.id)}
              className={`w-full rounded-md px-3 py-2 text-left text-sm transition-colors ${
                activeSession === s.id ? 'bg-accent' : 'hover:bg-accent/50'
              }`}
            >
              <p className="font-medium line-clamp-1">{s.title}</p>
              <p className="text-xs text-muted-foreground">
                {new Date(s.updated_at).toLocaleDateString()}
              </p>
            </button>
          ))}
        </ScrollArea>
      </div>

      {/* Chat area */}
      <div className="flex flex-1 flex-col rounded-lg border bg-card">
        {!activeSession ? (
          <div className="flex flex-1 items-center justify-center">
            <EmptyState
              icon={MessageSquare}
              title="Start a conversation"
              description="Create a new chat or select an existing one"
              action={{ label: 'New Chat', onClick: handleNewChat }}
            />
          </div>
        ) : (
          <>
            <ScrollArea className="flex-1 p-4">
              {loadingMessages ? (
                <LoadingState />
              ) : (
                <div className="space-y-4">
                  {messages?.map((msg: any) => (
                    <div
                      key={msg.id}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[80%] rounded-lg px-4 py-2 ${
                        msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'
                      }`}>
                        <ReactMarkdown className="prose prose-sm dark:prose-invert max-w-none">
                          {msg.content}
                        </ReactMarkdown>
                        {msg.source_chunks?.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-1">
                            {msg.source_chunks.map((s: any, i: number) => (
                              <Badge key={i} variant="outline" className="text-xs">
                                <BookOpen className="mr-1 h-3 w-3" />
                                {s.book_title} p.{s.page_number}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </ScrollArea>

            <div className="border-t p-4">
              <div className="flex gap-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                  placeholder="Ask about your books..."
                  disabled={sendMessage.isPending}
                />
                <Button onClick={handleSend} disabled={!input.trim() || sendMessage.isPending}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
