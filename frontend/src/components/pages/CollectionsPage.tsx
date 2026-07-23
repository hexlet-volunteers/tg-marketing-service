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



export const collections = [
  {
    id: 1,
    title: "Топ IT-каналов",
    description: "Технологии, разработка и цифровые продукты",
    author: "Редакция tgpulse",
    channels: 3,
    color: "var(--mantine-color-tgblue-5)",
    gradient: "linear-gradient(90deg,var(--mantine-color-tgblue-5),var(--mantine-color-tgpurple-6))",
    editorial: true,
  },
  {
    id: 2,
    title: "Маркетинг и SMM",
    description: "Продвижение, реклама и контент",
    author: "Редакция tgpulse",
    channels: 1,
    color: "var(--mantine-color-tgpurple-4)",
    gradient: "linear-gradient(90deg,var(--mantine-color-tgpurple-3),var(--mantine-color-tgpurple-6))",
    editorial: true,
  },
  {
    id: 3,
    title: "Крипта без шума",
    description: "Аналитика рынка без хайпа",
    author: "@crypta_daily",
    channels: 1,
    color: "var(--mantine-color-tgorange-5)",
    gradient: "linear-gradient(90deg,var(--mantine-color-tgorange-3),var(--mantine-color-tgorange-5))",
  },
  {
    id: 4,
    title: "Стартапы и венчур",
    description: "Истории, разборы и деньги",
    author: "Редакция tgpulse",
    channels: 2,
    color: "var(--mantine-color-tggreen-5)",
    gradient: "linear-gradient(90deg,var(--mantine-color-tggreen-3),var(--mantine-color-tggreen-5))",
    editorial: true,
  },
  {
    id: 5,
    title: "Дизайн и продукт",
    description: "UX, UI и продуктовое мышление",
    author: "@design_kitchen",
    channels: 2,
    color: "var(--mantine-color-tggreen-6)",
    gradient: "linear-gradient(90deg,var(--mantine-color-tggreen-4),var(--mantine-color-tggreen-6))",
  },
  {
    id: 6,
    title: "Финансы и инвестиции",
    description: "Личные финансы и рынки",
    author: "Редакция tgpulse",
    channels: 2,
    color: "var(--mantine-color-tgblue-4)",
    gradient: "linear-gradient(90deg,var(--mantine-color-tgblue-3),var(--mantine-color-tgblue-5))",
    editorial: true,
  },
];




export default function CollectionsPage() {
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