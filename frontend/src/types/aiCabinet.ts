
interface IdeaData {
  title: string;
  reason: string;
  scope: number;
  date: string;
}

interface Idea extends IdeaData {
  icon: React.ElementType;
}

interface Ideas {
  ideas: Idea[]
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

interface AiCabinetPageProps extends Ideas {
  insights: Insight[];
  competitors: Competitor[];
  heatMapData: HeatMapData;
}

export type { IdeaData, Idea, Competitor, InsightData, Insight, HeatMapData, AiCabinetPageProps }
