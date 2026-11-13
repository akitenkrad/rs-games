[English](adding-a-game.md) | **日本語**

# ゲームの追加

## 命名

ゲームは **key** で識別します．key は次の 3 つを兼ねます．

- GitHub のリポジトリ名（`https://github.com/akitenkrad/<key>`）
- サブモジュールのパス（`games/<key>`）
- `games.toml` の `key` フィールド

key は `rs-` で始まる kebab-case です．例: `rs-nim`．

## ゲームのリポジトリに求めること

- 公開リポジトリで，ルートが Cargo パッケージであること（`Cargo.toml` と，コミット済みの `Cargo.lock`）．
- `cargo test --locked` が通ること．CI がすべてのゲームで実行します．
- 遊び方を説明する README があること．既存のゲームに合わせるなら，README は最小限にして詳細を `docs/` に置き，英語と日本語訳をそろえます．
- 独自のライセンスファイルがあること．

## 手順

1. ゲームのリポジトリを作り，GitHub に push します．
2. rs-games で次を実行します．

   ```sh
   scripts/add-game.sh rs-example
   ```

   `https://github.com/akitenkrad/rs-example.git` を `games/rs-example` にサブモジュールとして追加し，`games.toml` に雛形のエントリを追記して，README の表を作り直します．別の URL を使うときは 2 つ目の引数に渡します．

3. `games.toml` に追記されたエントリの `TODO` を埋めます．

   ```toml
   [[games]]
   key = "rs-example"
   title = "Example"
   title_ja = "例"
   summary = "One sentence in English."
   summary_ja = "日本語で 1 文．"
   tags = ["puzzle", "ratatui"]
   ```

4. 一覧を作り直し，まとめてコミットします．

   ```sh
   python3 scripts/gen_catalog.py
   git add .gitmodules games/rs-example games.toml README.md README.ja.md
   git commit -m "Add rs-example"
   ```

README の表は `games.toml` の記載順に並びます．

## 一覧の生成スクリプト

`scripts/gen_catalog.py` は `games.toml` を読み，`README.md` と `README.ja.md` の `<!-- BEGIN:games ... -->` と `<!-- END:games -->` の間を書き換えます．表は手で編集せず，`games.toml` を直してスクリプトを再実行してください．

あわせて一覧を検査します．必須フィールド，key の重複，key の書式，そして各エントリに対応するサブモジュールが `.gitmodules` の `games/<key>` にあるか（逆も）を確かめます．

| オプション | 説明 |
|---|---|
| `--check` | 書き込まず，README が古ければ差分を表示して終了コード 1 で終わる |
| `--root <DIR>` | リポジトリのルート（既定: `scripts/` の親） |

## ゲームの削除

```sh
git submodule deinit -f games/rs-example
git rm -f games/rs-example
rm -rf .git/modules/games/rs-example
```

その後 `games.toml` から該当エントリを消し，`python3 scripts/gen_catalog.py` を実行してコミットします．
