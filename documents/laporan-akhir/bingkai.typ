// SPDX-FileCopyrightText: Copyright © 2026 Tri Rianto Utomo
// SPDX-License-Identifier: CC-BY-4.0

// A plain browser window drawn around website screenshots.
// The address bar stays empty until the site has a public address.
#let bingkai-browser(body, url: none, width: 100%, warna: luma(55), tebal: 0.8pt) = {
  let garis = tebal + warna
  let ikon(isi) = text(size: 10pt, fill: warna, font: ("Source Sans 3", "DejaVu Sans"), isi)
  let cari = box(width: 7pt, height: 7pt, {
    place(circle(radius: 2.4pt, stroke: 0.7pt + warna))
    place(dx: 4pt, dy: 4pt, line(length: 3pt, angle: 45deg, stroke: 0.7pt + warna))
  })
  block(width: width, stroke: garis, radius: 6pt, clip: true, breakable: false, {
    block(width: 100%, inset: (x: 10pt, y: 5pt), stroke: (bottom: garis), grid(
      columns: (auto, auto, 1fr, auto, auto),
      column-gutter: 10pt,
      align: horizon,
      ikon[←], ikon[→],
      // #figure centres its body, so the address bar sets left alignment itself.
      box(width: 100%, height: 13pt, stroke: 0.7pt + warna, radius: 3pt, inset: (x: 5pt),
        align(left + horizon, stack(dir: ltr, spacing: 5pt, cari, text(size: 7.5pt, fill: warna, if url == none { [] } else { url })))),
      ikon[↓], ikon[≡],
    ))
    set image(width: 100%)
    body
  })
}
