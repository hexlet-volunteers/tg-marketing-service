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
