// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: Apache-2.0

// Builds the HTML of a chart or map tooltip.
// Every tooltip has the same shape: a title, an optional subtitle, rows of label and value, and a note.
// The styles are in viz.css under the "tip" class names.

export interface TipRow { label: string, value: string, color?: string }
export interface TipInput { title: string, subtitle?: string, rows?: TipRow[], note?: string }

const ESCAPES: Record<string, string> = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', '\'': '&#39;' }
const esc = (s: string) => s.replace(/[&<>"']/g, c => ESCAPES[c]!)

export function tip({ title, subtitle, rows = [], note }: TipInput) {
  const head = `<div class="tip-title">${esc(title)}</div>${subtitle ? `<div class="tip-sub">${esc(subtitle)}</div>` : ''}`
  const body = rows.map(r => `<div class="tip-row"><span class="tip-label">${r.color ? `<span class="tip-dot" style="background:${esc(r.color)}"></span>` : ''}${esc(r.label)}</span><span class="tip-value">${esc(r.value)}</span></div>`).join('')
  return `<div class="tip">${head}${body}${note ? `<div class="tip-note">${esc(note)}</div>` : ''}</div>`
}

// A signed percent such as "+12%" or "-8%".
export function signedPercent(v: number) {
  const n = Math.round(v * 100)
  return `${n > 0 ? '+' : ''}${n.toLocaleString('id-ID')}%`
}
