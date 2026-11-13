**English** | [日本語](adding-a-game.ja.md)

# Adding a game

## Naming

A game is identified by its **key**, which is at the same time:

- the GitHub repository name (`https://github.com/akitenkrad/<key>`),
- the submodule path (`games/<key>`),
- the `key` field in `games.toml`.

Keys are kebab-case and start with `rs-`, e.g. `rs-nim`.

## Requirements for a game repository

- A public repository whose root is a Cargo package (`Cargo.toml` and a committed `Cargo.lock`).
- `cargo test --locked` passes — CI runs it for every game.
- A README that explains how to play. A minimal README with details under `docs/`, in English with a Japanese translation, matches the existing games.
- Its own license file.

## Steps

1. Create the game's repository and push it to GitHub.
2. In rs-games, run:

   ```sh
   scripts/add-game.sh rs-example
   ```

   This adds `https://github.com/akitenkrad/rs-example.git` as a submodule at `games/rs-example`, appends a stub entry to `games.toml` and regenerates the README tables. Pass a second argument to use a different URL.

3. Fill in the `TODO` fields of the new entry in `games.toml`:

   ```toml
   [[games]]
   key = "rs-example"
   title = "Example"
   title_ja = "例"
   summary = "One sentence in English."
   summary_ja = "日本語で 1 文．"
   tags = ["puzzle", "ratatui"]
   ```

4. Regenerate the catalog and commit everything together:

   ```sh
   python3 scripts/gen_catalog.py
   git add .gitmodules games/rs-example games.toml README.md README.ja.md
   git commit -m "Add rs-example"
   ```

The order of entries in `games.toml` is the order of the tables in the README.

## The catalog generator

`scripts/gen_catalog.py` reads `games.toml` and rewrites the region between the `<!-- BEGIN:games ... -->` and `<!-- END:games -->` markers in `README.md` and `README.ja.md`. Do not edit the tables by hand; edit `games.toml` and re-run the script.

It also validates the catalog: required fields, duplicate keys, the key format, and that every entry has a matching submodule at `games/<key>` in `.gitmodules` (and vice versa).

| Option | Description |
|---|---|
| `--check` | Do not write; exit with 1 and show a diff if the READMEs are out of date |
| `--root <DIR>` | Repository root (default: the parent of `scripts/`) |

## Removing a game

```sh
git submodule deinit -f games/rs-example
git rm -f games/rs-example
rm -rf .git/modules/games/rs-example
```

Then delete its entry from `games.toml`, run `python3 scripts/gen_catalog.py` and commit.
