interface FormFieldError {
  message: string;
  code: string;
}

interface AuthFormState {
  data: {
    email: string;
    password: string;
  };
  errors: Record<string, FormFieldError[]>;
}

interface AuthPageProps {
  form: AuthFormState;
  next: string;
}

interface AuthUser {
  id: number;
  name: string;
  email: string;
  avatar_url: string;
  role: string;
}

interface SharedPageProps {
  auth: AuthUser | null;
  role: string;
  is_admin: boolean;
  csrfToken: string;
  flash: { success?: string; error?: string } | null;
  [key: string]: unknown;
}

export type {
  FormFieldError,
  AuthFormState,
  AuthPageProps,
  AuthUser,
  SharedPageProps,
};
