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
import { router } from "@inertiajs/react";
import type { CollectionPageProps } from "@/types/channel";

export default function Collection({
    title,
    description,
    channel_count,
    channels,
}: CollectionPageProps) {
    const channelWord = channel_count === 1 ? "канал" : "канала";

    return (
        <Container>
            <Stack gap="xl">
            <Group gap={4} style={{ cursor: 'pointer' }} onClick={() => router.visit('/collections/')}>
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
                        {title}
                    </Title>

                    <Text c="rgba(255,255,255,.9)">
                        {description}
                    </Text>

                    <Text
                        c="rgba(255,255,255,.8)"
                        fw={600}
                    >
                        {channel_count} {channelWord}
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
