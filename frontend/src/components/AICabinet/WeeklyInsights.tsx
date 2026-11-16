import React from "react";
import { Group, Stack, Text } from "@mantine/core";
import { InsightCard } from "@/components/ui/InsightCard";
import { SectionCard } from "@/components/ui/SectionCard";
import type { WeeklyInsightsProps } from "@/types/aiCabinet";

const WeeklyInsights: React.FC<WeeklyInsightsProps> = ({ insights }) => {
 return (
  <SectionCard title="Инсайты недели">
   <Stack gap="sm">
    {insights.map((ins, i) => (
     <InsightCard key={i} color={ins.color ?? "blue"}>
      <Group gap="xs">
       <ins.icon size={14} color={`var(--mantine-color-tg${ins.color}-6)`} />
       <Text size="sm">{ins.text}</Text>
      </Group>
     </InsightCard>
    ))}
   </Stack>
  </SectionCard>
 );
};

export default WeeklyInsights;
