# 詳細設計書 (Detailed Design)

## 1. ディレクトリ構成
```
tegaki/
├── assets/
│   └── mnist_model.pkl   # 学習済みモデルファイル (生成物)
├── docs/
│   ├── requirements.md
│   ├── high_level_design.md
│   └── detailed_design.md
├── src/
│   ├── main.py           # アプリ本体
│   └── train.py          # モデル学習用スクリプト (ローカル実行用)
└── requirements.txt      # 依存ライブラリ
```

## 2. モジュール詳細

### 2.1 src/train.py (学習スクリプト)
ローカル環境で実行し、モデルファイル `assets/mnist_model.pkl` を生成する。

- **主な処理**:
  1. `sklearn.datasets.fetch_openml('mnist_784')` でデータを取得。
  2. データを0-255から0.0-1.0に正規化。
  3. `sklearn.neural_network.MLPClassifier` を定義。
     - hidden_layer_sizes=(100,)
     - activation='relu'
     - solver='adam'
  4. モデルを学習 (`fit`)。
  5. `joblib` または `pickle` を使用して `assets/mnist_model.pkl` に保存。

### 2.2 src/main.py (Webアプリ本体)

#### クラス構成 / 主要コンポーネント

##### `State` クラス (状態管理)
描画されたストロークの情報を保持する。
- `points`: `List[List[float]]` (x, y座標のリストのリスト。各リストが一筆書きに対応)
- `current_stroke`: `List[float]` (現在描画中のストローク)

##### `main(page: ft.Page)` 関数
アプリケーションのエントリーポイント。

- **UIコンポーネント**:
  - `ft.GestureDetector`:
    - `on_pan_start`: 新しいストローク書き始め。`State` に新規リスト追加。
    - `on_pan_update`: ドラッグ中の座標 (`e.local_x`, `e.local_y`) を取得し、現在のストロークに追加。Canvasを再描画。
    - `on_pan_end`: ストローク終了処理。
  - `ft.Canvas` (または `ft.Stack` + `ft.cv.Canvas`):
    - `shapes`: `State.points` に基づいて `ft.cv.Path` (線) オブジェクトのリストを生成して描画する。
    - `Paint`: `stroke_width=10`, `color=ft.colors.BLACK`, `style=ft.PaintingStyle.STROKE`
  - `PredictButton`: `on_click` で判定処理を実行。
  - `ClearButton`: `on_click` で `State` をクリアし、Canvasをリセット。

#### その他の関数

##### `run_prediction(state: State) -> (int, float)`
1. **ラスタライズ (Rasterization)**:
   - 28x28 のゼロ初期化 `numpy.array` を作成。
   - `cv2.line` (または `skimage.draw.line` / 手動実装) を使用して、`State.points` の座標を配列上に描画する。
   - **注意**: 画面座標(例えば300x300)から28x28へ縮小変換が必要。
   - 太さを考慮し、線を描画する（太さがないと細すぎて認識精度が落ちる）。
2. **重心補正とクロッピング**:
   - 文字領域（0以外の値がある範囲）を切り出し。
   - 20x20にアスペクト比保持でリサイズ。
   - 28x28の中心に配置。
3. **推論**:
   - `joblib.load` でモデルをロード（初回のみキャッシュ）。
   - `model.predict_proba` で確率取得。
   - 最も高い確率のクラスと、その確率値を返す。

## 3. データ処理詳細

### 3.1 座標から画像への変換 (Processing Pipeline)
Web上(Pyodide)でのOpenCV (`cv2`) の利用は、`opencv-python` が重いため避ける場合があるが、`opencv-python-headless` が使えるか、あるいは `Pillow` と `numpy` で代用する。
今回は軽量化のため **Pillow (PIL)** を推奨する。

1. **PIL Image作成**: `Image.new("L", (300, 300), 0)` で黒背景作成。
2. **描画**: `ImageDraw.Draw` で座標間を線で結ぶ (`width=15`程度)。
3. **リサイズ・加工**:
   - `image.getbbox()` で文字範囲取得・切り出し。
   - 長辺に合わせて縮小 (20px程度)。
   - 28x28の背景にペースト (センタリング)。
4. **配列化**: `np.array(image)` で正規化 (0.0-1.0)。

## 4. GitHub Actions (デプロイフロー)
- `.github/workflows/deploy.yml`
- Fletの `flet publish` コマンドを使用。
- `gh-pages` ブランチに静的ファイル (WASM) をプッシュ。
