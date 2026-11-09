import React from 'react';
import { Paper, Stack, Text, Title, Progress, Button } from '@mantine/core';
import TariffUpgrade from '../modals/TariffUpgrade';

/**
 * Компонент баннера обновления тарифа.
 *
 * Получает данные для отображения через пропс show_upgrade_banner: 
 * Этот shared props пока не реализован со стороны сервера.
 * В этой связи часть кода, связанная с пропсом show_upgrade_banner, закомментирована.
 * 
 * show_upgrade_banner со значение true будет показывать баннер только пользователям тарифа Free.
 * 
 * Нажатие кнопки "Улучшить тариф" открывает модальное окно обновления тарифа.
 * 
 * Пропсы модального окна (isVisible, onClose) заданы через UseState,
 * как и функция открытия модального окна.
 * 
 * Константы bannerTitle, bannerText и buttonText задают текстовое содержимое баннера.
 */

// interface UpgradeBannerProps {
//   show_upgrade_banner: boolean;
// }

const UpgradeBanner: React.FC/*<UpgradeBannerProps>*/ = (/*{ show_upgrade_banner }*/) => {  
  const [showModal, setShowModal] = React.useState(false);
    
  const openModal = () => setShowModal(true);
  const closeModal = () => setShowModal(false);

  const bannerTitle: string = "Тариф Free";
  const bannerText: string = "3 из 5 AI-разборов в этом месяце";
  const buttonText: string = "Улучшить тариф";

  /*if (show_upgrade_banner === true) {*/
    return (
      <>
        <Paper bg="tgblue.0">
          <Stack gap={0} p="md">
            <Title order={4} fz="xs" c="tgblue.6" mb={4}>{bannerTitle}</Title>
            <Text fz="xs" mb="xs" c="muted.5">
              {bannerText}
            </Text>
            <Progress value={60} h={6} radius="xl" mb="xs" bg="tgblue.1" color="tgblue.5"/>
            <Button fullWidth fz="xs" fw="bold" radius="md" color="tgblue.5" onClick={openModal}>
              {buttonText}
            </Button>
          </Stack>
        </Paper>
        <TariffUpgrade isVisible={showModal} onClose={closeModal} />
      </>
    )
  /*}
  return null;*/
}

export default UpgradeBanner;
