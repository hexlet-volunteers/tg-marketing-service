
interface IdeaData {
  title: string;
  reason: string;
  scope: number;
  date: string;
}

interface Idea extends IdeaData {
  icon: React.ElementType;
}

interface InsightData {
  type: 'recommendation' | 'trend' | 'warning' | 'positive';
  text: string;
}

interface Insight extends InsightData {
  icon: React.ElementType;
  color: 'green' | 'blue' | 'orange' | 'purple';
}

interface Competitor {
  name: string;
  er: number;
  delta: number;
}

type HeatMapData = Record<string, Record<number, number>>

interface AskAIAboutChannelProps {
 quickQuestions: string[];
}

interface BestTimeToPostProps {
 daysOfWeek: string[];
 hours: number[];
 heatMapData: HeatMapData;
}

interface CompetitorsProps {
 competitors: Competitor[];
}

interface WeeklyInsightsProps {
    insights: Insight[];
}

interface InsightsEmptyStateProps {
  variant: "all-read" | "no-insights";
}

type EmptyStateVariant = "all-read" | "no-insights";

interface WhatToWriteAboutProps {
 ideas: Idea[];
}

interface AiCabinetPageProps {
  ideas: IdeaData[];
  insights: InsightData[];
  competitors: Competitor[];
  heatMapData: HeatMapData;
}

export type { IdeaData, Idea, Competitor, InsightData, Insight, HeatMapData, AskAIAboutChannelProps, BestTimeToPostProps, CompetitorsProps, WeeklyInsightsProps, InsightsEmptyStateProps, EmptyStateVariant,  WhatToWriteAboutProps, AiCabinetPageProps }
