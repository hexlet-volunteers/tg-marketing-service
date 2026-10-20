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
import { router } from "@inertiajs/react";
import SmallArticle from "@/components/ui/SmallArticle";
import type { BlogPageProps } from '@/types/article';
import formatArticleDate from "@/utils/formatArticleDate";

const articleColors = [
  "var(--mantine-color-tgblue-5)",
  "var(--mantine-color-tggreen-5)",
  "var(--mantine-color-tgorange-5)",
];

export default function BlogPage({ featured, articles }: BlogPageProps) {
  return (
    <Container>
      <Stack gap="xl">
      <Box>
        <Title order={1}>Блог</Title>
        <Text c="dimmed">
          Как расти в Telegram: данные, AI и практика
        </Text>
      </Box>

        {featured && (
          <Card
            withBorder
            padding={0}
            onClick={() => router.visit(`/blog/${featured.slug}/`)}
          >
            <Grid>
              <Grid.Col span={{ base: 12, md: 7 }}>
                <Box
                  h={320}
                  bg={featured.cover_image || undefined}
                  style={{
                    background: featured.cover_image
                      ? undefined
                      : "linear-gradient(135deg,var(--mantine-color-tgpurple-6),var(--mantine-color-tgblue-4))",
                  }}
                />
              </Grid.Col>

              <Grid.Col span={{ base: 12, md: 5 }}>
                <Stack p="xl" justify="center" h="100%">
                  <Badge w="fit-content">{featured.category}</Badge>

                  <Title order={2}>
                    {featured.title}
                  </Title>

                  <Text c="dimmed">
                    {featured.excerpt}
                  </Text>

                  <Text size="sm" c="dimmed">
                    {formatArticleDate(featured.published_at)} • {featured.read_time} мин
                  </Text>
                </Stack>
              </Grid.Col>
            </Grid>
          </Card>
        )}

      <SimpleGrid cols={{ base: 1, md: 3 }}>
        {articles.map((article, index) => (
          <SmallArticle
            key={article.id}
            color={articleColors[index % articleColors.length]}
            article={article}
            onClick={() => router.visit(`/blog/${article.slug}/`)}
          />
        ))}
      </SimpleGrid>
      </Stack>
    </Container>
  );
}
