import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

CSV_PATH = "data/stream.csv"
MODEL_PATH = "model.joblib"

def train_simple():
    df = pd.read_csv(CSV_PATH)
    # use raw sensor columns as features
    X = df[["motion","sound","temp"]]
    y = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    clf = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42)
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    print("Evaluation on test split:")
    print(classification_report(y_test, preds))
    joblib.dump(clf, MODEL_PATH)
    print("Saved model to", MODEL_PATH)

if __name__ == "__main__":
    train_simple()
