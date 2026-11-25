import React from "react";
import { Container } from "@mantine/core";
import FormRegistration from "@/components/ui/FormRegistration";
import type { AuthPageProps } from "@/types/auth";

const Auth: React.FC<AuthPageProps> = ({ form, next }) => {
  return (
    <Container>
      <FormRegistration form={form} next={next} />
    </Container>
  );
};

export default Auth;
