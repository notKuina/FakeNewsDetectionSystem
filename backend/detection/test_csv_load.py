import os
import pandas as pd

DATA_DIR = "D:\\fakeNewsDetection\\FakeNews\\backend\\detection\\data"

true_path = os.path.join(DATA_DIR, 'True.csv')
fake_path = os.path.join(DATA_DIR, 'Fake.csv')

print("True.csv exists:", os.path.exists(true_path))
print("Fake.csv exists:", os.path.exists(fake_path))

try:
    df_true = pd.read_csv(true_path, names=['title', 'text'], quotechar='"', on_bad_lines='skip', encoding='utf-8-sig')
    df_fake = pd.read_csv(fake_path, names=['title', 'text'], quotechar='"', on_bad_lines='skip', encoding='utf-8-sig')
    print("True.csv sample rows:")
    print(df_true.head())
    print("Fake.csv sample rows:")
    print(df_fake.head())
except Exception as e:
    print("Error reading files:", e)
