import os
import re
import time
import threading
from queue import Queue

def search_keywords_in_file(file_path, keywords):
    
    found_words = {word: [] for word in keywords}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().lower()
            for word in keywords:
                if re.search(rf"{re.escape(word)}", content):
                    found_words[word].append(file_path)
    except Exception as e:
        print(f"Помилка при обробці {file_path}: {e}")
    return found_words


def threaded_search(files, keywords):
    def worker():
        while not file_queue.empty():
            file_path = file_queue.get()
            result = search_keywords_in_file(file_path, keywords)
            with lock:
                for key in keywords:
                    results[key].extend(result[key])
            file_queue.task_done()
    
    file_queue = Queue()
    for file in files:
        file_queue.put(file)
    
    results = {word: [] for word in keywords}
    lock = threading.Lock()
    threads = []
    
    for _ in range(min(2, len(files))):  # Обмежуємо кількість потоків
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    return results


if __name__ == "__main__":
    keywords = input("Введіть ключові слова, розділені комами: ").split(",")
    keywords = [word.strip() for word in keywords if word.strip()]
    directory = "../files"  
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".txt")]

    if not files:
        print("У вказаній папці немає текстових файлів.")
    elif not keywords:
        print("Ви не ввели жодного ключового слова.")
    else:
        start_time = time.time()
        thread_results = threaded_search(files, keywords)
        print("Threading results:", thread_results)
        print("Threading time:", time.time() - start_time)

