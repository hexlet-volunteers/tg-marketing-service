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

export type { Channel, ChannelsProps };
