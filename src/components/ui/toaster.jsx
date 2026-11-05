import * as React from 'react';
import { CheckCircle2, AlertTriangle, Info, X } from 'lucide-react';
import { cn } from '../../lib/utils';

const ToastContext = React.createContext({ toast: () => {} });

export function ToastProvider({ children }) {
  const [toasts, setToasts] = React.useState([]);

  const toast = React.useCallback(({ title, description, variant = 'default' }) => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, title, description, variant }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3200);
  }, []);

  const dismiss = (id) => setToasts((prev) => prev.filter((t) => t.id !== id));

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-[100] flex flex-col gap-2 w-full max-w-sm pointer-events-none px-4">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={cn(
              'pointer-events-auto flex items-start gap-2.5 rounded-lg border p-3 shadow-xl backdrop-blur-xl text-xs transition-all',
              t.variant === 'destructive'
                ? 'border-rose-500/50 bg-rose-950/90 text-rose-100'
                : 'border-border bg-card/95 text-card-foreground'
            )}
          >
            {t.variant === 'destructive' ? (
              <AlertTriangle className="h-4 w-4 text-rose-400 shrink-0 mt-0.5" />
            ) : (
              <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
            )}
            <div className="flex-1">
              {t.title && <div className="font-semibold">{t.title}</div>}
              {t.description && <div className="text-muted-foreground mt-0.5">{t.description}</div>}
            </div>
            <button onClick={() => dismiss(t.id)} className="opacity-60 hover:opacity-100 cursor-pointer">
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  return React.useContext(ToastContext);
}

