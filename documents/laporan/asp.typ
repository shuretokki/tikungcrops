#import "asp/defaults.typ" as defaults
#import "asp/layout.typ": layout
#import "asp/style.typ": style
#import "asp/components.typ": components, subfig, zebraw
#import "asp/outlines.typ": outlines
#import "asp/title-page.typ": title-page

#let frontmatter(
  outlined: true,
  title: none,
  title-align: center,
  uppercase-title: true,
  numbering: auto,
  start-page: auto,
  show-footer: true,
  show-page-number: true,
  pagebreak-before: true,
  pagebreak-after: true,
  body,
) = [#metadata((
  type: "front",
  outlined: outlined,
  title: title,
  numbering: numbering,
  start-page: start-page,
  show-footer: show-footer,
  show-page-number: show-page-number,
  pagebreak-before: pagebreak-before,
  pagebreak-after: pagebreak-after,
  body: {
    if start-page != auto {
      counter(page).update(start-page)
    }
    if title != none {
      let formatted-title = if uppercase-title and type(title) == str { upper(title) } else { title }
      align(title-align)[
        #heading(level: 1, numbering: none, outlined: outlined)[#formatted-title]
      ]
    }
    set figure(outlined: false)
    body
  },
)) <asp-matter>]

#let backmatter(it) = [#metadata((
  type: "back",
  body: {
    set figure(outlined: false, caption: none, gap: 0pt)
    it
  },
)) <asp-matter>]

#let signature-block(
  role: "",
  name: "",
  id-label: "NIP",
  id: "",
  height: 2cm,
  align-text: center,
) = block(width: 100%)[
  #set align(align-text)
  #if role != "" [#role \ ]
  #v(height)
  #text(weight: "bold")[#name] \
  #if id != "" [#id-label #id]
]

#let footer-state = state("asp-footer-text", none)
#let set-footer-text(val) = footer-state.update(val)

