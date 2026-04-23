# If this repo gets a DMCA takedown notice

Template for maintainers to respond thoughtfully. **Not legal advice.**
Consult a lawyer if you receive a notice.

## Anatomy of a DMCA §512 notice on GitHub

1. You'll receive an email from GitHub's DMCA team with the claim.
2. GitHub disables the repo within a few business hours by default.
3. You have two paths: let it stand, or file a **counter-notice**.

## When to file a counter-notice

Consider it if all of the following are true:

- This project contains **no binary or source copy** of the IM client
  itself.
- This project contains **no trade-secret, confidential, or
  reverse-engineered specifications** that weren't already publicly
  documented.
- This project **doesn't redistribute** the claimant's encryption keys,
  credentials, or cryptographic material as a product — it helps the
  end-user retrieve their own.
- The project's documented purpose is **data portability for the user's
  own data**, a right widely recognized by data-protection regulators
  (GDPR Article 20, PIPL Article 45, CCPA).

## Counter-notice skeleton (English)

```
I am the author and maintainer of the GitHub repository at
<https://github.com/{owner}/{repo}>. I have a good-faith belief that
the material was removed as a result of mistake or misidentification.

The repository does not redistribute any proprietary source code,
binaries, assets, or trade secrets of the complainant. It is a
personal-data-portability tool that helps end users obtain a
machine-readable copy of their own chat data from their own logged-in
account on their own devices — an activity recognized as lawful under
data-protection regimes including GDPR Article 20, CCPA, and PIPL
Article 45.

The repository explicitly disclaims use against third-party accounts
or devices (see DISCLAIMER.md). It ships no circumvention tool
primarily designed to infringe copyright within the meaning of 17
U.S.C. § 1201(a)(2).

I consent to the jurisdiction of the U.S. District Court for the
district in which my address is located, or if outside the United
States, the Northern District of California.

Signed,
{name}
{address}
{phone}
{email}
```

## Before filing

1. Save a tarball of the repo locally.
2. Mirror the repo to [Codeberg](https://codeberg.org), SourceHut, or a
   self-hosted Gitea so users retain access during the 14-day wait.
3. Add a banner on your personal homepage with the mirror URL.
4. Tweet / post the mirror URL so it gets indexed before any new
   takedown.

## If you choose not to counter-notice

- Leave the repo disabled. GitHub will eventually remove it.
- Publish the mirror(s).
- Consider moving future development to a jurisdiction-independent
  forge.

## Prevention

- Keep the repo **documentation-heavy, code-light**. Most of this
  toolkit is reference implementations of public specs + polyglot docs.
- Never include: screenshots of the IM client's UI, strings copied from
  its binary, hardcoded function offsets, proprietary icon art, or
  direct mentions of the claimant company's trademarks except in
  neutral technical context.
- Use generic names for variables, CLI flags, and docs ("the client",
  "the app") — don't put the brand name in command names or environment
  variables.

## Helpful links

- [EFF: Coders' Rights Project](https://www.eff.org/issues/coders)
- [GitHub's DMCA process](https://docs.github.com/en/site-policy/content-removal-policies/dmca-takedown-policy)
- [SecurityResearchPolicy.org](https://disclose.io/)
