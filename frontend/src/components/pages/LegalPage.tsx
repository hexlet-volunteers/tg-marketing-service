import {
  Container,
  Paper,
  SegmentedControl,
  Text,
  Title,
} from '@mantine/core';
import React from 'react';

const legalContent: Record<string, { title: string; text: string }> = {
  privacy: {
    title: 'Политика конфиденциальности',
    text: 'Мы собираем и обрабатываем персональные данные пользователей исключительно для целей предоставления сервиса аналитики Telegram-каналов. Мы не передаём данные третьим лицам без явного согласия пользователя.',
  },
  terms: {
    title: 'Пользовательское соглашение',
    text: 'Используя сервис TG Pulse, вы соглашаетесь с данными условиями. Сервис предоставляет инструменты аналитики Telegram-каналов «как есть» без гарантий точности данных.',
  },
  offer: {
    title: 'Публичная оферта',
    text: 'Настоящая оферта адресована физическим и юридическим лицам и определяет условия предоставления платных услуг сервиса TG Pulse на условиях подписки.',
  },
};

const LegalPage: React.FC = () => {
  const [tab, setTab] = React.useState('privacy');

  return (
    <Container>
      <Title order={1} mb="lg">
        Правовая информация
      </Title>
      <SegmentedControl
        data={[
          { label: 'Конфиденциальность', value: 'privacy' },
          { label: 'Соглашение', value: 'terms' },
          { label: 'Оферта', value: 'offer' },
        ]}
        value={tab}
        onChange={(v) => setTab(v as string)}
        mb="lg"
        fullWidth
      />
      <Paper p="lg">
        {(() => {
          const content = legalContent[tab];
          return (
            <>
              <Title order={3} mb="md">{content.title}</Title>
              <Text size="sm" c="dimmed">{content.text}</Text>
            </>
          );
        })()}
      </Paper>
    </Container>
  );
};

export default LegalPage;
