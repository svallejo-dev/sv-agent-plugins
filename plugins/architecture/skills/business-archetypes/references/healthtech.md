# Healthtech

**Analogy:** a medical records archive with a gatekeeper. What matters is not the speed of the corridors, but that only those who should get in, that who looked at what is recorded and that the file is never lost or mixed up.

## Dominant forces

- **Privacy and health data regulation**: HIPAA in the United States; in Colombia, Law 1581 of 2012 on personal data protection and the medical records regulations. Check the regulation in force in each country.
- **Auditing and consent**: who accessed which data, when and with what permission from the patient.
- **Integration with clinical third parties**: insurers, laboratories, providers, with standards such as HL7 FHIR and legacy systems.
- **Availability in critical flows** (telemedicine, prescriptions), even if the volume is moderate.

## Shape of the load (without metrics)

- Moderate volume, with peaks during care hours and campaigns (vaccination, respiratory illness seasons).
- Heavy media in some flows (images, video consultations).
- Scenarios to explore: 1k, 100k and 10M registered patients, with a small fraction active at once.

## Invariants and consistency

- No clinical data accessible without authorization; least privilege and explicit consent.
- An immutable audit log of accesses and changes.
- The medical record is not overwritten: it is versioned and annotated.
- Correct patient identity (avoid mixing two people's records).

## Typical subdomains

- **Core**: the health service that brings value (telemedicine, patient management, triage, care programs).
- **Supporting**: scheduling and appointments, medical records, billing to insurers, interoperability.
- **Generic**: video calls, messaging, identity, encrypted storage.

## Path already walked (check before citing)

- HL7 FHIR as the interoperability standard for clinical data.
- Encryption at rest and in transit, with key management and segregation of sensitive data.
- Separating identifiable data from clinical data (pseudonymization) for analytics.

## Typical failure modes (seed for the red team)

- Improper access to data through overly broad permissions or an uncontrolled endpoint.
- Logs or metrics that leak health data.
- An integration with a clinical third party down in a critical flow.
- Mixed records because of a patient identity error.
- Video consultations degrading at peak hours.

## Questions that change the design

- Which regulation applies in each country where the product operates?
- Which data is clinical and which is administrative? Who can see each?
- Which third parties must be integrated, and with which standard?
- Which flows are critical for patient safety?

## Hypotheses for a PoC

- Validate the permissions and consent model with negative cases (who must not see what).
- Validate the integration with the most critical clinical third party in its test environment.
- Instrument without sensitive data: access auditing, latency of critical flows, integration errors. Design the telemetry so it never contains health data.
