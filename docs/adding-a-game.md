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

   `tags` are kept as metadata; they are not shown in the README.

4. Record a gameplay GIF (optional, see [Gameplay GIFs](#gameplay-gifs)):

   ```sh
   scripts/record-demos.sh rs-example
   ```

5. Regenerate the catalog and commit everything together:

   ```sh
   python3 scripts/gen_catalog.py
   git add .gitmodules games/rs-example games.toml README.md README.ja.md \
     demos/rs-example.tape docs/assets/games/rs-example.gif
   git commit -m "Add rs-example"
   ```

The order of entries in `games.toml` is the order of the tables in the README.

## The catalog generator

`scripts/gen_catalog.py` reads `games.toml` and rewrites the region between the `<!-- BEGIN:games ... -->` and `<!-- END:games -->` markers in `README.md` and `README.ja.md`. Do not edit the tables by hand; edit `games.toml` and re-run the script.

The Preview column shows `docs/assets/games/<key>.gif` when that file exists, and `—` otherwise.

It also validates the catalog: required fields, duplicate keys, the key format, and that every entry has a matching submodule at `games/<key>` in `.gitmodules` (and vice versa).

| Option | Description |
|---|---|
| `--check` | Do not write; exit with 1 and show a diff if the READMEs are out of date |
| `--root <DIR>` | Repository root (default: the parent of `scripts/`) |

## Gameplay GIFs

The GIFs in the README are recorded with [VHS](https://github.com/charmbracelet/vhs) from the game's own replay mode, so they are reproducible: re-run the recording whenever a game's screen changes.

Each game has a tape at `demos/<key>.tape`. It replays one of the game's sample records in English and stops on the final position:

```text
Output docs/assets/games/rs-example.gif
Set Shell "bash"
Set FontSize 14
Set Width 900
Set Height 520
Set Padding 10
Set TypingSpeed 0
Hide
Type "clear && games/rs-example/target/release/rs-example --lang en replay games/rs-example/examples/records/sample.rec --interval 900"
Enter
Sleep 300ms
Show
Sleep 12s
```

- `Output` must be a path relative to the repository root.
- Set `Width` and `Height` large enough for the terminal size the game needs.
- Do not pass `--exit-on-end`: the GIF would end on an empty shell. Instead, set the last `Sleep` to the playback time plus about 3.5 s, so the final position stays on screen before the GIF loops. Check the last frame after recording.

Record every game, or only the ones you name:

```sh
scripts/record-demos.sh                   # every game with a tape
scripts/record-demos.sh rs-nim rs-gomoku  # only these
```

The script builds each game with `cargo build --release --locked`, runs `vhs` on its tape and regenerates the README tables. It needs `vhs` on `PATH`.

## Removing a game

```sh
git submodule deinit -f games/rs-example
git rm -f games/rs-example
rm -rf .git/modules/games/rs-example
```

Then delete its entry from `games.toml` along with `demos/rs-example.tape` and `docs/assets/games/rs-example.gif`, run `python3 scripts/gen_catalog.py` and commit.
