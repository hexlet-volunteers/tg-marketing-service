import { IconBulb, IconTrendingUp, IconAlertTriangle, IconThumbUp } from '@tabler/icons-react';
import type { IdeaData, Idea, InsightData, Insight } from '@/types/aiCabinet';

const iconsForIdeas: React.ElementType[] = [IconBulb, IconTrendingUp]

export const makeIdeas = (ideas: IdeaData[]): Idea[] => {
  return ideas.map((idea, index)  => {
    const assignedIcon = iconsForIdeas[index % iconsForIdeas.length];
    return { ...idea, icon: assignedIcon }
  })
}

export const makeInsights = (insights: InsightData[]): Insight[] => {
  return insights.map(insight => {
    switch(insight.type) {
      case 'recommendation':
        return { ...insight, icon: IconBulb, color: 'green' }
      case 'trend':
        return { ...insight, icon: IconTrendingUp, color: 'blue' }
      case 'warning':
        return { ...insight, icon: IconAlertTriangle, color: 'orange' }
      default:
        return { ...insight, icon: IconThumbUp, color: 'purple' }
    }
  })
}
