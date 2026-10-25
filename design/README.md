# design/ — Designer reference material

This folder is the assets repo's **reference zone**: art bibles, palettes,
concept boards, role notes — everything the Designer works from and the
Owner wants versioned. Nothing here ships and nothing here loads: no
manifest references it, no client reads it, and no release archive
packages it.

Per Standing Orders v1.4 the Owner commits this folder **directly** — no
Programmer brief, no verified client load. (The repo's pre-existing
reference folders — `art-bible/`, `concepts/`, `icons/`, `roles/` — carry
the same understanding; whether they fold into `design/` is the Owner's
call, not a Programmer's.)

Anything the client should actually **load** lives in a pack directory
(`default/` or another pack) and enters only through a Programmer brief
and a verified client load: the Designer delivers to the Owner, the Owner
relays the brief, the Programmer commits, and the release pipeline's
packaged smoke (or the dev run's `asset pack '...' loaded` line) proves
the load. Reference material that wants to ship moves from here into a
pack through that same path.
