import React, { useState } from "react";
import { Button, Group, TextInput, UnstyledButton } from "@mantine/core";
import { IconSend } from "@tabler/icons-react";

import { SectionCard } from "@/components/ui/SectionCard";

import type { AskAIAboutChannelProps } from "@/types/aiCabinet";

const AskAIAboutChannel: React.FC<AskAIAboutChannelProps> = ({
 quickQuestions,
}) => {
 const [questionText, setQuestionText] = useState("");

 return (
  <SectionCard title="Спросить AI о канале">
   <Group gap="xs" mb="md" wrap="wrap">
    {quickQuestions.map((q) => (
     <Button
      key={q}
      variant="light"
      color="tgpurple"
      onClick={() => setQuestionText(q)}
     >
      {q}
     </Button>
    ))}
   </Group>
   <TextInput
    placeholder="Задайте вопрос..."
    value={questionText}
    onChange={(e) => setQuestionText(e.currentTarget.value)}
    rightSection={
     <UnstyledButton
      onClick={() => {
       if (questionText.trim()) {
        setQuestionText("");
       }
      }}
     >
      <IconSend size={16} color="var(--mantine-color-tgpurple-5)" />
     </UnstyledButton>
    }
   />
  </SectionCard>
 );
};

export default AskAIAboutChannel;
