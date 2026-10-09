import React from 'react';
import { Route, Routes } from 'react-router-dom';
import LandingPage from '@/pages/LandingPage';
import Channels from '@/pages/Channels';
import DashboardPage from '@/pages/DashboardPage';
import ComparePage from '@/pages/ComparePage';
import PostPage from '@/pages/PostPage';
import AICabinetPage from '@/pages/AICabinetPage';
import CollectionsPage from '@/pages/CollectionsPage';
import CollectionPage from '@/pages/CollectionPage';
import BlogPage from '@/pages/BlogPage';
import BlogPostPage from '@/pages/BlogPostPage';
import LegalPage from '@/pages/LegalPage';
import NotFoundPage from '@/pages/NotFoundPage';
import AdminPage from '@/pages/AdminPage';
import Auth from '@/pages/Auth';
import UserProfilePage from '@/pages/UserProfilePage';
import channelsCol from '@/shared/mocks/channelsCollection';
import { mockKpis, mockGrowthData } from '@/shared/mocks/channelKpis';
import {mockPosts, mockReactions} from '@/shared/mocks/posts';
import mockLegalContent from '@/shared/mocks/legalContent';
import { mockNotifications, mockUser } from '@/shared/mocks/user';
import { mockCompetitors, mockHeatMapData } from '@/shared/mocks/aiPageData';
import { mockIdeas, mockInsights } from '@/utils/makeIdeasAndInsights';
import { mockUserRequests, mockArticles, mockCollection, mockCollections } from "@/utils/addColors"
import { mockMetrics } from '@/shared/mocks/metrics';

export const knownPaths = ['/', '/channels', '/dashboard', '/compare', '/post', '/ai-cabinet', '/collections', '/blog', '/legal', '/admin', '/auth', '/profile'];

const routes = [
  { path: '/', element: <LandingPage /> },
  { path: '/channels', element: <Channels channels={channelsCol} /> },
  { path: '/dashboard', element: <DashboardPage kpis={mockKpis} growthData={mockGrowthData} posts={mockPosts}/> },
  { path: '/compare', element: <ComparePage metrics={mockMetrics} channels={channelsCol.slice(0, 3)}/> },
  { path: '/post', element: <PostPage reactions={mockReactions} /> },
  { path: '/ai-cabinet', element: <AICabinetPage 
    ideas={mockIdeas} 
    insights={mockInsights} 
    competitors={mockCompetitors} 
    heatMapData={mockHeatMapData}/> 
  },
  { path: '/collections', element: <CollectionsPage collections={mockCollections}/> },
  { path: '/collections/:id', element: <CollectionPage channels={mockCollection}/> },
  { path: '/blog', element: <BlogPage articles={mockArticles}/> },
  { path: '/blog/:slug', element: <BlogPostPage /> },
  { path: '/legal', element: <LegalPage legalContent={mockLegalContent}/> },
  { path: '/admin', element: <AdminPage userRequests={mockUserRequests}/> },
  { path: '/auth', element: <Auth /> },
  { path: '/profile', element: <UserProfilePage user={mockUser} notifications={mockNotifications}/> },
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
