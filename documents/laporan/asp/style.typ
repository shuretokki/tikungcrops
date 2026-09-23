#let style(
  font-family: ("Times New Roman", "Liberation Serif"),
  font-size: 12pt,
  table-size: 10pt,
  lang: "id",
  body,
) = {
  set text(font: font-family, size: font-size, lang: lang)

  show link: it => {
    if type(it.dest) == str {
      text(fill: blue.darken(20%), underline(it))
    } else {
      it
    }
  }

  show table.cell: it => {
    set text(size: table-size)
    set par(justify: false, leading: 0.5em, first-line-indent: 0pt)
    it
  }

  body
}
