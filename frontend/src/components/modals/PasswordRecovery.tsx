import React from 'react';
import { Modal, TextInput, Stack, Text, Group, Button } from '@mantine/core';
import { useForm } from '@mantine/form';

interface PasswordRecoveryProps {
  isVisible: boolean;
  onClose: () => void;
}

const PasswordRecovery: React.FC<PasswordRecoveryProps> = ({ isVisible, onClose }) => {
  const form = useForm({
    initialValues: { email: '' },
    validate: {
      email: (val) => (!val || !/^\S+@\S+\.\S+$/.test(val) ? 'Некорректный email' : null),
    },
  });

  const handleSubmit = (values: { email: string }) => {
    console.log('Password recovery:', values.email);
    onClose();
  };

  return (
    <Modal opened={isVisible} onClose={onClose} title="Восстановление пароля" centered>
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack>
          <Text size="sm">Введите ваш email</Text>
          <TextInput
            {...form.getInputProps('email')}
            type="email"
            placeholder="E-mail"
          />
          <Group justify="space-between">
            <Button type="submit" color="tgblue">Отправить ссылку</Button>
            <Button variant="subtle" onClick={onClose}>Отмена</Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
};

export default PasswordRecovery;
