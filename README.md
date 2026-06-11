# 📰 Fake News Detection System

A web-based Fake News Detection System built with **Django**, **DRF**, and **Logistic Regression**. The system allows users to verify news articles, submit news for review, and enables administrators to manage and approve submitted content.

## 🚀 Features

### Guest Users

* Check whether a news article is Fake or Real.
* Instant prediction using a trained Machine Learning model.

### Registered Users

* User registration and login.
* Submit news articles for verification.
* View submitted news history.
* Edit submitted news.
* Delete submitted news.
* Track approval status of submitted articles.

### Admin Panel

* Review all submitted news articles.
* Approve or reject user submissions.
* Automatically update training datasets:

  * `True.csv`
  * `Fake.csv`
* Manage users and contributions.

## 🧠 Machine Learning Model

The prediction system is powered by:

* TF-IDF Vectorization
* Logistic Regression Classifier
* Scikit-learn
* Pandas
* NumPy

### Model Training Workflow

1. Load datasets (`True.csv` and `Fake.csv`)
2. Clean and preprocess text
3. Convert text into numerical vectors using TF-IDF
4. Train Logistic Regression model
5. Save trained model and vectorizer
6. Use saved model for predictions inside Django

## 🛠️ Technologies Used

### Backend

* Django
* Python

### Machine Learning

*JupiterNotebook
* Scikit-learn
* Pandas
* NumPy
* Joblib

### Frontend

* MVC

### Database

* Django ORM


## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/samjhanaG/FakeNewsDetectionSystem.git
cd FakeNewsDetectionSystem
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

**Windows**

```bash
venv\Scripts\activate
```

**Linux/Mac**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Admin Account

```bash
python manage.py createsuperuser
```

### 6. Start Development Server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## 📊 Dataset

The system uses two datasets:

* `True.csv` → Genuine news articles
* `Fake.csv` → Fake news articles

These datasets are used for training and updating the Machine Learning model.

## 🔍 How Prediction Works

1. User enters a news article.
2. Text is cleaned and transformed using the saved TF-IDF vectorizer.
3. Logistic Regression model predicts:

   * ✅ Real News
   * ❌ Fake News

## 📜 License

This project is developed for educational and research purposes.

## 👨‍💻 Author

**Samjhana G**

GitHub: https://github.com/samjhanaG
