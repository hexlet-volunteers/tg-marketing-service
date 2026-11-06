import React from 'react';
import { Avatar, Group, Modal, SegmentedControl, SimpleGrid, Text } from '@mantine/core';
import TariffCard from '../ui/TariffCard';

/**
 * Компонент модального окна обновления тарифа.
 *
 * Получает данные для отображения через пропсы: 
 * возможность отображения модального окна (isVisible), функция закрытия модального окна (onClose).
 * 
 * Добавлена возможность переключать период оплаты через SegmentedControl (помесячно vs за год со скидкой),
 * период оплаты сохраняется через useState в состоянии billingPeriod.
 * Изменение billingPeriod идёт через клик по соответствующему значению SegmentedControl.
 * 
 * Значение billingPeriod в качестве одного из пропсов передаётся в компонент TariffCard для отображения цены и периода оплаты.
 * 
 * Три возможные варианта тарифа (Free, Pro и Agency) отображаются через компонент TariffCard
 * с соответствующими данными в качестве пропсов (name, price, period, features, type).
 */

interface TariffUpgradeProps {
  isVisible: boolean;
  onClose: () => void;
}

const TariffUpgrade: React.FC<TariffUpgradeProps> = ({ isVisible, onClose }) => {
  const [billingPeriod, setBillingPeriod] = React.useState('monthly');

  return (
    <Modal.Root
      opened={isVisible}
      onClose={onClose}
      centered
      size="xl"
      radius="lg"
      shadow="modal"
    >
      <Modal.Overlay />

      <Modal.Content>
        <Modal.Header style={{ borderBottom: '1px solid var(--mantine-color-muted-1)' }}>
          <Group gap="xs">
              <Avatar color="tgblue" radius="md">t</Avatar>
              <Text size="sm" fw={700}>tgpulse</Text>
            </Group>
          <Modal.CloseButton />
        </Modal.Header>

        <Modal.Body style={{ padding: '22px 24px 24px' }}>
          <Modal.Title fz={19} fw={800} mb={4}>
            Улучшить тариф
          </Modal.Title>
          <Text size="sm" c="dimmed">
            Больше AI, без лимитов на разборы
          </Text>
          <SegmentedControl
            mt="md"
            size="sm"
            radius="md"
            value={billingPeriod}
            onChange={setBillingPeriod}
            data={[
              { label: 'Помесячно', value: 'monthly' },
              { label: 'За год · -20%', value: 'yearly' },
            ]}
          />
          <SimpleGrid mt="md" cols={{ base: 1, sm: 3 }} spacing="md">
            <TariffCard
              name="Free"
              price="0 ₽"
              period="навсегда"
              features={["Базовая статистика", "5 AI-разбора в месяц", "Каталог и подборки"]}
              type="free"
            />
            <TariffCard
              name="Pro"
              price={billingPeriod === 'monthly' ? '990 ₽' : '790 ₽'}
              period={billingPeriod === 'monthly' ? 'в месяц' : 'в месяц (при оплате за год)'}
              features={["Безлимит AI-разборов", "Контент-план и композер", "Сравнение до 5 каналов", "Конкуренты и алерты", "Экспорт отчётов"]}
              type="pro"
            />
            <TariffCard
              name="Agency"
              price={billingPeriod === 'monthly' ? '4 900 ₽' : '3 900 ₽'}
              period={billingPeriod === 'monthly' ? 'в месяц' : 'в месяц (при оплате за год)'}
              features={["Всё из Pro", "До 50 каналов и групп", "API-доступ", "Командный доступ"]}
              type="agency"
            />
          </SimpleGrid>
        </Modal.Body>
      </Modal.Content>
    </Modal.Root>
  );
};

export default TariffUpgrade;
