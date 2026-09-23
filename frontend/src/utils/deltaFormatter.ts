const deltaFormatter = (delta: number | undefined, percentDelta: number | undefined): string => {
  if (delta && percentDelta) {
    return delta > 0 
      ? `+${delta.toLocaleString('ru-RU')} · ${percentDelta.toFixed(1).replace(/\.0$/, '')}%` 
      : `${delta.toLocaleString('ru-RU')} · ${percentDelta.toFixed(1).replace(/\.0$/, '')}%`
  }
  if (delta) {
    return delta > 0
      ? `+${delta.toLocaleString('ru-RU')}` 
      : delta.toLocaleString('ru-RU')
  }
  if (percentDelta) {
    return percentDelta > 0 
      ? `+${percentDelta.toFixed(1).replace(/\.0$/, '')}%` 
      : `${percentDelta.toFixed(1).replace(/\.0$/, '')}%`
  }
  return '0'
}

export default deltaFormatter