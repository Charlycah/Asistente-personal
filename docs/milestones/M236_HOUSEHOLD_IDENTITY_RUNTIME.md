# M236 — Household Identity Runtime

ROBY treats Carlos and Cristina as one shared household identity. There is no private owner boundary between them.

The official runtime uses the `family-shared` profile and the owner label `Familia`. Reminder creation, listing, cancellation, snoozing, and resident delivery operate over the complete household set, including historical rows previously labelled for Carlos or Cristina.

Legacy owner fields remain in APIs and persistence only for backward compatibility. They do not restrict household access.
