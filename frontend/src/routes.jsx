import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Assistant } from './pages/Assistant';
import { ReviewQueue } from './pages/ReviewQueue';
import { Invoices } from './pages/Invoices';
import { InvoiceDetail } from './pages/InvoiceDetail';
import { Dashboard } from './pages/Dashboard';
import { AuditLog } from './pages/AuditLog';
import { Upload } from './pages/Upload';
import { Settings } from './pages/Settings';

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Assistant />} />
      <Route path="/queue" element={<ReviewQueue />} />
      <Route path="/invoices" element={<Invoices />} />
      <Route path="/invoices/:id" element={<InvoiceDetail />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/audit" element={<AuditLog />} />
      <Route path="/upload" element={<Upload />} />
      <Route path="/settings" element={<Settings />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
