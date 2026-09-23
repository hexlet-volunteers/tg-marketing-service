import {
  Box,
  Card,
  Badge,
  Container,
  Grid,
  SimpleGrid,
  Stack,
  Text,
  Title
} from "@mantine/core";
import { useNavigate } from "react-router-dom";
import SmallArticle from "@/components/ui/SmallArticle";
import type { BlogPageProps } from '@/types/article';
import { mockArticles } from "@/utils/addColors";

export default function BlogPage ({ articles = mockArticles }: BlogPageProps) {
  const navigate = useNavigate();

  return (
    <Container>
      <Stack gap="xl">
      <Box>
        <Title order={1}>Блог</Title>
        <Text c="dimmed">
          Как расти в Telegram: данные, AI и практика
        </Text>
      </Box>

        <Card withBorder padding={0} onClick={() => navigate('/blog/kak-ai-pomogaet-avtoram-rasti-v-2-raza-bystree')}>
          <Grid>
            <Grid.Col span={{ base: 12, md: 7 }}>
              <Box
                h={320}
                style={{
                  background:
                    "linear-gradient(135deg,var(--mantine-color-tgpurple-6),var(--mantine-color-tgblue-4))",
                }}
              />
            </Grid.Col>

            <Grid.Col span={{ base: 12, md: 5 }}>
              <Stack p="xl" justify="center" h="100%">
                <Badge w="fit-content">AI</Badge>

                <Title order={2}>
                  Как AI помогает авторам расти в 2 раза быстрее
                </Title>

                <Text c="dimmed">
                  Разбираем, как рекомендательные модели
                  подсказывают удачные темы постов и экономят
                  часы на планировании.
                </Text>

                <Text size="sm" c="dimmed">
                  28 июня 2026 • 6 мин
                </Text>
              </Stack>
            </Grid.Col>
          </Grid>
        </Card>

      <SimpleGrid cols={{ base: 1, md: 3 }}>
        {articles.map((article) => (
          <SmallArticle key={article.id} {...article} onClick={() => navigate(`/blog/${article.id}`)} />
        ))}
      </SimpleGrid>
      </Stack>
    </Container>
  );
}
