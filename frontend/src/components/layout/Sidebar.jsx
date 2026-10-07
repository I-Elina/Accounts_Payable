import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  MessageSquare,
  ClipboardList,
  FileText,
  LayoutDashboard,
  History,
  UploadCloud,
  Sliders
} from 'lucide-react';

const NAV_ITEMS = [
  { path: '/', label: 'Assistant', icon: MessageSquare },
  { path: '/queue', label: 'Review Queue', icon: ClipboardList },
  { path: '/invoices', label: 'Invoices', icon: FileText },
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/audit', label: 'Audit Log', icon: History },
  { path: '/upload', label: 'Upload', icon: UploadCloud },
  { path: '/settings', label: 'Settings', icon: Sliders },
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo-icon">C</div>
        <div>
          <div className="sidebar-title">Cache Me</div>
          <div className="sidebar-subtitle">AP Exception Assistant</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              end={item.path === '/'}
            >
              <Icon className="nav-icon" />
              <span className="nav-text">{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div>v1.1 — Chat-First</div>
        <div>Microsoft Innovate 2026</div>
      </div>
    </aside>
  );
}
