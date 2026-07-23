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
import { useNavigate } from "react-router-dom";



export default function BlogPostPage() {
    const navigate = useNavigate();

    return (
        <Container>
            <Stack gap="xl">
            <Breadcrumbs separator="">
                <Anchor
                    c="dimmed"
                    underline="never"
                    size="sm"
                    style={{ cursor: 'pointer' }}
                    onClick={() => navigate('/blog')}
                >
                    <Group gap={4}>
                        <IconChevronLeft size={14} />
                        <span>Все статьи</span>
                    </Group>
                </Anchor>

                <Text size="sm" c="tgblue" fw={600}>
                    AI
                </Text>
            </Breadcrumbs>

            <Stack gap={6}>
                <Title order={1} maw={760}>
                    Как AI помогает авторам расти в 2 раза быстрее
                </Title>

                <Text c="dimmed">
                    28 июня 2026 • 6 мин чтения
                </Text>
            </Stack>

            <Paper
                h={380}
                radius={20}
                bg="linear-gradient(135deg,var(--mantine-color-tgpurple-6),var(--mantine-color-tgblue-4))"
            />

            <Stack gap="lg">
                <Text size="lg" lh={1.8}>
                    Это демонстрационная статья блога tgpulse.
                    Здесь мы подробно разбираем тему и
                    показываем, как сервис помогает авторам
                    принимать решения на основе данных, а не
                    интуиции.
                </Text>

                <Text size="lg" lh={1.8}>
                    Ключевая идея: смотреть не на абсолютные
                    цифры, а на динамику и вовлечённость.
                    AI-модель сервиса подсказывает, какие
                    форматы и темы работают именно у вашей
                    аудитории.
                </Text>

                <Text size="lg" lh={1.8}>
                    В следующих материалах разберём конкретные
                    кейсы и покажем, как за месяц вырастить
                    охват без накруток и агрессивной рекламы.
                </Text>
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

                    <Button radius="md">
                        Разобрать канал
                    </Button>
                </Group>
            </Paper>
            </Stack>
        </Container>
    );
}