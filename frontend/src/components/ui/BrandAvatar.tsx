import { Avatar, Flex } from '@mantine/core';
import React from 'react';

interface BrandAvatarProps {
  name: string;
  size?: number;
}

export const BrandAvatar: React.FC<BrandAvatarProps> = ({ name, size = 46 }) => {
  const initial = name?.[0]?.toUpperCase() ?? '?';

  return (
    <Avatar size={size} radius="xl" variant="gradient" gradient={{ from: 'tgblue', to: 'tgpurple', deg: 135 }}>
      <Flex align="center" justify="center" lh={1}>{initial}</Flex>
    </Avatar>
  );
};
