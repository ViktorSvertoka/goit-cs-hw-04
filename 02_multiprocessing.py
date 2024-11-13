import os
import multiprocessing
from collections import defaultdict
from multiprocessing import Queue
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


def process_task(files, keywords, queue):
    """Завдання для окремого процесу."""
    local_result = defaultdict(list)
    for file in files:
        result = search_keywords_in_file(file, keywords)
        for k, v in result.items():
            local_result[k].extend(v)
    queue.put(local_result)


def multiprocessing_search(files, keywords):
    """Запускає багатопроцесорний пошук по файлах."""
    processes = []
    queue = Queue()
    results = defaultdict(list)

    # Розділяємо файли на частини для процесів
    num_processes = min(4, len(files))  # Максимум 4 процеси
    chunk_size = len(files) // num_processes
    for i in range(num_processes):
        start = i * chunk_size
        end = len(files) if i == num_processes - 1 else (i + 1) * chunk_size
        process = multiprocessing.Process(
            target=process_task, args=(files[start:end], keywords, queue)
        )
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    # Збираємо результати з черги
    while not queue.empty():
        result = queue.get()
        for k, v in result.items():
            results[k].extend(v)

    return results


# Виконання багатопроцесорного пошуку
if __name__ == "__main__":
    keywords = ["error", "warning", "critical"]

    # Отримуємо список файлів та сортуємо їх за номерами
    files = [f for f in os.listdir(".") if f.endswith(".txt")]

    print(
        f"{Fore.GREEN}Знайдені файли: {files}"
    )  # Виведемо знайдені файли для перевірки

    print(" ")

    if not files:
        print(f"{Fore.YELLOW}Немає доступних текстових файлів для пошуку.")
    else:
        start_time = time()
        results_multiprocessing = multiprocessing_search(files, keywords)
        end_time = time()
        print(
            f"{Fore.MAGENTA}Багатопроцесорний пошук завершено за {end_time - start_time:.2f} секунд."
        )

        print(f"{Style.BRIGHT}Результати пошуку:")
        if results_multiprocessing:
            for keyword, found_files in results_multiprocessing.items():
                print(
                    f"{Fore.BLUE}Ключове слово '{keyword}' знайдено у файлах: {Fore.YELLOW}{found_files}"
                )
        else:
            print(f"{Fore.RED}Жодних ключових слів не знайдено.")
