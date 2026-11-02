import { Badge, Box, Card, Stack, Text } from "@mantine/core";
import type { ArticleCard } from "@/types/article";
import formatArticleDate from "@/utils/formatArticleDate";

export default function SmallArticle({
  color,
  article,
  onClick,
}: {
  color: string;
  article: ArticleCard;
  onClick?: () => void;
}) {
  return (
    <Card withBorder radius="lg" padding={0} onClick={onClick} style={{ overflow: 'hidden' }}>
      <Box h={150} bg={color} />

      <Stack p="md" gap="xs">
        <Badge variant="light" w="fit-content">
          {article.category}
        </Badge>

        <Text fw={700} size="lg">
          {article.title}
        </Text>

        <Text c="dimmed" size="sm">
          {article.excerpt}
        </Text>

        <Text size="xs" c="dimmed">
          {formatArticleDate(article.published_at)} • {article.read_time} мин
        </Text>
      </Stack>
    </Card>
  );
}
