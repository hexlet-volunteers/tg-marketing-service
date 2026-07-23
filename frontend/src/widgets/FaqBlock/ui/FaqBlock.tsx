import React from 'react';
import { Accordion, Container, Title, Box } from '@mantine/core';
import type { FaqBlockProps } from '../model/types';
import { useFaqBlock } from '../model/useFaqBlock';

export const FaqBlock: React.FC<FaqBlockProps> = ({ faqs: propsFaqs }) => {
  const { faqs: faqsFromPage } = useFaqBlock();
  const faqs = propsFaqs ?? faqsFromPage;

  if (!faqs || faqs.length === 0) return null;

  return (
    <Box component="section" bg="muted.0" p={48}>
      <Container size="md" px="md">
        <Title order={2} ta="center" mb="lg">Частые вопросы</Title>

        <Accordion variant="separated" radius="md">
          {faqs.map((faq) => (
            <Accordion.Item key={faq.id} value={String(faq.id)}>
              <Accordion.Control>{faq.question}</Accordion.Control>
              <Accordion.Panel>
                {faq.answer}
              </Accordion.Panel>
            </Accordion.Item>
          ))}
        </Accordion>
      </Container>
    </Box>
  );
};
