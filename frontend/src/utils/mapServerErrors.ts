import type { FormFieldError } from '@/types/auth';

export type ServerErrors = Record<string, FormFieldError[] | string>;

export const mapServerErrors = (serverErrors?: ServerErrors) =>
  Object.entries(serverErrors ?? {}).reduce<Record<string, string>>(
    (acc, [key, value]) => {
      const message = Array.isArray(value) ? value[0]?.message : value;
      if (message) {
        acc[key] = message;
      }
      return acc;
    },
    {},
  );
