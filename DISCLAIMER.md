# Disclaimer — Own Data Only

This toolkit exists as a **personal data portability helper**, grounded in
the broadly-recognized principle that individuals should be able to obtain
a machine-readable copy of data they have authored on their own devices.

## Intended use

- You run this against **your own logged-in account**,
- On **your own machine**, with
- **Your own** chat history, attachments, and contacts.

## Not intended use

- Accessing, exporting, decrypting, or redistributing **another person's**
  account, messages, photos, voice notes, or contact graph.
- Bulk-harvesting data from shared / company / customer-support
  terminals.
- Reselling or monetizing extracted content.
- Evading safety/moderation or corporate security controls on devices you
  do not own.

## Responsibility

You are solely responsible for ensuring your use of this software
complies with:

- The terms of service of the IM application you extract from,
- Applicable data-protection law in your jurisdiction (GDPR, PIPL, CCPA,
  etc.) — including any limits on retaining third-party personal data
  present in your own chat logs,
- Your employer's acceptable-use policy, if the account or device is
  employer-controlled,
- Any private agreements with conversation participants.

The authors and contributors provide this tool under the MIT license
"AS IS" with no warranty and assume no responsibility for how it is used.

## Data minimization recommendations

If you plan to **share, archive, or analyze** the output:

- Redact or hash third-party identifiers (wxid, phone numbers, real
  names) before committing or uploading anywhere.
- Store decrypted databases with at-rest encryption (e.g., FileVault) or
  on an encrypted disk image; don't push them to public repos or cloud
  storage.
- If you use an LLM to summarize, prefer a local model (ollama + qwen or
  equivalent) or a provider that doesn't retain inputs for training.
- Delete the decrypted copies when you're done with the analysis.

## Reporting issues

If you believe this software enabled misuse against you, please open a
GitHub issue or contact the maintainer. We will add additional warnings
or remove features as warranted.
