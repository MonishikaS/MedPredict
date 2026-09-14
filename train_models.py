import pandas as pd
import numpy as np
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score


# ============================================================
# EXHRA - AI HEALTH RISK ASSESSMENT SYSTEM
# MODEL TRAINING
# ============================================================

print("\n==============================================")
print("       EXHRA MODEL TRAINING")
print("==============================================\n")


# ------------------------------------------------------------
# Create models folder
# ------------------------------------------------------------

os.makedirs("models", exist_ok=True)


# ------------------------------------------------------------
# Models
# ------------------------------------------------------------

def get_models():

    return {
        "Logistic Regression": LogisticRegression(max_iter=2000),
        "SVM": SVC(probability=True),
        "KNN": KNeighborsClassifier(n_neighbors=5),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            random_state=42
        ),
        "XGBoost": XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            random_state=42,
            eval_metric="logloss"
        )
    }


# ============================================================
# DIABETES
# ============================================================

def train_diabetes():

    print("\n")
    print("==============================================")
    print("DIABETES MODEL")
    print("==============================================")

    data = pd.read_csv("data/diabetes.csv")

    # Clean column names
    data.columns = data.columns.str.strip().str.lower()

    # -----------------------------
    # TARGET
    # -----------------------------

    data["class"] = data["class"].astype(str).str.strip().str.lower()

    data["class"] = data["class"].map({
        "positive": 1,
        "negative": 0
    })

    y = data["class"].astype(int)

    # -----------------------------
    # FEATURES
    # -----------------------------

    X = data.drop(columns=["class"]).copy()

    # Convert categorical columns
    categorical_columns = [
        "gender",
        "polyuria",
        "polydipsia",
        "sudden weight loss",
        "weakness",
        "polyphagia",
        "genital thrush",
        "visual blurring",
        "itching",
        "irritability",
        "delayed healing",
        "partial paresis",
        "muscle stiffness",
        "alopecia",
        "obesity"
    ]

    for column in categorical_columns:

        X[column] = (
            X[column]
            .astype(str)
            .str.strip()
            .str.lower()
            .map({
                "yes": 1,
                "no": 0,
                "male": 1,
                "female": 0
            })
        )

    # Age is numeric
    X["age"] = pd.to_numeric(
        X["age"],
        errors="coerce"
    )

    print("\nMissing values:")
    print(X.isna().sum())

    # -----------------------------
    # TRAIN / TEST SPLIT
    # -----------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    # -----------------------------
    # MODELS
    # -----------------------------

    models = get_models()

    trained_models = {}

    for name, model in models.items():

        pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", model)
        ])

        pipeline.fit(X_train, y_train)

        probabilities = pipeline.predict_proba(X_test)[:, 1]

        predictions = (probabilities >= 0.5).astype(int)

        accuracy = accuracy_score(
            y_test,
            predictions
        )

        precision = precision_score(
            y_test,
            predictions,
            zero_division=0
        )

        recall = recall_score(
            y_test,
            predictions,
            zero_division=0
        )

        f1 = f1_score(
            y_test,
            predictions,
            zero_division=0
        )

        auc = roc_auc_score(
            y_test,
            probabilities
        )

        print(f"\n{name}")
        print(f"Accuracy : {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall   : {recall:.4f}")
        print(f"F1 Score : {f1:.4f}")
        print(f"ROC-AUC  : {auc:.4f}")

        trained_models[name] = pipeline

    # -----------------------------
    # SAVE MODELS
    # -----------------------------

    joblib.dump(
        trained_models,
        "models/diabetes_models.pkl"
    )

    joblib.dump(
        list(X.columns),
        "models/diabetes_features.pkl"
    )

    print("\nDiabetes models saved successfully!")

# ============================================================
# HEART DISEASE
# ============================================================

