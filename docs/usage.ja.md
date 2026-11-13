[English](usage.md) | **日本語**

# リポジトリの使い方

## 構成

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

このリポジトリは Cargo workspace **ではありません**．各ゲームは自分の `Cargo.toml` と `Cargo.lock` を持ち，単独のリポジトリにあるときとまったく同じにビルドされます．

## clone

```sh
git clone --recursive https://github.com/akitenkrad/rs-games
```

`--recursive` 無しで clone した場合は，次を実行します．

```sh
git submodule update --init --recursive
```

## ゲームの実行

リポジトリのルートから実行する場合:

```sh
cargo run --release --manifest-path games/rs-nim/Cargo.toml
```

`--` の後ろはゲームに渡されます．例:

```sh
cargo run --release --manifest-path games/rs-nim/Cargo.toml -- replay games/rs-nim/examples/records/classic-1357.nimrec
```

ゲームのディレクトリに入って，いつもどおり作業してもかまいません（`cd games/rs-nim && cargo run --release`）．操作方法やオプションは各ゲームの README に書いてあります．

## ゲームの更新

サブモジュールは各ゲームの特定のコミットを記録しています．すべてのゲームを既定ブランチの最新コミットに進めるには，次を実行します．

```sh
git submodule update --remote
git add games
git commit -m "Update games"
```

1 つのゲームだけを更新するときは，パスを指定します: `git submodule update --remote games/rs-nim`．

## ゲームの開発

ゲームの開発は，そのゲームのリポジトリ（または完全な clone である `games/<key>` の中）で行います．先にそちらでコミットして push し，その後 rs-games 側で `git add games/<key>` してコミットし，新しいコミットを記録します．

## 継続的インテグレーション

`.github/workflows/ci.yml` は `main` への push と pull request のたびに動きます．

- **catalog** — `tests/` のテストを実行した後，`python3 scripts/gen_catalog.py --check` を実行します．README の表が `games.toml` とずれているとき，または `games.toml` と `.gitmodules` が食い違っているときに失敗します．
- **games** — すべてのサブモジュールを取得し，各ゲームで `cargo test --locked` を実行します．
