# Upcoming Medical Appointment → Consultation Preparation Offer

## Certified design candidate

The existing Reminder authority remains responsible for time, persistence, staged
awareness and delivery. The existing MedicalConsultationPreparationService remains
responsible for building a health-data summary only after an explicit conversational
request.

This seam adds one bounded presentation adapter:
`MedicalAppointmentConsultationOffer`.

It inspects only the already-visible reminder title/description. When the text contains
a bounded medical-appointment cue and exactly one named household member (Carlos or
Cristina), it appends an opt-in sentence offering the existing pre-consultation summary.

It does not read health repositories, prepare a summary, persist medical metadata,
create reminders, create calendar events, or authorize any medical action.

Ambiguous person or ambiguous medical semantics fail closed to the normal reminder
message.

Canonical boundary:

`Reminder → staged awareness → bounded medical cue → opt-in offer`

then, only after a human conversational request:

`MedicalConsultationPreparationService → confirmed local health data → summary`.
