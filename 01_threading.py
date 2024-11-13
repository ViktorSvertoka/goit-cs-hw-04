import os
import threading
from collections import defaultdict
from time import time
from colorama import Fore, Style, init

# Ініціалізуємо colorama
init(autoreset=True)


def search_keywords_in_file(filename, keywords):
    """Функція для пошуку ключових слів у конкретному файлі."""
    result = defaultdict(list)
    try:
        with open(filename, "r", encoding="utf-8") as file:
            text = file.read()
            # Виводимо весь текст файлу
            print(f"{Fore.CYAN}Читання файлу {filename}:\n{Fore.YELLOW}{text}\n")
            for word in keywords:
                if word.lower() in text.lower():  # Ігноруємо регістр при пошуку
                    result[word].append(filename)
    except Exception as e:
        print(f"{Fore.RED}Помилка при читанні файлу {filename}: {e}")
    return result


def threaded_search(files, keywords):
    """Запускає багатопотоковий пошук по файлах."""
    threads = []
    results = defaultdict(list)
    lock = threading.Lock()

    def search_task(files_subset):
        local_result = defaultdict(list)
        for file in files_subset:
            result = search_keywords_in_file(file, keywords)
            for k, v in result.items():
                local_result[k].extend(v)
        with lock:
            for k, v in local_result.items():
                results[k].extend(v)

    # Розділяємо файли на частини для потоків
    num_threads = min(4, len(files))  # Максимум 4 потоки
    chunk_size = len(files) // num_threads if num_threads > 0 else 1
    for i in range(num_threads):
        start = i * chunk_size
        end = len(files) if i == num_threads - 1 else (i + 1) * chunk_size
        thread = threading.Thread(target=search_task, args=(files[start:end],))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return results


# Виконання багатопотокового пошуку
if __name__ == "__main__":
    keywords = ["error", "warning", "critical"]

    # Отримуємо список файлів та сортуємо їх за номерами
    files = [f for f in os.listdir(".") if f.endswith(".txt")]
    files.sort(
        key=lambda x: int(x.split("_")[1].split(".")[0])
    )  # Сортуємо файли за номерами у назвах

    print(
        f"{Fore.GREEN}Знайдені файли: {files}"
    )  # Виведемо знайдені файли для перевірки

    print(" ")

    if not files:
        print(f"{Fore.YELLOW}Немає доступних текстових файлів для пошуку.")
    else:
        start_time = time()
        results_threading = threaded_search(files, keywords)
        end_time = time()
        print(
            f"{Fore.MAGENTA}Багатопотоковий пошук завершено за {end_time - start_time:.2f} секунд."
        )

        print(f"{Style.BRIGHT}Результати пошуку:")

        # Сортуємо файли перед виведенням
        sorted_results = defaultdict(list)
        for keyword in keywords:
            found_files = sorted(
                results_threading.get(keyword, []),
                key=lambda x: int(x.split("_")[1].split(".")[0]),
            )
            sorted_results[keyword] = found_files

        if sorted_results:
            for (
                keyword
            ) in keywords:  # Виводимо результати в правильному порядку ключових слів
                found_files = sorted_results[keyword]
                print(
                    f"{Fore.BLUE}Ключове слово '{keyword}' знайдено у файлах: {Fore.YELLOW}{found_files}"
                )
        else:
            print(f"{Fore.RED}Жодних ключових слів не знайдено.")
