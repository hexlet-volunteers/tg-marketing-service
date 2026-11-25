import { Anchor, Avatar, Button, Divider, Group, Modal, Stack, Text, TextInput } from '@mantine/core';
import { useForm } from '@mantine/form';
import React from 'react';

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
    <Modal.Root
      opened={isVisible}
      onClose={onClose}
      centered
      size={420}
      radius="lg"
      shadow="modal"
    >
      <Modal.Overlay />

      <Modal.Content>
        <Modal.Header>
          <Group gap="xs">
            <Avatar color="tgblue" radius="md">t</Avatar>
            <Text size="sm" fw="bold">tgpulse</Text>
          </Group>
          <Modal.CloseButton />
        </Modal.Header>
        <Divider color="muted.1" />

        <Modal.Body p="lg">
          <Modal.Title fz="lg" fw="bold" mb={4}>
            Сброс пароля
          </Modal.Title>
          <Text size="sm" c="dimmed" mb="md">
            Введите email — пришлём ссылку для восстановления доступа
          </Text>

          <form onSubmit={form.onSubmit(handleSubmit)}>
            <Stack gap="sm">
              <TextInput
                {...form.getInputProps('email')}
                type="email"
                placeholder="Email"
              />

              <Button type="submit" fullWidth color="tgblue">
                Отправить ссылку
              </Button>

              <Text size="sm" c="dimmed" ta="center">
                Вспомнили пароль?{' '}
                <Anchor component="button" type="button" size="sm" fw={700} onClick={onClose}>
                  Войти
                </Anchor>
              </Text>
            </Stack>
          </form>
        </Modal.Body>
      </Modal.Content>
    </Modal.Root>
  );
};

export default PasswordRecovery;
