import {
  Box,
  Container,
  SimpleGrid,
  Stack,
  Text,
  Title
} from "@mantine/core";
import { router } from "@inertiajs/react";
import CollectionCard from "@/components/ui/CollectionCard";
import type {
  Collection,
  CollectionColor,
  CollectionWithColor,
  CollectionsPageProps
} from "@/types/collection";

const cardPalettes: CollectionColor[] = [
  { color: "var(--mantine-color-tgblue-5)",
    gradient: "linear-gradient(90deg,var(--mantine-color-tgblue-5),var(--mantine-color-tgpurple-6))" },
  { color: "var(--mantine-color-tgpurple-4)",
    gradient: "linear-gradient(90deg,var(--mantine-color-tgpurple-3),var(--mantine-color-tgpurple-6))" },
  { color: "var(--mantine-color-tgorange-5)",
    gradient: "linear-gradient(90deg,var(--mantine-color-tgorange-3),var(--mantine-color-tgorange-5))" },
  { color: "var(--mantine-color-tggreen-5)",
    gradient: "linear-gradient(90deg,var(--mantine-color-tggreen-3),var(--mantine-color-tggreen-5))" },
  { color: "var(--mantine-color-tggreen-6)",
    gradient: "linear-gradient(90deg,var(--mantine-color-tggreen-4),var(--mantine-color-tggreen-6))" },
  { color: "var(--mantine-color-tgblue-4)",
    gradient: "linear-gradient(90deg,var(--mantine-color-tgblue-3),var(--mantine-color-tgblue-5))" },
];

const toCardData = (collection: Collection, index: number): CollectionWithColor => ({
  id: collection.id,
  title: collection.name,
  description: collection.description ?? "",
  author: collection.curator ?? "",
  channels: collection.channel_count,
  editorial: collection.is_editorial,
  ...cardPalettes[index % cardPalettes.length],
});

export default function CollectionsPage({ collections }: CollectionsPageProps) {
  return (
    <Container>
      <Stack gap="xl">
      <Box>
        <Title order={1}>
          Подборки каналов
        </Title>

        <Text c="dimmed" mt={4}>
          Готовые тематические списки от редакции и
          авторов
        </Text>
      </Box>

      <SimpleGrid
        cols={{ base: 1, sm: 2, lg: 3 }}
        spacing="lg"
      >
        {collections.map((collection, index) => (
          <CollectionCard
            key={collection.id}
            {...toCardData(collection, index)}
            onClick={() => router.visit(`/collections/${collection.id}`)}
          />
        ))}
      </SimpleGrid>
      </Stack>
    </Container>
  );
}
