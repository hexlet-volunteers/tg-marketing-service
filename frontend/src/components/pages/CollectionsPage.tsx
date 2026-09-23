import {
  Box,
  Container,
  SimpleGrid,
  Stack,
  Text,
  Title
} from "@mantine/core";
import { useNavigate } from "react-router-dom";
import CollectionCard from "../ui/CollectionCard";
import type { CollectionsPageProps } from "@/types/collection";
import { mockCollections } from "@/utils/addColors";

export default function CollectionsPage({ collections = mockCollections }: CollectionsPageProps) {
  const navigate = useNavigate();

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
        {collections.map((collection) => (
          <CollectionCard
            key={collection.id}
            {...collection}
            onClick={() => navigate(`/collections/${collection.id}`)}
          />
        ))}
      </SimpleGrid>
      </Stack>
    </Container>
  );
}