#let asp(
  title: "",
  extra-title: "",
  partner: "",
  footer-text: none,
  footer: (:),
  course: "",
  lecturer: (name: "", id: ""),
  students: (),
  program: "",
  department: "",
  faculty: "",
  university: "",
  year: "",
  logo: "unesa.png",
  bib-file: none,
  bib-style: "ieee",
  lang: "id",
  type: none,
  theme: sys.inputs.at("theme", default: "light"),
  paper: "a4",
  margin: "print",
  cover: (:),
  numbering-config: (:),
  typography: (:),
  paragraph: (:),
  outlines-attr: (:),
  headings-attr: (:),
  i18n: (:),
  include-cover: true,
  body,
) = {
  let cover = (
    (
      top: 2cm,
      logo-width: 8cm,
      title-size: 18pt,
      type-size: 14pt,
      type-pos: "bottom", // "top" or "bottom"
      gap-course-lecturer: 0.2cm,
      gap-lecturer-students: 0.2cm,
    )
      + cover
  )

  let numbering-config = (
    (
      front: auto,
      back: auto,
      back-title: auto,
      lampiran: auto,
      heading: auto,
      bib-chapter: true,
      align: center,
    )
      + numbering-config
  )

  let typography = (
    (
      font-family: ("Times New Roman", "Liberation Serif"),
      font-size: 12pt,
      caption-size: auto,
      caption-gap: auto,
      table-size: 10pt,
    )
      + typography
  )

  let paragraph = (
    (
      justify: true,
      indent: 0.63cm,
      leading: 0.575em,
      spacing: 1.15em,
      enum-indent: 0cm,
      enum-body-indent: 0.63cm,
      list-indent: 0.63cm,
      list-body-indent: 0.63cm,
    )
      + paragraph
  )

  let footer-config = (
    (
      enabled: true,
      show-on-cover: false,
      left: auto,
      center: auto,
      right: none,
      mode: "stacked",
      show-page-number: true,
      page-number-align: center,
      font-size: 9pt,
      weight: "bold",
      style: "normal",
      separator-line: false,
    )
      + footer
  )

  let outlines-attr = (
    (
      depth: 3,
      figures: true,
      tables: true,
      codes: true,
      toc: true,
      toc-title: auto,
      lof-title: auto,
      lot-title: auto,
      loc-title: auto,
    )
      + outlines-attr
  )

  let headings-attr = (
    (
      h1: auto,
      h2: auto,
      h3: auto,
      h4: auto,
    )
      + headings-attr
  )

  let i18n = (
    (
      course: (id: "Mata Kuliah :", en: "Course :"),
      lecturer: (id: "Dosen Pengampu :", en: "Lecturer :"),
      students: (id: [Disusun oleh :], en: "Prepared by :"),
      program: (id: "PROGRAM STUDI", en: "STUDY PROGRAM"),
      faculty: (id: "FAKULTAS", en: "FACULTY"),
      toc: (id: [DAFTAR ISI], en: [TABLE OF CONTENTS]),
      lof: (id: [DAFTAR GAMBAR], en: [LIST OF FIGURES]),
      lot: (id: [DAFTAR TABEL], en: [LIST OF TABLES]),
      loc: (id: [DAFTAR KODE], en: [LIST OF CODES]),
      back: (id: [LAMPIRAN-LAMPIRAN], en: [APPENDICES]),
      lampiran: (id: "Lampiran", en: "Appendix"),
      chapter: (id: "BAB", en: "CHAPTER"),
      code: (id: "Kode", en: "Code"),
      thesis: (id: "SKRIPSI", en: "THESIS"),
      ta: (id: "LAPORAN TUGAS AKHIR", en: "FINAL PROJECT REPORT"),
      practicum: (id: "LAPORAN PRAKTIKUM", en: "PRACTICUM REPORT"),
      report: (id: "LAPORAN AKHIR", en: "FINAL REPORT"),
      proposal: (id: "PROPOSAL PENELITIAN", en: "RESEARCH PROPOSAL"),
      by: (id: "Oleh", en: "By"),
      department: (id: "JURUSAN", en: "DEPARTMENT")
    ) + i18n
  )

  let tr(key) = i18n.at(key).at(lang)

  let is-formal = (
    type != none
      and (
        lower(type) in ("skripsi", "ta", "thesis", "proposal")
      )
  )

  let type-label = if type == none { "" } else { type }

  let label-course = tr("course")
  let label-lecturer = tr("lecturer")
  let label-students = tr("students")
  let label-program = tr("program")
  let label-faculty = tr("faculty")
  let label-dept = tr("department")
  let label-by = tr("by")

  let toc-title = if outlines-attr.toc-title != auto { outlines-attr.toc-title } else { tr("toc") }
  let lof-title = if outlines-attr.lof-title != auto { outlines-attr.lof-title } else { tr("lof") }
  let lot-title = if outlines-attr.lot-title != auto { outlines-attr.lot-title } else { tr("lot") }
  let loc-title = if outlines-attr.loc-title != auto { outlines-attr.loc-title } else { tr("loc") }

  let back-title = if numbering-config.back-title != auto { numbering-config.back-title } else { tr("back") }
  let lampiran-label = if numbering-config.lampiran != auto { numbering-config.lampiran } else { tr("lampiran") }
  let chapter-prefix = tr("chapter")
  let code-supplement = tr("code")

  set document(title: title, author: students.map(s => s.name))

  set page(numbering: none)
  set page(footer: context {
    set par(first-line-indent: 0pt)
    let section = state("asp-section", "front").get()
    if section == "cover" or footer-config.enabled == false {
      return none
    }

    let local-fn = state("asp-front-numbering", auto).get()
    let fn = if local-fn != auto and local-fn != none {
      local-fn
    } else if numbering-config.front != auto {
      numbering-config.front
    } else {
      defaults.numbering.front
    }
    let bn = "1"
    let backn = if numbering-config.back != auto { numbering-config.back } else { defaults.numbering.back }
    let fmt = if section == "main" {
      bn
    } else if section == "back" and backn == "body" {
      bn
    } else {
      fn
    }

    let n = counter(page).get().first()
    let page-num-str = if footer-config.show-page-number {
      std.numbering(fmt, n)
    } else {
      ""
    }

    let state-text = footer-state.get()
    let left-val = if state-text != none {
      state-text
    } else if footer-config.left != auto {
      footer-config.left
    } else if footer-text != none {
      footer-text
    } else {
      none
    }

    let sep = if footer-config.separator-line [
      #line(length: 100%, stroke: 0.5pt + luma(150))
      #v(0.2em)
    ] else [ ]

    if footer-config.mode == "stacked" [
      #sep
      #if left-val != none [
        #align(left, text(size: footer-config.font-size, weight: footer-config.weight, style: footer-config.style)[#left-val])
        #v(0.2em)
      ]
      #if page-num-str != "" [
        #align(footer-config.page-number-align, text(size: typography.font-size)[#page-num-str])
      ]
    ] else [
      #sep
      #grid(
        columns: (1fr, auto, 1fr),
        align: (left + bottom, footer-config.page-number-align + bottom, right + bottom),
        if left-val != none { text(size: footer-config.font-size, weight: footer-config.weight, style: footer-config.style)[#left-val] } else { [] },
        if page-num-str != "" { text(size: typography.font-size)[#page-num-str] } else { [] },
        if footer-config.right != none { text(size: footer-config.font-size)[#footer-config.right] } else { [] },
      )
    ]
  })

  show: layout.with(
    paper: paper,
    margin: margin,
    number-align: numbering-config.align,
  )

  show: style.with(
    font-family: typography.font-family,
    font-size: typography.font-size,
    table-size: typography.table-size,
    lang: lang,
  )

  show: components.with(
    numbering-style: (
      if numbering-config.heading != auto { (heading: numbering-config.heading) } else { (:) }
        + if numbering-config.front != auto { (front: numbering-config.front) } else { (:) }
        + (body: "1")
        + if numbering-config.back != auto { (back: numbering-config.back) } else { (:) }
    ),
    caption: (
      if typography.caption-size != auto { (size: typography.caption-size) } else { (:) }
        + if typography.caption-gap != auto { (gap: typography.caption-gap) } else { (:) }
    ),
    labels: (
      if chapter-prefix != auto { (chapter: chapter-prefix) } else { (:) }
        + if lampiran-label != auto { (appendix: lampiran-label) } else { (:) }
        + if code-supplement != auto { (code: code-supplement) } else { (:) }
    ),
    headings: (
      if headings-attr.h1 != auto { (h1: headings-attr.h1) } else { (:) }
        + if headings-attr.h2 != auto { (h2: headings-attr.h2) } else { (:) }
        + if headings-attr.h3 != auto { (h3: headings-attr.h3) } else { (:) }
        + if headings-attr.h4 != auto { (h4: headings-attr.h4) } else { (:) }
    ),
    bib-chapter: numbering-config.bib-chapter,
  )

  let logo-img = if logo != none { image(logo, width: cover.logo-width) } else { none }

  let apply-template(it) = {
    let content = outlines.with(
      front-numbering: if numbering-config.front != auto { numbering-config.front } else { defaults.numbering.front },
      body-numbering: "1",
      back-numbering: if numbering-config.back != auto { numbering-config.back } else { defaults.numbering.back },
      chapter-prefix: chapter-prefix,
      toc-title: toc-title,
      toc-depth: outlines-attr.depth,
      back-title: back-title,
      lampiran-label: lampiran-label,
      list-of-figures: outlines-attr.figures,
      list-of-tables: outlines-attr.tables,
      list-of-codes: outlines-attr.codes,
      toc: outlines-attr.toc,
      lof-title: lof-title,
      lot-title: lot-title,
      loc-title: loc-title,
      bib-chapter: numbering-config.bib-chapter,
    )(it)

    if include-cover {
      title-page(
        title: title,
        extra-title: extra-title,
        partner: partner,
        course: course,
        lecturer: lecturer,
        students: students,
        program: program,
        department: department,
        faculty: faculty,
        university: university,
        year: year,
        logo-image: logo-img,
        type: type,
        type-label: type-label,
        is-formal: is-formal,
        type-pos: cover.type-pos,
        cover-top: cover.top,
        cover-title-size: cover.title-size,
        cover-type-size: cover.type-size,
        cover-gap-course-lecturer: cover.gap-course-lecturer,
        cover-gap-lecturer-students: cover.gap-lecturer-students,
        label-course: label-course,
        label-lecturer: label-lecturer,
        label-students: label-students,
        label-program: label-program,
        label-faculty: label-faculty,
        label-dept: label-dept,
        label-by: label-by,
        content,
      )
    } else {
      content
    }
  }

  show: apply-template

  set par(
    justify: paragraph.justify,
    first-line-indent: (amount: paragraph.indent, all: true),
    leading: paragraph.leading,
    spacing: paragraph.spacing,
  )

  set enum(indent: paragraph.enum-indent, body-indent: paragraph.enum-body-indent)
  set list(indent: paragraph.list-indent, body-indent: paragraph.list-body-indent)

  body

  if bib-file != none {
    pagebreak(weak: true)
    let bib-title = if lang == "id" { [DAFTAR PUSTAKA] } else { [BIBLIOGRAPHY] }
    heading(level: 1, numbering: none)[#bib-title]
    bibliography(bib-file, title: none, style: bib-style)
  }
}
