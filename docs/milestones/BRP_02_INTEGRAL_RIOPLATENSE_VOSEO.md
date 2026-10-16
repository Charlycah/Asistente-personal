# BRP.02 — Integral Rioplatense Voseo

## Objective

Refine ROBY's visible Spanish so companion responses consistently use
Rioplatense voseo without adding architectural layers or modifying technical
content.

## Behavioral scope

The expression policy now normalizes common second-person forms, including
pronouns, present-tense verbs, and frequent imperatives. Examples include
`tu eres` to `vos sos`, `para ti` to `para vos`, `puedes` to `podes`,
`quieres` to `queres`, `dime` to `decime`, and `cuentame` to `contame`.

Inline code and fenced code remain byte-for-byte unchanged. Intent matching,
identifiers, APIs, commands, and internal architecture are outside this
refinement.

## Verification

Focused regression tests cover extended voseo, pronouns and imperatives, and
protected technical literals.
