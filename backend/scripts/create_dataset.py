import pandas as pd
import os
import dotenv

# Завантаження .env
dotenv.load_dotenv()

# Отримання шляху до директорії з датасетом
DATASET_DIR = os.getenv("DATASET_DIR")  # ОНОВЛЕНО назву змінної
if not DATASET_DIR:
    raise EnvironmentError("Змінна середовища 'DATASET_DIR' не знайдена або порожня.")

# Шлях до CSV файлу
csv_file = os.path.join(DATASET_DIR, "drugs_for_common_treatments.csv")

# Шлях до output файлу
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_file = os.path.join(project_root, "illness_description.txt")


def create_dataset():
    if not os.path.exists(output_file):
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV файл не знайдено за шляхом: {csv_file}")

        drugs_df = pd.read_csv(csv_file)

        drugs_df['alcohol'] = drugs_df['alcohol'].apply(lambda x: 1 if pd.notna(x) else 0)
        drugs_df['no_of_reviews'] = drugs_df['no_of_reviews'].fillna(0)
        drugs_df['rating'] = drugs_df['rating'].fillna(0)

        tagged_descr = pd.DataFrame({
            'combined_info': drugs_df.apply(
                lambda row: f"{row['medical_condition']} Info: {row['medical_condition_description']}",
                axis=1
            )
        })

        unique_descriptions = tagged_descr['combined_info'].drop_duplicates()

        unique_descriptions.to_csv(output_file, index=False, sep='\n', header=False)

        print(f"✅ Датасет успішно створено та збережено у: {output_file}")
    else:
        print(f"ℹ️ Датасет вже існує за шляхом: {output_file}, створення пропущено.")


def get_drugs_df():
    if not os.path.exists(output_file):
        create_dataset()

    drugs_df = pd.read_csv(output_file, header=None, names=['combined_info'])
    return drugs_df


# Ініціалізація
drugs_df = get_drugs_df()
