import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor


def load_data(file_path, column_names=None, sep=','):
    data = pd.read_csv(file_path, names=column_names, sep=sep)
    return data


def preprocess_data(data, target_column):
    X = data.drop(target_column, axis=1)
    y = data[target_column]

    for col in X.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))

    if y.dtype == 'object':
        le = LabelEncoder()
        y = le.fit_transform(y.astype(str))

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    return X_train, X_val, y_train, y_val


def get_models(task_type='classification'):
    if task_type == 'classification':
        return {
            'Random Forest': RandomForestClassifier(random_state=42),
            'XGBoost': XGBClassifier(
                use_label_encoder=False,
                eval_metric='logloss',
                random_state=42
            ),
            'LightGBM': LGBMClassifier(random_state=42)
        }
    else:
        return {
            'Random Forest': RandomForestRegressor(random_state=42),
            'XGBoost': XGBRegressor(random_state=42),
            'LightGBM': LGBMRegressor(random_state=42)
        }
