export function formatNumberShort(num: number): string {
  if (num >= 1_000_000) {
    return (num / 1_000_000).toFixed(1).replace(/\.0$/, '') + ' млн';
  } else if (num >= 10_000) {
    return Math.round(num / 1_000) + ' тыс.';
  } else if (num >= 1_000) {
    return (num / 1_000).toFixed(1).replace(/\.0$/, '') + ' тыс.';
  } else {
    return num.toString();
  }
}

export function formatNumberShortEn(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M';
  if (n >= 1_000) return (n / 1_000).toFixed(1).replace(/\.0$/, '') + 'K';
  return String(n);
}

export function formatNumber(num: number): string {
    if (Math.abs(num) >= 950000) {
        const millions = Math.round(num / 1000000);
        return `${millions}M`;
    }
    
    const thousands = Math.round(num / 1000);
    return `${thousands}K`;
}
