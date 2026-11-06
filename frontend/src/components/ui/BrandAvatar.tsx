import { Avatar, Flex } from "@mantine/core";
import React from "react";
import { avatarGradients } from '@/shared/const/avatarGradients';

/** Пропсы для компонента аватара бренда */
interface BrandAvatarProps {
 /** Название бренда или канала. Первая буква будет использована как инициал. */
 name: string;
 /** Размер аватара в пикселях. По умолчанию: 46. */
 size?: number;
}

/**
 * Круглый аватар с градиентным фоном и первой буквой названия бренда/канала.
 * Использует фирменные цвета tgblue и tgpurple.
 */
export const BrandAvatar: React.FC<BrandAvatarProps> = ({
 name,
 size = 46,
}) => {
 const initial = name?.[0]?.toUpperCase() ?? "?";

 return (
  <Avatar
   size={size}
   radius="xl"
   variant="gradient"
   gradient={{ ...avatarGradients.default }}
  >
   <Flex align="center" justify="center" lh={1}>
    {initial}
   </Flex>
  </Avatar>
 );
};
