interface LegalItem {
    title: string;
    text: string;
    updated_at?: string;
}

interface LegalPageProps {
    documents: Record<string, LegalItem>;
}

export type { LegalItem, LegalPageProps };
