import { Search, Moon, Sun, Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useAppStore } from '@/stores/app-store';
import { useNavigate } from 'react-router-dom';

export function TopBar() {
  const { darkMode, toggleDarkMode, setSearchOpen } = useAppStore();
  const navigate = useNavigate();

  return (
    <header className="flex h-14 items-center justify-between border-b bg-card px-6">
      <div className="flex items-center gap-4">
        <Button
          variant="outline"
          className="w-64 justify-start text-muted-foreground"
          onClick={() => navigate('/search')}
        >
          <Search className="mr-2 h-4 w-4" />
          <span>Search books, concepts...</span>
          <kbd className="ml-auto rounded bg-muted px-1.5 py-0.5 text-xs">Ctrl+K</kbd>
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon">
          <Bell className="h-5 w-5" />
        </Button>
        <Button variant="ghost" size="icon" onClick={toggleDarkMode}>
          {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </Button>
      </div>
    </header>
  );
}
