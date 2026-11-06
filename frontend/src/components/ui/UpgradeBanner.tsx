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
 */

// interface UpgradeBannerProps {
//   show_upgrade_banner: boolean;
// }

const UpgradeBanner: React.FC/*<UpgradeBannerProps>*/ = (/*{ show_upgrade_banner }*/) => {  
  const [showModal, setShowModal] = React.useState(false);
    
  const openModal = () => setShowModal(true);
  const closeModal = () => setShowModal(false);

  /*if (show_upgrade_banner === true) {*/
    return (
      <>
        <Paper bg="tgblue.0">
          <Stack gap={0} p={14}>
            <Title order={4} fz={12} c="tgblue.6" mb={4}>Тариф Free</Title>
            <Text fz={11.5} mb={10} c="muted.5">
              3 из 5 AI-разборов в этом месяце
            </Text>
            <Progress value={60} h={6} radius="xl" mb={11} bg="tgblue.1" color="tgblue.5"/>
            <Button fullWidth fz={12} fw={700} radius="md" color="tgblue.5" onClick={openModal}>
              Улучшить тариф
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
