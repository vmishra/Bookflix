import { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { getConfig, updateConfig, getModels, setModel } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useAppStore } from '@/stores/app-store';
import { Settings, Moon, Sun, Cpu, Sliders } from 'lucide-react';
import { toast } from 'sonner';

export function SettingsPage() {
  const { darkMode, toggleDarkMode } = useAppStore();
  const { data: config } = useQuery({ queryKey: ['config'], queryFn: () => getConfig().then((r) => r.data) });
  const { data: models } = useQuery({ queryKey: ['models'], queryFn: () => getModels().then((r) => r.data) });
  const [newModel, setNewModel] = useState('');

  const updateMutation = useMutation({
    mutationFn: (data: any) => updateConfig(data),
    onSuccess: () => toast.success('Config updated'),
  });

  const setModelMutation = useMutation({
    mutationFn: ({ taskType, modelId }: { taskType: string; modelId: string }) => setModel(taskType, modelId),
    onSuccess: () => toast.success('Model updated'),
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>

      {/* Appearance */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            {darkMode ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
            Appearance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Button variant="outline" onClick={toggleDarkMode}>
            {darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          </Button>
        </CardContent>
      </Card>

      {/* LLM Models */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Cpu className="h-5 w-5" />
            LLM Models
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {models?.current && Object.entries(models.current).map(([task, model]: any) => (
            <div key={task} className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">{task}</p>
                <p className="text-xs text-muted-foreground">{model}</p>
              </div>
              <Badge variant="outline">{task}</Badge>
            </div>
          ))}
          <div className="flex gap-2 pt-2 border-t">
            <Input
              placeholder="openai/gpt-4o or anthropic/claude-3.5-sonnet"
              value={newModel}
              onChange={(e) => setNewModel(e.target.value)}
            />
            <Button
              variant="secondary"
              onClick={() => {
                if (newModel) {
                  setModelMutation.mutate({ taskType: 'default', modelId: newModel });
                  setNewModel('');
                }
              }}
            >
              Set Default
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Config Info */}
      {config && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Sliders className="h-5 w-5" />
              Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-muted-foreground">Books Path</span><span>{config.books_path}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Embedding Model</span><span>{config.embedding_model}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Orchestrator</span><Badge variant="outline">{config.orchestrator_intensity}</Badge></div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
