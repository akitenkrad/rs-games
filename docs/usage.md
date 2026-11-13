**English** | [日本語](usage.ja.md)

# Working with this repository

## Layout

```text
rs-games/
├── games.toml              # the list of games (single source of truth for the catalog)
├── games/
│   └── rs-nim/             # one Git submodule per game
├── scripts/
│   ├── gen_catalog.py      # regenerates the game tables in README.md / README.ja.md
│   └── add-game.sh         # adds a game as a submodule and registers it
└── .github/workflows/ci.yml
```

This repository is **not** a Cargo workspace. Each game keeps its own `Cargo.toml` and `Cargo.lock` and builds exactly as it does in its own repository.

## Cloning

```sh
git clone --recursive https://github.com/akitenkrad/rs-games
```

Or, after a plain clone:

```sh
git submodule update --init --recursive
```

## Running a game

From the repository root:

```sh
cargo run --release --manifest-path games/rs-nim/Cargo.toml
```

Arguments after `--` go to the game, for example:

```sh
cargo run --release --manifest-path games/rs-nim/Cargo.toml -- replay games/rs-nim/examples/records/classic-1357.nimrec
```

Or work inside the game's directory as usual (`cd games/rs-nim && cargo run --release`). Each game's README documents its own controls and options.

## Updating the games

A submodule records a specific commit of each game. To move every game to the latest commit on its default branch:

```sh
git submodule update --remote
git add games
git commit -m "Update games"
```

To update just one game, pass its path: `git submodule update --remote games/rs-nim`.

## Developing a game

Work on a game in its own repository (or inside `games/<key>`, which is a full clone). Commit and push there first; then record the new commit here with `git add games/<key>` and commit in rs-games.

## Continuous integration

`.github/workflows/ci.yml` runs on every push and pull request to `main`:

- **catalog** — runs the tests in `tests/`, then `python3 scripts/gen_catalog.py --check` fails if the README tables are out of date with `games.toml`, or if `games.toml` and `.gitmodules` disagree.
- **games** — checks out all submodules and runs `cargo test --locked` in every game.
