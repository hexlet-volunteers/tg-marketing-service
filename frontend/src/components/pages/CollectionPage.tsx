import CollectionChannelCard from "@/components/ui/CollectionChannelCard";
import {
    Container,
    Group,
    Paper,
    SimpleGrid,
    Stack,
    Text,
    Title
} from "@mantine/core";
import { IconChevronLeft } from "@tabler/icons-react";
import { useNavigate } from "react-router-dom";
import type { CollectionPageProps } from "@/types/channel";
import { mockCollection } from "@/utils/addColors";

export default function CollectionPage({ channels = mockCollection }: CollectionPageProps) {
    const navigate = useNavigate();

    return (
        <Container>
            <Stack gap="xl">
            <Group gap={4} style={{ cursor: 'pointer' }} onClick={() => navigate('/collections')}>
                <IconChevronLeft
                    size={14}
                    color="gray"
                />

                <Text size="sm" c="dimmed">
                    Все подборки
                </Text>
            </Group>

            <Paper
                p={32}
                style={{
                    background:
                        "linear-gradient(90deg,var(--mantine-color-tgblue-5),var(--mantine-color-tgpurple-6))",
                }}
            >
                <Stack gap="sm">
                    <Title order={1} c="white">
                        Топ IT-каналов
                    </Title>

                    <Text c="rgba(255,255,255,.9)">
                        Технологии, разработка и цифровые
                        продукты
                    </Text>

                    <Text
                        c="rgba(255,255,255,.8)"
                        fw={600}
                    >
                        3 канала
                    </Text>
                </Stack>
            </Paper>

            <SimpleGrid
                cols={{ base: 1, md: 3 }}
                spacing="lg"
            >
                {channels.map((channel) => (
                    <CollectionChannelCard
                        key={channel.name}
                        {...channel}
                    />
                ))}
            </SimpleGrid>
            </Stack>
        </Container>
    );
}
