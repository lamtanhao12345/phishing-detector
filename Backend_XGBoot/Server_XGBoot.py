from flask import Flask, request, jsonify
import joblib
import pandas as pd
import re
from urllib.parse import urlparse
import logging
import warnings
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome extension

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tắt cảnh báo
warnings.filterwarnings("ignore")

# Load mô hình
try:
    model = joblib.load("D:/CSUD/Backend_FN/phishing_xgboost_FN.pkl")
    expected_features = model.feature_names_in_.tolist()
    logger.info(f"Đã tải mô hình với {len(expected_features)} đặc trưng: {expected_features}")
except Exception as e:
    logger.error(f"Lỗi khi tải mô hình: {e}")
    exit()

# Ngưỡng tối ưu (cập nhật từ roc_curve trong train_phishing_model.py)
OPTIMAL_THRESHOLD = 0.5  # Cần cập nhật từ mã huấn luyện

# Hàm chuẩn hóa URL
def normalize_url(url):
    """Thêm scheme nếu thiếu và kiểm tra tính hợp lệ."""
    if not url:
        return None
    url = url.strip().lower()
    if not re.match(r'^https?://', url):
        url = 'http://' + url
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return None
        return parsed.geturl()
    except:
        return None

# Hàm trích xuất đặc trưng từ URL
def extract_features(url):
    try:
        normalized_url = normalize_url(url)
        if not normalized_url:
            raise ValueError("URL không hợp lệ")
        
        parsed_url = urlparse(normalized_url)
        domain = parsed_url.netloc
        path = parsed_url.path
        query = parsed_url.query

        # Trích xuất đặc trưng
        features = {
            'URLLength': len(normalized_url),
            'DomainLength': len(domain),
            'IsDomainIP': 1 if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain) else 0,
            'NoOfSubDomain': max(len([d for d in domain.split('.') if d]) - 2, 0),
            'HasObfuscation': 1 if re.search(r'%\d{2}|javascript:|eval\(', normalized_url, re.IGNORECASE) else 0,
            'NoOfObfuscatedChar': len(re.findall(r'%\d{2}', normalized_url)),
            'ObfuscationRatio': len(re.findall(r'%\d{2}', normalized_url)) / max(len(normalized_url), 1),
            'NoOfLettersInURL': sum(c.isalpha() for c in normalized_url),
            'LetterRatioInURL': sum(c.isalpha() for c in normalized_url) / max(len(normalized_url), 1),
            'NoOfDegitsInURL': sum(c.isdigit() for c in normalized_url),
            'DegitRatioInURL': sum(c.isdigit() for c in normalized_url) / max(len(normalized_url), 1),
            'NoOfEqualsInURL': normalized_url.count('='),
            'NoOfQMarkInURL': normalized_url.count('?'),
            'NoOfAmpersandInURL': normalized_url.count('&'),
            'NoOfOtherSpecialCharsInURL': len(re.findall(r'[!@#$%^&*(),.<>{}|;:]', normalized_url)),
            'SpacialCharRatioInURL': len(re.findall(r'[!@#$%^&*(),.<>{}|;:]', normalized_url)) / max(len(normalized_url), 1),
            'IsHTTPS': 1 if parsed_url.scheme == 'https' else 0,
            'HasTitle': 1,  # Giả sử có title
            'HasFavicon': 1 if re.search(r'favicon|icon', normalized_url, re.IGNORECASE) else 0,
            'Robots': 1 if 'robots.txt' in normalized_url.lower() else 0,
            'IsResponsive': 0,  # Không thể xác định từ URL
            'HasDescription': 0,
            'HasExternalFormSubmit': 1 if re.search(r'form|login|signin', normalized_url, re.IGNORECASE) else 0,
            'HasSocialNet': 1 if re.search(r'facebook|twitter|linkedin|instagram|social', normalized_url, re.IGNORECASE) else 0,
            'HasSubmitButton': 1 if re.search(r'submit|login|signin', normalized_url, re.IGNORECASE) else 0,
            'HasHiddenFields': 1 if 'hidden' in normalized_url.lower() else 0,
            'HasPasswordField': 1 if re.search(r'password|pass', normalized_url, re.IGNORECASE) else 0,
            'Bank': 1 if re.search(r'bank|paypal|hsbc|barclays|wellsfargo|chase|citi', normalized_url, re.IGNORECASE) else 0,
            'Pay': 1 if re.search(r'pay|payment|checkout|billing|invoice|card|credit', normalized_url, re.IGNORECASE) else 0,
            'Crypto': 1 if re.search(r'crypto|bitcoin|blockchain|ethereum|wallet|coin', normalized_url, re.IGNORECASE) else 0,
            'HasCopyrightInfo': 1 if re.search(r'copyright|©', normalized_url, re.IGNORECASE) else 0,
            'NoOfURLRedirect': 1 if re.search(r'redirect|forward', normalized_url, re.IGNORECASE) else 0,
            'NoOfSelfRedirect': 0,
            'NoOfPopup': 1 if 'popup' in normalized_url.lower() else 0,
            'NoOfiFrame': 1 if 'iframe' in normalized_url.lower() else 0,
            # Mô phỏng đặc trưng website dựa trên phân phối huấn luyện
            'NoOfImage': 10 if 'image' in normalized_url.lower() else 5,  # Giả sử giá trị trung bình
            'NoOfCSS': 3 if 'css' in normalized_url.lower() else 1,
            'NoOfJS': 5 if re.search(r'js|javascript', normalized_url, re.IGNORECASE) else 2,
            'NoOfSelfRef': 2,
            'NoOfEmptyRef': 1,
            'NoOfExternalRef': 5
        }

        feature_df = pd.DataFrame([features])
        logger.info(f"Đã trích xuất {len(feature_df.columns)} đặc trưng cho {url}: {feature_df.iloc[0].to_dict()}")

        # Kiểm tra đặc trưng thiếu
        missing_features = [f for f in expected_features if f not in feature_df.columns]
        if missing_features:
            logger.warning(f"Thiếu {len(missing_features)} đặc trưng: {missing_features}. Gán giá trị 0.")
            for f in missing_features:
                feature_df[f] = 0
        
        # Reindex để khớp với expected_features
        feature_df = feature_df.reindex(columns=expected_features, fill_value=0)
        logger.debug(f"Đặc trưng sau reindex: {feature_df.iloc[0].to_dict()}")
        return feature_df
    except Exception as e:
        logger.error(f"Lỗi khi trích xuất đặc trưng từ {url}: {e}")
        return None

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data:
        logger.error("Yêu cầu không chứa dữ liệu JSON")
        return jsonify({'error': 'Yêu cầu không chứa dữ liệu JSON'}), 400

    url = data.get('url')
    features = data.get('features')

    if not url and not features:
        logger.error("Yêu cầu thiếu URL hoặc đặc trưng")
        return jsonify({'error': 'Yêu cầu thiếu URL hoặc đặc trưng'}), 400

    # Xử lý khi có URL
    if url:
        logger.info(f"Trích xuất đặc trưng từ URL: {url}")
        feature_df = extract_features(url)
        if feature_df is None:
            return jsonify({'error': 'Không thể trích xuất đặc trưng từ URL'}), 400
    else:
        try:
            feature_df = pd.DataFrame([features])
            if not all(col in feature_df.columns for col in expected_features):
                missing_cols = [col for col in expected_features if col not in feature_df.columns]
                logger.error(f"Đặc trưng đầu vào thiếu: {missing_cols}")
                return jsonify({'error': f'Đặc trưng đầu vào thiếu: {missing_cols}'}), 400
            feature_df = feature_df[expected_features]
            logger.info(f"Đặc trưng đầu vào trực tiếp: {feature_df.iloc[0].to_dict()}")
        except Exception as e:
            logger.error(f"Lỗi khi xử lý đặc trưng đầu vào: {e}")
            return jsonify({'error': f'Lỗi khi xử lý đặc trưng: {str(e)}'}), 400

    # Dự đoán
    try:
        probability = model.predict_proba(feature_df)[0][1]
        prediction = 1 if probability >= OPTIMAL_THRESHOLD else 0
        result = "Phishing" if prediction == 1 else "Safe"
        logger.info(f"Dự đoán cho {url or 'đặc trưng trực tiếp'}: is_phishing={prediction}, result={result}, probability={probability:.4f}")
        return jsonify({
            'is_phishing': bool(prediction),
            'result': result,
            'probability': float(probability),
            'url': url,
            'source': 'XGBoost',
            'features': feature_df.to_dict(orient='records')[0]
        })
    except Exception as e:
        logger.error(f"Lỗi khi dự đoán: {e}")
        return jsonify({'error': f'Lỗi khi dự đoán: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)