// src/main.jsx
import React             from 'react';
import ReactDOM          from 'react-dom/client';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools }  from '@tanstack/react-query-devtools';

import App              from './App';
import { queryClient } from './lib/queryClient';
import { initPostHog }  from './lib/posthog';
import './styles/globals.css';

// TODO (Backend): wire Supabase onAuthStateChange here
// import { supabase }    from './lib/supabase';
// import useAuthStore    from './stores/useAuthStore';
// supabase.auth.onAuthStateChange((_event, session) => {
//   useAuthStore.getState().setSession(session);
// });

initPostHog();

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  </React.StrictMode>
);
