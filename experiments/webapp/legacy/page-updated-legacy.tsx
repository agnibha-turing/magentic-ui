'use client';

import { useState, useEffect } from 'react';
import { AppUpdated } from '@/components/AppUpdated';
import { AppStateProvider } from '@/hooks/useAppStateContext';

export default function HomePage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-lg text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <AppStateProvider>
      <AppUpdated />
    </AppStateProvider>
  );
}
