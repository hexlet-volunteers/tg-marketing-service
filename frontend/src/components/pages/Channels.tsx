import {
  Button,
  Container,
  Group,
  SegmentedControl,
  SimpleGrid,
  Text,
  Title,
} from '@mantine/core';
import React, { useMemo, useState } from 'react';
import ChannelCard from '../ui/ChannelCard';
import type { ChannelsProps } from '@/types/channel';
import channelsCol from '@/fixtures/channelsCollection';

const defaultChannels = channelsCol;

type TypeFilter = 'all' | 'channel' | 'group';

const Channels: React.FC<ChannelsProps> = ({ channels = defaultChannels }) => {
  const [typeFilter, setTypeFilter] = useState<TypeFilter>('all');
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  const sortedChannels = useMemo(
    () => [...channels].sort((a, b) => b.subscribers - a.subscribers),
    [channels],
  );

  const categories = useMemo(() => {
    const map = new Map<string, number>();
    for (const ch of sortedChannels) {
      map.set(ch.category, (map.get(ch.category) ?? 0) + 1);
    }
    return Array.from(map.entries()).sort((a, b) => b[1] - a[1]);
  }, [sortedChannels]);

  const filtered = useMemo(() => {
    let result = sortedChannels;

    if (typeFilter !== 'all') {
      result = result.filter((ch) => ch.type === typeFilter);
    }

    if (activeCategory) {
      result = result.filter((ch) => ch.category === activeCategory);
    }

    return result;
  }, [sortedChannels, typeFilter, activeCategory]);

  return (
    <Container>
      <Group justify="space-between" mb="md">
        <Title order={1}>Каталог каналов и групп</Title>
        <Text c="dimmed" size="sm">
          Найдено: {filtered.length} из {channels.length}
        </Text>
      </Group>

      <Group mb="md" gap="md" wrap="wrap" align="center">
        <SegmentedControl
          data={[
            { label: 'Все', value: 'all' },
            { label: 'Каналы', value: 'channel' },
            { label: 'Группы', value: 'group' },
          ]}
          value={typeFilter}
          onChange={(val) => setTypeFilter(val as TypeFilter)}
        />
      </Group>

      <Group gap="xs" mb="lg" wrap="wrap">
        <Button
          variant={activeCategory === null ? 'filled' : 'light'}
          color="tgblue"
          onClick={() => setActiveCategory(null)}
        >
          Все
        </Button>
        {categories.map(([cat, count]) => (
          <Button
            key={cat}
            variant={activeCategory === cat ? 'filled' : 'light'}
            color="tgblue"
            onClick={() => setActiveCategory(activeCategory === cat ? null : cat)}
          >
            {cat} ({count})
          </Button>
        ))}
      </Group>

      {filtered.length === 0 ? (
        <Text c="dimmed" ta="center" py="xl" size="lg">
          Ничего не найдено
        </Text>
      ) : (
        <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing={16}>
          {filtered.map((channel) => (
            <ChannelCard key={channel.id} channel={channel} />
          ))}
        </SimpleGrid>
      )}
    </Container>
  );
};

export default Channels;
