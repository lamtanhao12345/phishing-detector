import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, roc_curve
from catboost import CatBoostClassifier  # Thay bằng CatBoost
import joblib
import numpy as np

# Đọc dữ liệu từ file CSV
data_path = "D:/CSUD/Data/PhiUSIIL_Phishing_URL_Dataset.csv"  # Cập nhật đường dẫn nếu cần
df = pd.read_csv(data_path)
X = df.drop(columns=['label'])
y = df['label']
print("Thông tin dataset: Số mẫu =", X.shape[0], "Số đặc trưng =", X.shape[1])

# Kiểm tra trùng lặp
duplicates = X.duplicated(keep=False).sum()
print(f"Số mẫu trùng lặp trong dataset: {duplicates}")
X = X.drop_duplicates()
y = y.loc[X.index]

# Kiểm tra giá trị thiếu
print("\nSố giá trị thiếu trong mỗi cột:\n", X.isna().sum())

# Xử lý giá trị thiếu
object_cols = X.select_dtypes(include=['object']).columns
for col in object_cols:
    X[col] = X[col].fillna(X[col].mode()[0])
X = X.fillna(X.select_dtypes(include=['float', 'int']).median())

# Kiểm tra cardinality
for col in object_cols:
    print(f"Cột {col}: {X[col].nunique()} giá trị duy nhất")

# Loại bỏ cột high cardinality
high_cardinality_cols = ['FILENAME', 'URL', 'Domain', 'TLD', 'Title']
X = X.drop(columns=high_cardinality_cols, errors='ignore')

# Xử lý cột boolean (chuyển thành 0/1 trực tiếp)
boolean_cols = ['IsDomainIP', 'HasObfuscation', 'IsHTTPS', 'HasTitle', 'HasFavicon', 
                'Robots', 'IsResponsive', 'HasDescription', 'HasExternalFormSubmit', 
                'HasSocialNet', 'HasSubmitButton', 'HasHiddenFields', 'HasPasswordField', 
                'Bank', 'Pay', 'Crypto', 'HasCopyrightInfo']
for col in boolean_cols:
    if col in X.columns:
        X[col] = X[col].astype(int)  # Giả sử dữ liệu đã là 0/1 hoặc True/False

# Chia dữ liệu thành train/val/test
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.667, random_state=42)
print(f"Kích thước tập train: {X_train.shape}")
print(f"Kích thước tập validation: {X_val.shape}")
print(f"Kích thước tập test: {X_test.shape}")

# Kiểm tra tương quan với nhãn
correlations = X_train.corrwith(y_train)
print("\nTương quan với nhãn:\n", correlations.sort_values(ascending=False))

# Loại bỏ đặc trưng có tương quan cao (>0.8 để chặt chẽ hơn)
suspicious_features = correlations[abs(correlations) > 0.8].index.tolist()
if suspicious_features:
    print(f"Loại bỏ các đặc trưng nghi ngờ: {suspicious_features}")
    X_train = X_train.drop(columns=suspicious_features)
    X_val = X_val.drop(columns=suspicious_features)
    X_test = X_test.drop(columns=suspicious_features)

# Xem mẫu dữ liệu để kiểm tra label leakage
print("\nMẫu dữ liệu (10 mẫu đầu):\n", X.head(10))
print("\nNhãn tương ứng:\n", y.head(10))

# Tính trọng số lớp
class_weights = len(y) / (2 * y.value_counts())
weight_dict = {0: class_weights[0], 1: class_weights[1]}

# Tinh chỉnh mô hình CatBoost
model = CatBoostClassifier(
    random_state=42,
    scale_pos_weight=weight_dict[1]/weight_dict[0],  # Xử lý mất cân bằng
    reg_lambda=6.0,  # L2 regularization
    max_depth=2,    # Độ sâu tối đa
    iterations=20,  # Tương ứng với n_estimators
    learning_rate=0.1,  # Tốc độ học
    subsample=0.6,  # Tỷ lệ mẫu
    colsample_bylevel=0.6,  # Tỷ lệ đặc trưng (tương tự colsample_bytree)
    min_data_in_leaf=15,  # Tương ứng với min_child_weight/min_child_samples
    verbose=0  # Tắt log chi tiết
)
param_grid = {
    'iterations': [20],
    'max_depth': [2],
    'learning_rate': [0.01, 0.05],
    'min_data_in_leaf': [15, 20]  # Tương ứng với min_child_samples
}
grid_search = GridSearchCV(model, param_grid, cv=10, scoring='f1', n_jobs=-1)
grid_search.fit(X_train, y_train)

# Lấy mô hình tốt nhất
best_model = grid_search.best_estimator_
print("Tham số tốt nhất:", grid_search.best_params_)
print("Điểm F1 trung bình trên 10-fold CV:", grid_search.best_score_)

# Tìm ngưỡng tối ưu
y_val_pred_proba = best_model.predict_proba(X_val)[:, 1]
fpr, tpr, thresholds = roc_curve(y_val, y_val_pred_proba)
optimal_idx = np.argmax(tpr - fpr)
optimal_threshold = thresholds[optimal_idx]
print(f"Ngưỡng tối ưu: {optimal_threshold}")

# Kiểm tra tầm quan trọng đặc trưng
feature_importance = pd.DataFrame({
    'feature': X_train.columns,
    'importance': best_model.feature_importances_
}).sort_values('importance', ascending=False)
print("\nTầm quan trọng đặc trưng:\n", feature_importance.head(10))

# Đánh giá trên tập train
y_pred_train = best_model.predict(X_train)
print("\nBáo cáo phân loại trên tập train:")
print(classification_report(y_train, y_pred_train))

# Đánh giá trên tập validation
y_pred_val = best_model.predict(X_val)
print("\nBáo cáo phân loại trên tập validation:")
print(classification_report(y_val, y_pred_val))

# Đánh giá trên tập test
y_pred_test = best_model.predict(X_test)
print("\nBáo cáo phân loại trên tập test:")
print(classification_report(y_test, y_pred_test))

# Lưu mô hình
joblib.dump(best_model, "D:/CSUD/backend_CatBoost/phishing_CatBoost.pkl")
print("Mô hình CatBoost đã được lưu vào 'phishing_CatBoost.pkl'")