import React from "react";
import {
 Badge,
 Button,
 Group,
 Paper,
 Stack,
 Text,
 ThemeIcon,
} from "@mantine/core";
import { SectionCard } from "../ui";
import { formatNumber } from "@/utils/formatNumberShort";
import type { WhatToWriteAboutProps } from "@/types/aiCabinet";

const WhatToWriteAboutThisWeek: React.FC<WhatToWriteAboutProps> = ({
 ideas,
}) => {
 return (
  <div>
   <SectionCard title="О чём написать на этой неделе">
    <Stack>
     {ideas.map((idea) => (
      <Paper key={idea.title} p="md">
       <Group gap="sm" mb="xs">
        <ThemeIcon size={28} color="tgpurple">
         <idea.icon size={16} />
        </ThemeIcon>
        <Text fw={700} size="sm">
         {idea.title}
        </Text>
       </Group>
       <Text size="xs" c="dimmed" mb="xs">
        {idea.reason}
       </Text>
       <Group justify="space-between">
        <Group gap="xs">
         <Badge size="xs" color="gray">
          {`~${formatNumber(idea.scope)} охват`}
         </Badge>
         <Badge size="xs" color="gray">
          {idea.date}
         </Badge>
        </Group>
        <Button
         size="xs"
         variant="filled"
         color="tgpurple"
         onClick={() => console.log("Write post:", idea.title)}
        >
         Написать
        </Button>
       </Group>
      </Paper>
     ))}
    </Stack>
   </SectionCard>
  </div>
 );
};

export default WhatToWriteAboutThisWeek;
