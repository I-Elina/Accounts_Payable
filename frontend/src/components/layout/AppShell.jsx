import React from 'react';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export function AppShell({ children, pageTitle = 'Assistant', autoPassThreshold = 0.85 }) {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-content">
        <Topbar pageTitle={pageTitle} autoPassThreshold={autoPassThreshold} />
        <main className="page-body">
          {children}
        </main>
      </div>
    </div>
  );
}
