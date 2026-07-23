export interface TariffFeature {
  id: number;
  text: string;
}

export interface TariffButton {
  label: string;
  variant: 'default' | 'primary';
}

export interface Tariff {
  id: number;
  name: string;
  label?: string;
  description: string;
  price: string;
  period: string;
  monthlyPrice: number;
  features: TariffFeature[];
  button: TariffButton;
  isHighlighted?: boolean;
  isPopular?: boolean;
}

export interface TariffsBlockProps {
  tariffs?: Tariff[];
}
