import { IconBulb, IconTrendingUp, IconAlertTriangle, IconThumbUp } from '@tabler/icons-react';
import type { IdeaData, Idea, InsightData, Insight } from '@/types/aiCabinet';
import { mockIdeasData, mockInsightsData } from '@/shared/mocks/aiPageData';

const iconsForIdeas: React.ElementType[] = [IconBulb, IconTrendingUp]

const makeIdea = (iconsForIdeas: React.ElementType[], mockIdeasData: IdeaData[]): Idea[] => {
  return mockIdeasData.map((idea, index)  => {
    const assignedIcon = iconsForIdeas[index % iconsForIdeas.length];
    return { ...idea, icon: assignedIcon }
  })
}

const makeInsights = (mockInsightsData: InsightData[]): Insight[] => {
  return mockInsightsData.map(insight => {
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

export const mockIdeas = makeIdea(iconsForIdeas, mockIdeasData)
export const mockInsights = makeInsights(mockInsightsData)