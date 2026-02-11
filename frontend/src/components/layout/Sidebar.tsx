import { Link, useLocation } from 'react-router-dom';
import {
  Home, BookOpen, Search, MessageSquare, Newspaper,
  Network, Brain, Library, Settings, ChevronLeft, ChevronRight,
} from 'lucide-react';
import { useAppStore } from '@/stores/app-store';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

const navItems = [
  { path: '/', icon: Home, label: 'Home' },
  { path: '/browse', icon: BookOpen, label: 'Browse' },
  { path: '/search', icon: Search, label: 'Search' },
  { path: '/chat', icon: MessageSquare, label: 'Chat' },
  { path: '/feed', icon: Newspaper, label: 'Feed' },
  { path: '/topics', icon: Network, label: 'Topics' },
  { path: '/knowledge', icon: Brain, label: 'Knowledge' },
];

const bottomItems = [
  { path: '/library', icon: Library, label: 'Library' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export function Sidebar() {
  const location = useLocation();
  const { sidebarOpen, toggleSidebar } = useAppStore();

  return (
    <aside className={cn(
      'fixed left-0 top-0 z-40 flex h-screen flex-col border-r bg-card transition-all',
      sidebarOpen ? 'w-64' : 'w-16',
    )}>
      <div className="flex h-14 items-center justify-between px-4">
        {sidebarOpen && (
          <Link to="/" className="flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold text-primary">Bookflix</span>
          </Link>
        )}
        <Button variant="ghost" size="icon" onClick={toggleSidebar} className="ml-auto">
          {sidebarOpen ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        </Button>
      </div>

      <Separator />

      <nav className="flex-1 space-y-1 p-2">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={cn(
              'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent',
              location.pathname === item.path ? 'bg-accent text-accent-foreground' : 'text-muted-foreground',
              !sidebarOpen && 'justify-center px-2',
            )}
          >
            <item.icon className="h-5 w-5 shrink-0" />
            {sidebarOpen && <span>{item.label}</span>}
          </Link>
        ))}
      </nav>

      <Separator />

      <div className="space-y-1 p-2">
        {bottomItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={cn(
              'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-accent',
              location.pathname === item.path ? 'bg-accent text-accent-foreground' : 'text-muted-foreground',
              !sidebarOpen && 'justify-center px-2',
            )}
          >
            <item.icon className="h-5 w-5 shrink-0" />
            {sidebarOpen && <span>{item.label}</span>}
          </Link>
        ))}
      </div>
    </aside>
  );
}
