import {
    Badge,
    Box,
    Card,
    Group,
    Stack,
    Text,
    Title
} from "@mantine/core";
import {
    IconStarFilled
} from "@tabler/icons-react";
import type { collections } from "../pages/CollectionsPage";



export default function CollectionCard(props: (typeof collections)[0] & { onClick?: () => void }) {
    return (
        <Card
            withBorder
            shadow="xs"
            p={0}
            style={{ overflow: "hidden" }}
            onClick={props.onClick}
        >
            <Box
                p="md"
                h={116}
                c="white"
                bg={props.gradient}
            >
                <Stack justify="space-between" h="100%">
                    {props.editorial ? (
                        <Badge
                            leftSection={<IconStarFilled size={10} />}
                            color="white"
                            variant="filled"
                            c="var(--mantine-color-tgblue-5)"
                            w="fit-content"
                        >
                            Редакция
                        </Badge>
                    ) : (
                        <Box h={24} />
                    )}

                    <Title order={3} c="white">
                        {props.title}
                    </Title>
                </Stack>
            </Box>

            <Stack p="md" gap={10}>
                <Text c="dimmed" size="sm">
                    {props.description}
                </Text>

                <Group justify="space-between">
                    <Text size="sm" c="dimmed">
                        {props.author}
                    </Text>

                    <Text fw={600} c="tgblue">
                        {props.channels}{" "}
                        {props.channels === 1 ? "канал" : "канала"}
                    </Text>
                </Group>
            </Stack>
        </Card>
    );
}