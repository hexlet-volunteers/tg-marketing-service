import React, { useState } from "react";
import {
 Badge,
 Button,
 Container,
 Group,
 Paper,
 Progress,
 SimpleGrid,
 Stack,
 Text,
 Title,
 ThemeIcon,
 Anchor,
 List,
 Alert,
 Skeleton,
 Loader,
} from "@mantine/core";
import { InsightCard } from "@/components/ui/InsightCard";
import { IconArrowLeft, IconSparkles, IconBrain } from "@tabler/icons-react";
import { useNavigate } from "react-router-dom";
import { mockReactions, MOCK_ANALYSIS_DATA } from "@/shared/mocks/posts";
import type { PostPageProps, PostAnalysis } from "@/types/post";

const PostPage: React.FC<PostPageProps> = ({
 reactions = mockReactions,
 analysis: propAnalysis = MOCK_ANALYSIS_DATA,
}) => {
 const navigate = useNavigate();

 const [analysis, setAnalysis] = useState<PostAnalysis | null>(null);

 const handleStartAnalysis = () => {
  const baseData = propAnalysis || MOCK_ANALYSIS_DATA;

  setAnalysis({
   ...baseData,
   status: "processing",
  });

  setTimeout(() => {
   setAnalysis({
    ...baseData,
    status: "completed",
   });
  }, 3000);
 };

 return (
  <Container>
   <Button
    variant="subtle"
    color="tgblue"
    leftSection={<IconArrowLeft size={16} />}
    mb="md"
    onClick={() => navigate(-1)}
   >
    Назад к каналу
   </Button>

   <SimpleGrid cols={{ base: 1, lg: 2 }} spacing="lg" mb="lg">
    <Paper withBorder p="lg" radius="md">
     <Title order={3} mb="md">
      Обзор нового iPhone 16 Pro
     </Title>
     <Text size="sm" c="dimmed" mb="md">
      Apple представила новый iPhone 16 Pro с чипом A18 Pro, титановым корпусом
      и улучшенной камерой. Главные изменения: новый дизайн, увеличенный экран и
      поддержка Apple Intelligence.
     </Text>
     <Group gap="xs" mb="md">
      <Text size="xs" c="dimmed">
       #apple
      </Text>
      <Text size="xs" c="dimmed">
       #iphone
      </Text>
      <Text size="xs" c="dimmed">
       #tech
      </Text>
     </Group>
     <Group gap="lg">
      <Text size="sm">👁 42.1K</Text>
      <Text size="sm">❤️ 890</Text>
      <Text size="sm">↗ 234</Text>
      <Text size="sm">💬 45</Text>
     </Group>
    </Paper>

    <Paper withBorder p="lg" radius="md">
     <Title order={3} mb="md">
      Разбивка реакций
     </Title>
     <Stack>
      {reactions.map((r) => (
       <div key={r.label}>
        <Group justify="space-between" mb={4}>
         <Text size="sm">
          {r.emoji} {r.label}
         </Text>
         <Text size="xs" c="dimmed">
          {r.count} ({r.percent}%)
         </Text>
        </Group>
        <Progress value={r.percent} size="sm" radius="xl" color="tgblue" />
       </div>
      ))}
     </Stack>
     <Group justify="space-between" mt="md" pt="md" bd="1px solid gray.2">
      <Text fw={600}>ER</Text>
      <Badge size="lg" color="tggreen">
       31.2%
      </Badge>
     </Group>
    </Paper>
   </SimpleGrid>

   <Group gap="sm" mb="lg">
    <ThemeIcon
     size={26}
     variant="gradient"
     gradient={{ from: "tgblue", to: "tgpurple", deg: 135 }}
    >
     <IconSparkles size={18} />
    </ThemeIcon>
    <Title order={3}>AI-разбор поста</Title>
   </Group>

   {!analysis && (
    <Paper withBorder p="xl" radius="md" ta="center">
     <IconBrain
      size={40}
      stroke={1}
      style={{ marginBottom: 10, opacity: 0.5 }}
     />
     <Title order={4} mb="xs">
      Анализ не проведен
     </Title>
     <Button variant="light" onClick={handleStartAnalysis}>
      Запустить разбор
     </Button>
    </Paper>
   )}

   {analysis?.status === "processing" && (
    <Stack>
     <Alert
      icon={<Loader size="xs" />}
      title="Генерируем анализ..."
      color="blue"
     />
     <SimpleGrid cols={{ base: 1, md: 3 }} spacing="lg">
      <Skeleton height={140} radius="md" />
      <Skeleton height={140} radius="md" />
      <Skeleton height={140} radius="md" />
     </SimpleGrid>
    </Stack>
   )}

   {analysis?.status === "completed" && (
    <SimpleGrid cols={{ base: 1, md: 3 }} spacing="lg">
     <InsightCard color="green" label="Почему зашёл">
      <List size="sm" spacing="xs">
       {analysis.why_worked.map((item, i) => (
        <List.Item key={i}>{item}</List.Item>
       ))}
      </List>
     </InsightCard>

     <InsightCard color="orange" label="Что улучшить">
      <List size="sm" spacing="xs">
       {analysis.how_to_improve.map((item, i) => (
        <List.Item key={i}>{item}</List.Item>
       ))}
      </List>
     </InsightCard>

     <InsightCard color="purple" label="Похожие идеи">
      <Stack gap="xs">
       {analysis.similar_posts.map((post) => (
        <Anchor
         key={post.id}
         href={post.permalink}
         size="sm"
         target="_blank"
         display="block"
        >
         {post.text}
        </Anchor>
       ))}
      </Stack>
     </InsightCard>
    </SimpleGrid>
   )}
  </Container>
 );
};

export default PostPage;
