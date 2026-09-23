interface Channel {
  id: number;
  name: string;
  username: string;
  type: 'channel' | 'group';
  subscribers: number;
  category: string;
  verified: boolean;
  country: string;
  imageUrl: string;
  er: number;
  growth30d: number;
}

interface ChannelsProps {
  channels: Channel[];
}

type MainCharactersOfChannel = Pick<Channel, 'name' | 'username' | 'subscribers' | 'er' | 'growth30d'> 

interface MainCharactersOfChannelAndColor extends MainCharactersOfChannel {
  color: string
}

interface CollectionPageProps {
  channels: MainCharactersOfChannelAndColor[]
}

interface Kpi {
  label: string;
  value: number;
  delta?: number;
  percentDelta?: number;
  positive: boolean;
}

interface GrowthSubscribersData {
  date: string;
  подписчики: number;
}

interface ChannelData {
  kpis: Kpi[];
  growthData: GrowthSubscribersData[];
}

interface MetricDef {
  key: string;
  label: string;
  format: (v: number) => string;
}

interface ComparePageProps {
  metrics: MetricDef[];
  channels: Channel[]
}

export type { Channel, 
  ChannelsProps, 
  Kpi, 
  GrowthSubscribersData, 
  ChannelData, 
  MetricDef, 
  ComparePageProps,
  MainCharactersOfChannel,
  MainCharactersOfChannelAndColor,
  CollectionPageProps 
};
