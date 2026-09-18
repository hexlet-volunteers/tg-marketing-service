
export const initials = (name: string): string => {
  return name.split(' ').find(word => word === 'AI') 
    ? 'AI' 
    : name.split(' ').map((w) => w[0]).slice(0, 2).join('').toUpperCase(); 
}