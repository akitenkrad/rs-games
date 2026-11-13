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

   `tags` はメタデータとして残していますが，README には表示しません．

4. プレイの様子の GIF を録画します（任意．[プレイの様子の GIF](#プレイの様子の-gif) を参照）．

   ```sh
   scripts/record-demos.sh rs-example
   ```

5. 一覧を作り直し，まとめてコミットします．

   ```sh
   python3 scripts/gen_catalog.py
   git add .gitmodules games/rs-example games.toml README.md README.ja.md \
     demos/rs-example.tape docs/assets/games/rs-example.gif
   git commit -m "Add rs-example"
   ```

README の表は `games.toml` の記載順に並びます．

## 一覧の生成スクリプト

`scripts/gen_catalog.py` は `games.toml` を読み，`README.md` と `README.ja.md` の `<!-- BEGIN:games ... -->` と `<!-- END:games -->` の間を書き換えます．表は手で編集せず，`games.toml` を直してスクリプトを再実行してください．

「プレイの様子」の列には，`docs/assets/games/<key>.gif` があればその GIF を，なければ `—` を表示します．

あわせて一覧を検査します．必須フィールド，key の重複，key の書式，そして各エントリに対応するサブモジュールが `.gitmodules` の `games/<key>` にあるか（逆も）を確かめます．

| オプション | 説明 |
|---|---|
| `--check` | 書き込まず，README が古ければ差分を表示して終了コード 1 で終わる |
| `--root <DIR>` | リポジトリのルート（既定: `scripts/` の親） |

## プレイの様子の GIF

README の GIF は，各ゲームのリプレイ機能で棋譜を再生し，[VHS](https://github.com/charmbracelet/vhs) で録画しています．何度でも同じ GIF を作れるので，ゲームの画面が変わったら録画し直してください．

ゲームごとに `demos/<key>.tape` を置きます．サンプル棋譜の 1 つを英語の画面で再生し，最終局面で止めます．

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

- `Output` はリポジトリのルートからの相対パスで書きます．
- `Width` と `Height` は，ゲームが必要とする端末サイズに足りる大きさにします．
- `--exit-on-end` は付けません．付けると GIF が空のシェルで終わります．代わりに最後の `Sleep` を「再生にかかる時間 + 3.5 秒ほど」にして，最終局面を表示したまま GIF がループするようにします．録画後は最後のフレームを確かめてください．

全ゲーム，または指定したゲームだけを録画します．

```sh
scripts/record-demos.sh                   # every game with a tape
scripts/record-demos.sh rs-nim rs-gomoku  # only these
```

スクリプトは各ゲームを `cargo build --release --locked` でビルドし，tape に対して `vhs` を実行して，README の表を作り直します．`PATH` に `vhs` が必要です．

## ゲームの削除

```sh
git submodule deinit -f games/rs-example
git rm -f games/rs-example
rm -rf .git/modules/games/rs-example
```

その後 `games.toml` から該当エントリを，`demos/rs-example.tape` と `docs/assets/games/rs-example.gif` とあわせて消し，`python3 scripts/gen_catalog.py` を実行してコミットします．
