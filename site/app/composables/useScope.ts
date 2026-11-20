// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

// The chosen place and crop. It is set on the home page and read by every other page.
export function useScope() {
  const region = useState('scope-region', () => 'tikung')
  const crop = useState('scope-crop', () => 'padi')
  const label = computed(() => {
    const c = COPY.scope.crops.find(o => o.value === crop.value)?.label ?? crop.value
    const r = COPY.scope.regions.find(o => o.value === region.value)?.label ?? region.value
    return COPY.scope.summary(c, r)
  })
  return { region, crop, label }
}
