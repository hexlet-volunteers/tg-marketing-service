import type React from "react";
import { Badge, Button, Group, Paper, Stack, Text, Title } from "@mantine/core";
import { router } from "@inertiajs/react";
import type { CompetitorsProps } from "@/types/aiCabinet";


const Competitors: React.FC<CompetitorsProps> = ({ competitors }) => {
 return (
  <div>
   <Paper p="lg">
    <Title order={3} mb="md">
     Конкуренты
    </Title>
    <Stack gap="sm">
     {competitors.map((c) => (
      <Group key={c.name} justify="space-between">
       <Text size="sm" fw={500}>
        {c.name}
       </Text>
       <Group gap="xs">
        <Text size="xs" c="dimmed">
         ER {c.er}%
        </Text>
        <Badge size="xs" color={c.delta >= 0 ? "green" : "red"}>
         {c.delta >= 0 ? "+" : ""}
         {c.delta}%
        </Badge>
       </Group>
      </Group>
     ))}
    </Stack>
    <Group mt="md" gap="sm">
     <Button
      size="xs"
      color="tgblue"
      onClick={() => console.log("Add competitor")}
     >
      + Добавить
     </Button>
     <Button
      size="xs"
      variant="subtle"
      color="tgblue"
      onClick={() => router.visit("/compare/")}
     >
      Сравнить все каналы
     </Button>
    </Group>
   </Paper>
  </div>
 );
};

export default Competitors;
