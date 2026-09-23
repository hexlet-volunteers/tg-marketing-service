interface LegalItem {
    title: string;
    text: string;
}

interface LegalPageProps {
    legalContent: Record<string, LegalItem>;
}

export type { LegalItem, LegalPageProps }