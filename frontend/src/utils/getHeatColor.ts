const getHeatColor = (value: number) => {
  if (value === 0) return 'var(--mantine-color-gray-1)';
  if (value <= 3) return 'var(--mantine-color-tgblue-1)';
  if (value <= 5) return 'var(--mantine-color-tgblue-2)';
  if (value <= 7) return 'var(--mantine-color-tgblue-3)';
  if (value <= 9) return 'var(--mantine-color-tgblue-4)';
  return 'var(--mantine-color-tgblue-5)';
};

export default getHeatColor;