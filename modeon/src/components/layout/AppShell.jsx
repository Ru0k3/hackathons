// src/components/layout/AppShell.jsx
import Sidebar from './Sidebar';
import ToastContainer from '@/components/ui/ToastContainer';

export default function AppShell({ children }) {
  return (
    <div className="flex min-h-screen bg-canvas">
      <Sidebar />
      {/* Spacer matches collapsed sidebar width */}
      <div className="w-[76px] flex-shrink-0" aria-hidden="true" />
      <main className="flex-1 min-w-0">
        {children}
      </main>
      <ToastContainer />
    </div>
  );
}
