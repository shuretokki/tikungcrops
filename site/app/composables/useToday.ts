// The "Hari ini" marker follows the visitor's own date, not the date of the data.
// The page is built ahead of time, so the day is set in the browser once the page has loaded.
// To undo this, build the marker from `meta.as_of` again, as the pages did before.
export function useToday() {
  const today = ref<number | null>(null)
  onMounted(() => {
    const now = new Date()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    const date = String(now.getDate()).padStart(2, '0')
    today.value = dayOfYear(`2001-${month}-${date}`)
  })
  return today
}
