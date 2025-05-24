import os
import pandas as pd
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import shutil # Для видалення директорії Chroma при необхідності (опціонально для тестування)

# --- Конфігурація шляхів та назв файлів ---
# Шлях до директорії з вихідними даними Kaggle
# Зверніть увагу: вам потрібно буде змінити цей шлях на той, де у вас збережено dataset
KAGGLE_DATA_PATH = "/Users/boychukmaksim/.cache/kagglehub/datasets/jithinanievarghese/drugs-related-to-common-treatments/versions/1"
CSV_FILE_NAME = "drugs_for_common_treatments.csv"
PROCESSED_DATA_PATH = os.path.join(KAGGLE_DATA_PATH, CSV_FILE_NAME)

# Шлях для збереження проміжного текстового файлу з описами
ILLNESS_DESCRIPTION_FILE = "illness_description.txt"

# Директорія для збереження Chroma DB
CHROMA_PERSIST_DIRECTORY = "chroma_db"

# Модель для ембеддингів
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# --- Ініціалізація додатку FastAPI ---


# --- Глобальні змінні для зберігання даних та бази даних ---
# Ці змінні будуть заповнені під час ініціалізації
drugs_df: pd.DataFrame = None
db_drugs: Chroma = None
embeddings: HuggingFaceEmbeddings = None

# --- Функція для ініціалізації даних та бази даних ---
def initialize_data_and_db():
    global drugs_df, db_drugs, embeddings

    print("Перевірка та ініціалізація даних та Chroma DB...")

    # 1. Завантаження та обробка даних з CSV
    if drugs_df is None:
        try:
            print(f"Завантаження даних з {PROCESSED_DATA_PATH}")
            temp_drugs_df = pd.read_csv(PROCESSED_DATA_PATH)

            # Обробка даних, як у ноутбуці
            temp_drugs_df['alcohol'] = temp_drugs_df['alcohol'].apply(lambda x: 1 if pd.notna(x) else 0)
            temp_drugs_df['no_of_reviews'] = temp_drugs_df['no_of_reviews'].apply(lambda x: 0 if pd.isna(x) else x )
            temp_drugs_df['rating'] = temp_drugs_df['rating'].apply(lambda x: 0 if pd.isna(x) else x )

            drugs_df = temp_drugs_df
            print("Дані завантажено та оброблено.")

        except FileNotFoundError:
            print(f"Помилка: Файл даних {PROCESSED_DATA_PATH} не знайдено.")
            print("Будь ласка, переконайтеся, що шлях до датасету Kaggle вказано коректно.")
            # В реальному застосунку тут можна викликати sys.exit(1) або іншим чином обробити помилку
            drugs_df = pd.DataFrame() # Створюємо пустий DataFrame, щоб уникнути помилок, але застосунок не буде функціональним
            return # Перериваємо ініціалізацію, якщо дані не завантажено


    # 2. Перевірка та створення проміжного текстового файлу
    if not os.path.exists(ILLNESS_DESCRIPTION_FILE):
        print(f"Файл {ILLNESS_DESCRIPTION_FILE} не знайдено. Створення...")
        if drugs_df is not None and not drugs_df.empty:
            tagged_descr = pd.DataFrame({
                'combined_info': drugs_df.apply(
                    lambda row: f"{row['medical_condition']} Info: {row['medical_condition_description']}", axis=1
                )
            })
            unique_descriptions = tagged_descr['combined_info'].drop_duplicates()
            unique_descriptions.to_csv(ILLNESS_DESCRIPTION_FILE, index=False, sep='|', header=False)
            print(f"Файл {ILLNESS_DESCRIPTION_FILE} створено.")
        else:
             print(f"Не вдалося створити {ILLNESS_DESCRIPTION_FILE}, оскільки дані не завантажено або вони порожні.")


    # 3. Ініціалізація моделі ембеддингів
    if embeddings is None:
         print(f"Ініціалізація моделі ембеддингів: {EMBEDDING_MODEL_NAME}")
         embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
         print("Модель ембеддингів ініціалізовано.")

    # 4. Перевірка та ініціалізація/завантаження Chroma DB
    if db_drugs is None:
        if os.path.exists(CHROMA_PERSIST_DIRECTORY):
            print(f"Директорія {CHROMA_PERSIST_DIRECTORY} знайдена. Завантаження Chroma DB...")
            try:
                # Завантаження існуючої бази даних
                db_drugs = Chroma(persist_directory=CHROMA_PERSIST_DIRECTORY, embedding_function=embeddings)
                print("Chroma DB завантажено.")
            except Exception as e:
                print(f"Помилка при завантаженні Chroma DB: {e}")
                print(f"Спроба перестворити Chroma DB...")
                # Видаляємо пошкоджену директорію і створюємо знову
                shutil.rmtree(CHROMA_PERSIST_DIRECTORY, ignore_errors=True)
                db_drugs = create_and_persist_chroma_db(ILLNESS_DESCRIPTION_FILE, embeddings, CHROMA_PERSIST_DIRECTORY)

        else:
            print(f"Директорія {CHROMA_PERSIST_DIRECTORY} не знайдена. Створення Chroma DB...")
            db_drugs = create_and_persist_chroma_db(ILLNESS_DESCRIPTION_FILE, embeddings, CHROMA_PERSIST_DIRECTORY)

    print("Ініціалізація завершена.")


def create_and_persist_chroma_db(file_path: str, embeddings: HuggingFaceEmbeddings, persist_directory: str) -> Chroma:
    """Створює Chroma DB з текстового файлу та зберігає її."""
    if not os.path.exists(file_path):
        print(f"Помилка: Файл {file_path} для створення Chroma DB не знайдено.")
        return None # Повертаємо None, якщо файл не існує

    try:
        # Завантаження документів
        raw_documents = TextLoader(file_path).load()

        # Розбиття на чанки (в даному випадку, кожен рядок - окремий документ, тому chunk_size=0 ідентично)
        text_splitter = CharacterTextSplitter(chunk_size=0, chunk_overlap=0, separator="\n")
        documents = text_splitter.split_documents(raw_documents)

        # Створення та збереження Chroma DB
        # from_documents автоматично створить директорію, якщо її немає
        db = Chroma.from_documents(
            documents,
            embedding=embeddings,
            persist_directory=persist_directory
        )
        print(f"Chroma DB створено та збережено в {persist_directory}.")
        return db
    except Exception as e:
        print(f"Помилка при створенні Chroma DB з файлу {file_path}: {e}")
        return None # Повертаємо None у випадку помилки