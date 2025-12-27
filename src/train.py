import os
import joblib
from sklearn.datasets import fetch_openml
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_model():
    print("Fetching MNIST data...")
    # MNISTデータの取得 (70000件)
    X, y = fetch_openml('mnist_784', version=1, return_X_y=True, as_frame=False)
    
    # ピクセル値を 0-255 から 0.0-1.0 に正規化
    X = X / 255.0

    # 訓練用とテスト用に分割
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # MLP (多層パーセプトロン) モデルの定義
    # 精度向上のために隠れ層を増やし、学習回数(max_iter)を増加
    print("Training MLP Classifier (Enhanced)...")
    mlp = MLPClassifier(
        hidden_layer_sizes=(256, 128),  # より表現力のあるネットワーク構造
        max_iter=50,  # イテレーション数を増やして収束させる
        alpha=1e-4,
        solver='adam', 
        verbose=10, 
        random_state=1,
        learning_rate_init=0.001 # 標準的な学習率に変更
    )

    # 学習実行
    mlp.fit(X_train, y_train)

    # 精度確認
    print("Evaluating model...")
    y_pred = mlp.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Test Set Accuracy: {accuracy:.4f}")

    # モデルの保存
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    model_path = os.path.join(assets_dir, "mnist_model.pkl")
    
    print(f"Saving model to {model_path}...")
    joblib.dump(mlp, model_path)
    print("Model saved successfully.")

if __name__ == "__main__":
    train_model()
