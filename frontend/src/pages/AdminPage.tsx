import {
  Avatar,
  Badge,
  Box,
  Button,
  Container,
  Group,
  Paper,
  ScrollArea,
  Select,
  Table,
  Tabs,
  Text,
  ThemeIcon,
  Title,
} from "@mantine/core";
import {
  IconShield,
} from "@tabler/icons-react";
import type { UserRequestProps } from "@/types/user";
import { mockUserRequests } from "@/utils/addColors";

export default function AdminPage({ userRequests = mockUserRequests }: UserRequestProps ) {
  return (
    <Container>
      <Group mb={8}>
        <ThemeIcon color="tgorange" radius="md">
          <IconShield size={18} />
        </ThemeIcon>

        <Title order={1}>Админка</Title>
      </Group>

      <Text c="dimmed" mb={28}>
        Только для администраторов сервиса · модерация заявок
        пользователей, каналов, статей и подборок
      </Text>

      <Tabs defaultValue="moderation" mb="xl">
        <Tabs.List>
          <Tabs.Tab
            value="moderation"
            rightSection={
              <Badge color="tgorange" size="xs">
                4
              </Badge>
            }
          >
            Модерация
          </Tabs.Tab>

          <Tabs.Tab value="channels">Каналы и группы</Tabs.Tab>

          <Tabs.Tab value="posts">Статьи блога</Tabs.Tab>

          <Tabs.Tab value="collections">Подборки</Tabs.Tab>
        </Tabs.List>
      </Tabs>

      <Paper radius="lg" withBorder>
        <Box p="lg">
          <Title order={4}>Заявки от пользователей</Title>

          <Text size="sm" c="dimmed">
            Каналы и группы, которые добавили сами пользователи.
            Назначьте категорию и одобрите публикацию.
          </Text>
        </Box>

        <ScrollArea p="xs">
          <Table highlightOnHover verticalSpacing="md">
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Канал</Table.Th>
                <Table.Th>Кто добавил</Table.Th>
                <Table.Th>Категория</Table.Th>
                <Table.Th ta="right">Действие</Table.Th>
              </Table.Tr>
            </Table.Thead>

            <Table.Tbody>
              {userRequests.map((userRequest) => (
                <Table.Tr key={userRequest.title}>
                  <Table.Td>
                    <Group>
                      <Avatar color={userRequest.color}>
                        {userRequest.title.slice(0, 2).toUpperCase()}
                      </Avatar>

                      <Box>
                        <Text fw={600}>{userRequest.title}</Text>
                        <Text size="sm" c="dimmed">
                          {userRequest.username}
                        </Text>
                      </Box>
                    </Group>
                  </Table.Td>

                  <Table.Td>
                    <Text>{userRequest.author}</Text>

                    <Text size="sm" c="dimmed">
                      {userRequest.time}
                    </Text>
                  </Table.Td>

                  <Table.Td w={220}>
                    <Select
                      defaultValue={userRequest.category}
                      data={[
                        "Технологии",
                        "Маркетинг",
                        "Крипта",
                        "Дизайн",
                      ]}
                    />
                  </Table.Td>

                  <Table.Td>
                    <Group>
                      <Button color="tggreen">Одобрить</Button>

                      <Button variant="outline" color="tgred">
                        Отклонить
                      </Button>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </ScrollArea>
      </Paper>
    </Container>
  );
}
