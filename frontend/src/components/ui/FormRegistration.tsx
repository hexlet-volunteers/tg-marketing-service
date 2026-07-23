import React from 'react';
import { Text, TextInput, PasswordInput, Checkbox, Stack, Divider, Group, Title, Button, Box, Flex, Anchor } from '@mantine/core';
import { useForm } from '@mantine/form';
import { SocialIcon } from 'react-social-icons';
import PasswordRecovery from '../modals/PasswordRecovery';

const FormRegistration: React.FC = () => {
  const form = useForm({
    initialValues: { email: '', password: '', remember: false },
    validate: {
      email: (val) => (!val || !/^\S+@\S+\.\S+$/.test(val) ? 'Некорректный email' : null),
      password: (val) => (!val || val.length < 6 ? 'Минимум 6 символов' : null),
    },
  });

  const [showModal, setShowModal] = React.useState(false);

  const openModal = () => setShowModal(true);
  const closeModal = () => setShowModal(false);

  const onSubmit = (values: { email: string; password: string; remember: boolean }) => {
    console.log('Login:', values.email);
  };

  return (
    <>
      <Box
        component="form"
        onSubmit={form.onSubmit(onSubmit)}
        maw={380}
        mx="auto"
        p={20}
      >
        <Flex direction="column" gap="md">
          <Box ta="center">
            <Title order={2} fw={700}>Войти в систему</Title>
            <Text c="dimmed">Используйте привычный способ входа</Text>
          </Box>

          <Group justify="center" gap="sm">
            <Box w={40} h={40}><SocialIcon network="yandex" /></Box>
            <Box w={40} h={40}><SocialIcon network="vk" /></Box>
            <Box w={40} h={40}><SocialIcon network="github" /></Box>
          </Group>

          <Divider label="или" labelPosition="center" />

          <TextInput
            {...form.getInputProps('email')}
            type="email"
            placeholder="E-mail"
          />

          <PasswordInput
            {...form.getInputProps('password')}
            placeholder="Пароль"
          />

          <Checkbox
            {...form.getInputProps('remember', { type: 'checkbox' })}
            label="Запомнить меня"
          />

          <Stack gap="sm" align="center">
            <Button type="submit" fullWidth color="tgblue">
              Войти
            </Button>
            <Anchor component="button" size="sm" onClick={openModal}>
              Забыли пароль?
            </Anchor>
          </Stack>
        </Flex>
      </Box>
      <PasswordRecovery isVisible={showModal} onClose={closeModal} />
    </>
  );
};

export default FormRegistration;
