#let layout(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 2.5cm, left: 2.5cm, right: 2.5cm),
  number-align: center,
  body,
) = {
  let set-margin = if margin == "print" {
    (top: 3cm, bottom: 3cm, left: 4cm, right: 3cm)
  } else {
    margin
  }
  set page(
    paper: paper,
    margin: set-margin,
    number-align: number-align,
  )

  body
}
