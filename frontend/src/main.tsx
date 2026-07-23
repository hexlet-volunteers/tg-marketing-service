import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@mantine/core/styles.css'
import App from './app/App.tsx'
import 'vite/modulepreload-polyfill'
// import { createInertiaApp } from '@inertiajs/react'
// import { InertiaProgress } from '@inertiajs/progress'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

// document.addEventListener('DOMContentLoaded', () => {
//   InertiaProgress.init();

//   createInertiaApp({
//     resolve: (name: string) => {
//       switch (name) {
//         case 'Home':
//           return import('./components/pages/LandingPage.tsx');
//         case 'Auth':
//           return import('./components/pages/Auth.tsx');
//         case 'ComparePages':
//           return import('./components/pages/ComparePage.tsx');
//         case 'CompareProducts':
//           return import('./components/pages/Co.tsx');
//         case 'MassParsing':
//           return import('./components/pages/Channels.tsx');
//         case 'PasswordRecovery':
//           return import('./components/modals/PasswordRecovery.tsx');

//         case 'Header':
//           return import('./components/Layout/Header.tsx');
//         case 'Layout':
//           return import('./components/Layout/Layout.tsx');
//         case 'FormRegistration':
//           return import('./components/ui/FormRegistration.tsx');
//         case 'Tooltip':
//           return import('./components/ui/Tooltip.tsx');

//         default: throw new Error(`Page ${name} not found`);
//       }
//     },
//     setup({ el, App, props }) {
//       const root = createRoot(el);
//       root.render(<App {...props} />);
//     },
//   });
// });
