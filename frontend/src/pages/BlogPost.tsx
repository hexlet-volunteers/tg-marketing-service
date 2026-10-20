import {
    Anchor,
    Breadcrumbs,
    Button,
    Container,
    Group,
    Paper,
    Stack,
    Text,
    Title
} from "@mantine/core";
import {
    IconChevronLeft
} from "@tabler/icons-react";
import { router } from "@inertiajs/react";
import type { BlogPostProps } from "@/types/article";
import formatArticleDate from "@/utils/formatArticleDate";


const toParagraphs = (body: string): string[] =>
    body
        .split("\n\n")
        .map((block) => block.replace(/^#+\s*/, "").trim())
        .filter(Boolean);


export default function BlogPost(article: BlogPostProps) {
    const paragraphs = toParagraphs(article.body);

    return (
        <Container>
            <Stack gap="xl">
            <Breadcrumbs separator="">
                <Anchor
                    c="dimmed"
                    underline="never"
                    size="sm"
                    style={{ cursor: 'pointer' }}
                    onClick={() => router.visit('/blog/')}
                >
                    <Group gap={4}>
                        <IconChevronLeft size={14} />
                        <span>Все статьи</span>
                    </Group>
                </Anchor>

                <Text size="sm" c="tgblue" fw={600}>
                    {article.category}
                </Text>
            </Breadcrumbs>

            <Stack gap={6}>
                <Title order={1} maw={760}>
                    {article.title}
                </Title>

                <Text c="dimmed">
                    {formatArticleDate(article.published_at)} • {article.read_time} мин чтения
                </Text>
            </Stack>

            <Paper
                h={380}
                radius={20}
                bg={article.cover_image || undefined}
                style={{
                    background: article.cover_image
                        ? undefined
                        : "linear-gradient(135deg,var(--mantine-color-tgpurple-6),var(--mantine-color-tgblue-4))",
                }}
            />

            <Stack gap="lg">
                {paragraphs.map((paragraph) => (
                    <Text key={paragraph} size="lg" lh={1.8}>
                        {paragraph}
                    </Text>
                ))}
            </Stack>

            <Paper
                withBorder
                radius="xl"
                bg="tgblue.0"
                p="lg"
            >
                <Group justify="space-between" align="center">
                    <Stack gap={4}>
                        <Text fw={700} size="lg">
                            Хотите так же для своего канала?
                        </Text>

                        <Text c="dimmed">
                            AI-разбор покажет, о чём писать дальше
                        </Text>
                    </Stack>

                   <Button radius="md" onClick={() => router.visit(article.cta.url)}>
                       {article.cta.label}
                   </Button>
               </Group>
            </Paper>
            </Stack>
        </Container>
    );
}
