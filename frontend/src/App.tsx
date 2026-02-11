import { Routes, Route } from 'react-router-dom';
import { AppShell } from '@/components/layout/AppShell';
import { HomePage } from '@/pages/HomePage';
import { BrowsePage } from '@/pages/BrowsePage';
import { BookPage } from '@/pages/BookPage';
import { ReaderPage } from '@/pages/ReaderPage';
import { SearchPage } from '@/pages/SearchPage';
import { ChatPage } from '@/pages/ChatPage';
import { FeedPage } from '@/pages/FeedPage';
import { TopicsPage } from '@/pages/TopicsPage';
import { KnowledgePage } from '@/pages/KnowledgePage';
import { LibraryPage } from '@/pages/LibraryPage';
import { SettingsPage } from '@/pages/SettingsPage';

export default function App() {
  return (
    <Routes>
      <Route path="/reader/:bookId" element={<ReaderPage />} />
      <Route element={<AppShell />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/browse" element={<BrowsePage />} />
        <Route path="/book/:bookId" element={<BookPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/chat/:sessionId" element={<ChatPage />} />
        <Route path="/feed" element={<FeedPage />} />
        <Route path="/topics" element={<TopicsPage />} />
        <Route path="/knowledge" element={<KnowledgePage />} />
        <Route path="/library" element={<LibraryPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}
