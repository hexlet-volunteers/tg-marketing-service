import { http, router } from '@inertiajs/react';
import {
  Anchor,
  Avatar,
  Box,
  Button,
  Divider,
  Group,
  Modal,
  PasswordInput,
  Stack,
  Text,
  TextInput,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { useState } from 'react';
import { mapServerErrors } from '@/utils/mapServerErrors';
import PasswordRecovery from './PasswordRecovery';

interface AuthModalProps {
  opened: boolean;
  onClose: () => void;
  next?: string;
}

const FIELD_KEYS = new Set(['email', 'password']);

const AuthModal = ({ opened, onClose, next }: AuthModalProps) => {
  const form = useForm({
    initialValues: { email: '', password: '' },
    validate: {
      email: (val) => (!val || !/^\S+@\S+\.\S+$/.test(val) ? 'Некорректный email' : null),
      password: (val) => (!val ? 'Введите пароль' : null),
    },
    validateInputOnBlur: true,
  });

  const [showRecovery, setShowRecovery] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [generalError, setGeneralError] = useState('');
  const { setErrors } = form;

  const onSubmit = async (values: { email: string; password: string }) => {
    setProcessing(true);
    setGeneralError('');

    try {
      const response = await http.getClient().request({
        method: 'post',
        url: '/auth/login/',
        data: new URLSearchParams({
          email: values.email,
          password: values.password,
          next: next ?? '',
        }),
        headers: { 'X-Inertia': 'true' },
      });

      const isJson = (response.headers['content-type'] ?? '').includes('application/json');
      const data = isJson && response.data ? JSON.parse(response.data) : null;

      const serverErrors = data?.props?.form?.errors;
      if (serverErrors && Object.keys(serverErrors).length > 0) {
        const errors = mapServerErrors(serverErrors);
        setErrors({
          email: errors.email ?? '',
          password: errors.password ?? '',
        });
        setGeneralError(
          Object.entries(errors).find(([field]) => !FIELD_KEYS.has(field))?.[1] ?? '',
        );
        return;
      }

      onClose();
      router.visit(typeof data?.url === 'string' ? data.url : next || '/dashboard/');
    } catch {
      setGeneralError('Не удалось войти. Проверьте подключение и попробуйте ещё раз.');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <>
      <Modal.Root
        opened={opened}
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
              Вход
            </Modal.Title>
            <Text size="sm" c="dimmed" mb="md">
              Рады видеть снова
            </Text>

            <Box component="form" noValidate onSubmit={form.onSubmit(onSubmit)}>
              <Stack gap="sm">
                <TextInput
                  {...form.getInputProps('email')}
                  type="email"
                  placeholder="Email"
                />

                <PasswordInput
                  {...form.getInputProps('password')}
                  placeholder="Пароль"
                />

                <Group justify="flex-end">
                  <Anchor
                    component="button"
                    type="button"
                    size="sm"
                    fw={600}
                    onClick={() => setShowRecovery(true)}
                  >
                    Забыли пароль?
                  </Anchor>
                </Group>

                {generalError && (
                  <Text c="red" size="sm" ta="center">
                    {generalError}
                  </Text>
                )}

                <Button
                  type="submit"
                  fullWidth
                  color="tgblue"
                  loading={processing}
                  disabled={processing}
                >
                  Войти
                </Button>

                <Text size="sm" c="dimmed" ta="center">
                  Нет аккаунта?{' '}
                  <Anchor
                    component="button"
                    type="button"
                    size="sm"
                    fw={700}
                    onClick={() => {
                      onClose();
                      router.visit('/auth/create/');
                    }}
                  >
                    Зарегистрироваться
                  </Anchor>
                </Text>
              </Stack>
            </Box>
          </Modal.Body>
        </Modal.Content>
      </Modal.Root>
      <PasswordRecovery isVisible={showRecovery} onClose={() => setShowRecovery(false)} />
    </>
  );
};

export default AuthModal;
