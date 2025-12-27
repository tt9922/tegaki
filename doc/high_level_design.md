# 概要設計書 (High-Level Design)

## 1. システムアーキテクチャ
本アプリケーションは、ブラウザ上で動作するSingle Page Application (SPA) である。
Fletの技術を用いてPythonで記述され、Pyodide (WebAssembly) 上で実行される。サーバーサイド処理は持たず、すべての計算（描画処理、AI推論）はクライアントサイドで完結する。

### アーキテクチャ図
[User] <--> [Flet Web App (WASM)]
                  |
                  +-- [UI Layer] (Canvas, Buttons, Text)
                  |
                  +-- [Logic Layer] (Events, Preprocessing)
                  |
                  +-- [AI Model] (Scikit-learn MLP / mnist_model.pkl)

## 2. コンポーネント構成

### 2.1 UI Layer (View)
- **MainPage**: アプリケーションのメイン画面。
  - **CanvasView**: ユーザーが手書きを行う領域。`ft.GestureDetector` と `ft.CustomPaint` (または `ft.Canvas` & `ft.cv.Path`) を組み合わせて線を描画する。
  - **ControlPanel**: 「判定」「クリア」などのボタン群。
  - **ResultDisplay**: 判定結果（数字）と確信度を表示するエリア。

### 2.2 Logic Layer (Controller)
- **CanvasController**:
  - ユーザーのドラッグ操作 (on_pan_update) を検知し、座標点リストを記録する。
  - 画面上の線を更新し、視覚的なフィードバックを行う。
- **ImageProcessor**:
  - 記録された座標点リストから、28x28ピクセルのグレースケール画像を生成する。
  - MNISTデータセットと同様の形式（黒背景・白文字、センタリング、リサイズ）に正規化する。
- **Predictor**:
  - 学習済みモデル (`.pkl`) を読み込む（初回のみ）。
  - 生成された画像データをモデルに入力し、予測クラス（数字）を取得する。

### 2.3 Data / Model Layer
- **Model File**: `mnist_model.pkl`
  - Scikit-learnの `MLPClassifier` (多層パーセプトロン) で学習させたモデル。
  - 軽量であり、Pyodide環境でも標準的に動作する。
  - アプリ起動時または初回判定時に非同期で読み込まれる。

## 3. データフロー

1. **描画**: ユーザーがCanvas上でドラッグ -> 座標データ `[(x1,y1), (x2,y2)...]` がメモリに蓄積される。UIに線が描画される。
2. **トリガー**: 「判定」ボタン押下。
3. **前処理**:
   - 座標データを元に、仮想的な28x28のグリッド（Numpy配列）に線を再現（ラスタライズ）。
   - 文字のバウンディングボックスを特定し、中心に移動・リサイズ（MNIST形式への合わせ込み）。
   - 値を0.0〜1.0に正規化し、1次元配列にフラット化。
4. **推論**: 正規化データをモデルに入力 -> 確率分布を出力。
5. **表示**: 最高確率の数字を画面に表示。

## 4. 技術選定の理由
- **Flet**: PythonのみでモダンなUIを構築でき、GitHub Pagesへのデプロイも容易なため。
- **Scikit-learn**:
  - Flet (Pyodide) での動作実績がある。
  - MNISTのような単純なタスクでは、重厚なDeep Learningフレームワーク（TensorFlow/PyTorch）を用いずとも、軽量なMLPやSVMで十分な精度（95%以上）が出せるため。
  - `.pkl` ファイル一つでモデル配布ができ、管理が容易。
