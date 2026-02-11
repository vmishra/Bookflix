import { Link, useLocation } from 'react-router-dom';
import { Home, BookOpen, Search, MessageSquare, Library } from 'lucide-react';
import { cn } from '@/lib/utils';

const items = [
  { path: '/', icon: Home, label: 'Home' },
  { path: '/browse', icon: BookOpen, label: 'Browse' },
  { path: '/search', icon: Search, label: 'Search' },
  { path: '/chat', icon: MessageSquare, label: 'Chat' },
  { path: '/library', icon: Library, label: 'Library' },
];

export function MobileNav() {
  const location = useLocation();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 flex border-t bg-card md:hidden">
      {items.map((item) => (
        <Link
          key={item.path}
          to={item.path}
          className={cn(
            'flex flex-1 flex-col items-center gap-1 py-2 text-xs',
            location.pathname === item.path ? 'text-primary' : 'text-muted-foreground',
          )}
        >
          <item.icon className="h-5 w-5" />
          <span>{item.label}</span>
        </Link>
      ))}
    </nav>
  );
}
