# Authentication in front of the shared server instance

## WHAT

Require a login before anyone can reach the class's shared `strictdoc
server` instance. This is a deployment change, not a change to this
repository's code.

## WHY

`strictdoc/server` has no authentication layer: a repo-wide search turns up
no login, session, or credential-checking code anywhere in it, and the
Backlog itself lists `SDOC-SRS-130 "User accounts"` as `STATUS: Backlog`,
meaning upstream has not built this either. Building an authentication layer
into StrictDoc itself would be a much larger effort than the class needs; a
reverse proxy in front of the existing server solves the actual problem
(only enrolled students and mentors can reach the instance) without touching
StrictDoc's code at all.

## HOW

Run `strictdoc server` as today, bound to a local address, and put a
reverse proxy in front of it that the class actually reaches:

- Caddy or nginx with HTTP Basic Auth is the simplest option for a small,
  fixed class roster: one shared or per-student credential, configured once
  per term.
- An OAuth2 proxy (for example oauth2-proxy) in front of the same server is
  a better fit if the school already has an identity provider (Google
  Workspace, Microsoft 365, or a campus SSO) and wants students to sign in
  with their existing account rather than a separate password.

Either way, the proxy terminates the login and forwards authenticated
traffic to `strictdoc server`'s local port; StrictDoc itself never sees
credentials.

### Deferred work

Per-user permissions inside StrictDoc (for example, restricting who can
edit which document) are out of scope here. The Backlog's "User accounts"
item covers that, and it is unimplemented upstream; this task only gates
access to the instance as a whole.
