# pandemonium-assets

The official Pandemonium presentation asset packs. **This repo is art only**:
PNGs and the pack manifests that name them. It holds no code and it is never
hashed into the simulation (docs/adr/0200-authoritative-vs-presentation-data.md
in the main repo — two peers with different packs still produce identical
state hashes).

## Layout

```
default/                 <- the default pack (shipped in every release archive)
├── manifest.ron         pack_id "tactical_field", schema_version 1
├── README.md            the pack's own art-direction notes
└── textures/
    ├── terrain/         grass, gravel, rock, sand (512x512)
    └── entities/        worker, rifleman, raider, guardian, turret,
                         command_center, barracks, supply_depot (256x256)
```

`manifest.ron`'s `pack_id` stays `"tactical_field"`: the id names the art
style, while `default/` names the slot the client and the release archives
load it into (the client discovers a pack at `assets/packs/default/`).

## How the pack reaches a player or a dev

- **Developers** run `scripts/fetch-assets.sh` in the main repo
  ([E-Vex/pandemonium-bd](https://github.com/E-Vex/pandemonium-bd)): it clones
  or updates this repo and copies `default/` to
  `crates/client/assets/packs/default/` (gitignored there).
- **Releases**: the `release` workflow checks this repo out and packages
  `default/` into every archive at `assets/packs/default/`, next to the
  binary — discovery order #2 in the client. The packaged smoke fails if the
  pack does not load.

## Rules

- Art enters the **main** repo only through a Programmer brief (Standing
  Orders v1.3): the Designer delivers files to the Owner, who hands them to
  the Programmer, who commits them here.
- Manifest paths stay relative, forward slashes, inside the pack root —
  the client's pack loader rejects absolute paths, `..`, and pack escapes.
- PNGs are limited to 2048x2048 and 64 MiB per file (the loader's limits).
