import type { Channel, GrowthSubscribersData, Kpi } from './channel';
import type { Post } from './post';

interface Insight {
  text: string;
  type: string;
  id?: number | null;
}

interface DashboardPageProps {
  channel: Channel;
  kpis: Kpi[];
  growthData: GrowthSubscribersData[];
  posts: Post[];
  ai_insights: Insight[];
}

export type { Insight, DashboardPageProps };
