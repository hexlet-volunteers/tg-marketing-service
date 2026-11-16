import React from "react";

import { Box, Grid, Group, Text, ScrollArea } from "@mantine/core";
import { SectionCard } from "../ui";
import getHeatColor from "@/utils/getHeatColor";
import type { BestTimeToPostProps } from "@/types/aiCabinet";

const BestTimeToPost: React.FC<BestTimeToPostProps> = ({
 daysOfWeek,
 hours,
 heatMapData,
}) => {
 return (
  <SectionCard title="Лучшее время для публикаций">
   <Text size="xs" c="dimmed" mb="sm">
    Тепловая карта активности подписчиков по дням и часам
   </Text>
   <ScrollArea>
    <Grid columns={16} gap={2} maw={580}>
     <Grid.Col span={1} />
     {hours
      .filter((h) => h >= 8 && h <= 22)
      .map((h) => (
       <Grid.Col key={h} span={1}>
        <Box ta="center" fz="10px" c="dimmed">
         {h}
        </Box>
       </Grid.Col>
      ))}
     {daysOfWeek.map((day) => (
      <React.Fragment key={day}>
       <Grid.Col span={1}>
        <Text fz="10px" c="dimmed">
         {day}
        </Text>
       </Grid.Col>
       {hours
        .filter((h) => h >= 8 && h <= 22)
        .map((h) => {
         const val = heatMapData[day]?.[h] ?? 0;
         return (
          <Grid.Col key={`${day}-${h}`} span={1}>
           <Box
            h={24}
            bdrs={3}
            bg={getHeatColor(val)}
            title={`${day} ${h}:00 — ${val > 0 ? `${val}/10 активность` : "нет данных"}`}
            style={{ aspectRatio: "1" }}
           />
          </Grid.Col>
         );
        })}
      </React.Fragment>
     ))}
    </Grid>
   </ScrollArea>
   <Group mt="sm" gap="xs">
    <Text size="xs" c="dimmed">
     Меньше
    </Text>
    {[0, 3, 5, 7, 9, 10].map((v) => (
     <Box key={v} w={12} h={12} bdrs={2} bg={getHeatColor(v)} />
    ))}
    <Text size="xs" c="dimmed">
     Больше
    </Text>
   </Group>
  </SectionCard>
 );
};

export default BestTimeToPost;
