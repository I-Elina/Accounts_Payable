import React from 'react';
import { useLocation } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { AppRoutes } from './routes';
import { api } from './lib/api';
import { useApi } from './hooks/useApi';

const ROUTE_TITLES = {
  '/': 'Assistant',
  '/queue': 'Review Queue',
  '/invoices': 'Invoices',
  '/dashboard': 'Dashboard',
  '/audit': 'Audit Log',
  '/upload': 'Upload',
  '/settings': 'Settings',
};

export function App() {
  const location = useLocation();
  const { data: config } = useApi(api.getConfig);

  let pageTitle = ROUTE_TITLES[location.pathname];
  if (!pageTitle) {
    if (location.pathname.startsWith('/invoices/')) {
      pageTitle = 'Invoice Detail';
    } else {
      pageTitle = 'Cache Me';
    }
  }

  const autoPassThreshold = config?.auto_pass_threshold || 0.85;

  return (
    <AppShell pageTitle={pageTitle} autoPassThreshold={autoPassThreshold}>
      <AppRoutes />
    </AppShell>
  );
}

export default App;
