import React from 'react';
import { Route, Routes } from 'react-router-dom';
import LandingPage from '@/components/pages/LandingPage';
import Channels from '@/components/pages/Channels';
import DashboardPage from '@/components/pages/DashboardPage';
import ComparePage from '@/components/pages/ComparePage';
import PostPage from '@/components/pages/PostPage';
import AICabinetPage from '@/components/pages/AICabinetPage';
import CollectionsPage from '@/components/pages/CollectionsPage';
import CollectionPage from '@/components/pages/CollectionPage';
import BlogPage from '@/components/pages/BlogPage';
import BlogPostPage from '@/components/pages/BlogPostPage';
import LegalPage from '@/components/pages/LegalPage';
import NotFoundPage from '@/components/pages/NotFoundPage';
import AdminPage from '@/components/pages/AdminPage';
import Auth from '@/components/pages/Auth';
import UserProfilePage from '@/pages/UserProfilePage/ui/UserProfilePage';
import channelsCol from '@/fixtures/channelsCollection';

export const knownPaths = ['/', '/channels', '/dashboard', '/compare', '/post', '/ai-cabinet', '/collections', '/blog', '/legal', '/admin', '/auth', '/profile'];

const routes = [
  { path: '/', element: <LandingPage /> },
  { path: '/channels', element: <Channels channels={channelsCol} /> },
  { path: '/dashboard', element: <DashboardPage /> },
  { path: '/compare', element: <ComparePage /> },
  { path: '/post', element: <PostPage /> },
  { path: '/ai-cabinet', element: <AICabinetPage /> },
  { path: '/collections', element: <CollectionsPage /> },
  { path: '/collections/:id', element: <CollectionPage /> },
  { path: '/blog', element: <BlogPage /> },
  { path: '/blog/:slug', element: <BlogPostPage /> },
  { path: '/legal', element: <LegalPage /> },
  { path: '/admin', element: <AdminPage /> },
  { path: '/auth', element: <Auth /> },
  { path: '/profile', element: <UserProfilePage /> },
  { path: '*', element: <NotFoundPage /> },
];

export const renderRoutes = (): React.ReactNode => {
  return (
    <Routes>
      {routes.map((route) => (
        <Route
          key={route.path}
          path={route.path}
          element={route.element}
        />
      ))}
    </Routes>
  );
};

export default routes;
