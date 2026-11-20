// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

// The desa the visitor marked as their own, kept for a year in a cookie so the home page can link straight to it.
export function useMyDesa() {
  return useCookie<string | null>('desa-saya', { maxAge: 60 * 60 * 24 * 365, sameSite: 'lax', default: () => null })
}
