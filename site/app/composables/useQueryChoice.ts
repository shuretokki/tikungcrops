// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

// A choice that lives in the address, so a view can be shared and the back button works.
export function useQueryChoice<T extends string>(key: string, allowed: readonly T[], fallback: T) {
  const route = useRoute()
  const router = useRouter()
  return computed<T>({
    get: () => {
      const v = String(route.query[key] ?? '')
      return (allowed as readonly string[]).includes(v) ? v as T : fallback
    },
    set: (v) => {
      router.replace({ query: { ...route.query, [key]: v === fallback ? undefined : v } })
    }
  })
}