def train_heart():

    print("\n")
    print("==============================================")
    print("HEART DISEASE MODEL")
    print("==============================================")

    data = pd.read_csv("data/heart.csv")

    X = data.drop(columns=["target"])
    y = data["target"].astype(int)

    # Convert all columns to numeric
    X = X.apply(pd.to_numeric, errors="coerce")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    models = get_models()

    trained_models = {}

    for name, model in models.items():

        pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("model", model)
        ])

        pipeline.fit(X_train, y_train)

        probabilities = pipeline.predict_proba(X_test)[:, 1]

        predictions = (probabilities >= 0.5).astype(int)

        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions, zero_division=0)
        recall = recall_score(y_test, predictions, zero_division=0)
        f1 = f1_score(y_test, predictions, zero_division=0)
        auc = roc_auc_score(y_test, probabilities)

        print(f"\n{name}")
        print(f"Accuracy : {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall   : {recall:.4f}")
        print(f"F1 Score : {f1:.4f}")
        print(f"ROC-AUC  : {auc:.4f}")

        trained_models[name] = pipeline

    joblib.dump(
        trained_models,
        "models/heart_models.pkl"
    )

    joblib.dump(
        list(X.columns),
        "models/heart_features.pkl"
    )

    print("\nHeart disease models saved successfully!")


# ============================================================
# BREAST CANCER
# ============================================================
# ============================================================
# BREAST CANCER MODEL TRAINING
# ============================================================

def train_breast():

    print("\n")
    print("==============================================")
    print("BREAST CANCER MODEL")
    print("==============================================")

    data = pd.read_csv(
        "data/breast_cancer.csv"
    )

    # --------------------------------------------------------
    # Separate features and target
    # --------------------------------------------------------

    X = data.drop(
        columns=["target"]
    )

    y = data["target"].astype(int)

    # --------------------------------------------------------
    # Remove ID column if present
    # --------------------------------------------------------

    if "id" in X.columns:

        X = X.drop(
            columns=["id"]
        )

    # --------------------------------------------------------
    # Convert everything to numeric
    # --------------------------------------------------------

    X = X.apply(
        pd.to_numeric,
        errors="coerce"
    )

    # --------------------------------------------------------
    # SAVE EXACT FEATURE NAMES
    # --------------------------------------------------------

    breast_features = list(X.columns)

    print("\nFeatures used for training:")

    for feature in breast_features:

        print(" -", feature)

    # --------------------------------------------------------
    # Train / test split
    # --------------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(

        X,
        y,

        test_size=0.2,

        random_state=42,

        stratify=y
    )

    # --------------------------------------------------------
    # Get models
    # --------------------------------------------------------

    models = get_models()

    trained_models = {}

    # --------------------------------------------------------
    # Train every model
    # --------------------------------------------------------

    for name, model in models.items():

        print("\nTraining:", name)

        pipeline = Pipeline([

            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                )
            ),

            (
                "scaler",
                StandardScaler()
            ),

            (
                "model",
                model
            )
        ])

        # Train
        pipeline.fit(
            X_train,
            y_train
        )

        # ----------------------------------------------------
        # Predictions
        # ----------------------------------------------------

        probabilities = pipeline.predict_proba(
            X_test
        )[:, 1]

        predictions = (
            probabilities >= 0.5
        ).astype(int)

        # ----------------------------------------------------
        # Metrics
        # ----------------------------------------------------

        accuracy = accuracy_score(
            y_test,
            predictions
        )

        precision = precision_score(
            y_test,
            predictions,
            zero_division=0
        )

        recall = recall_score(
            y_test,
            predictions,
            zero_division=0
        )

        f1 = f1_score(
            y_test,
            predictions,
            zero_division=0
        )

        auc = roc_auc_score(
            y_test,
            probabilities
        )

        # ----------------------------------------------------
        # Print results
        # ----------------------------------------------------

        print(f"\n{name}")

        print(
            f"Accuracy : {accuracy:.4f}"
        )

        print(
            f"Precision: {precision:.4f}"
        )

        print(
            f"Recall   : {recall:.4f}"
        )

        print(
            f"F1 Score : {f1:.4f}"
        )

        print(
            f"ROC-AUC  : {auc:.4f}"
        )

        # ----------------------------------------------------
        # Store trained pipeline
        # ----------------------------------------------------

        trained_models[name] = pipeline

    # ========================================================
    # SAVE MODELS
    # ========================================================

    joblib.dump(
        trained_models,
        "models/breast_models.pkl"
    )

    # ========================================================
    # SAVE EXACT TRAINING FEATURES
    # ========================================================

    joblib.dump(
        breast_features,
        "models/breast_features.pkl"
    )

    print("\n==============================================")
    print("Breast cancer models saved successfully!")
    print("==============================================")

# ============================================================
# RUN EVERYTHING
# ============================================================

train_diabetes()
train_heart()
train_breast()

print("\n")
print("==============================================")
print("       ALL MODELS TRAINED SUCCESSFULLY")
print("==============================================")
print("\nModels are stored inside the models folder.")