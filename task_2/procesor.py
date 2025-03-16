import os
import re
import time
import multiprocessing


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

def process_worker(files, keywords, queue):
    partial_results = {word: [] for word in keywords}
    for file in files:
        result = search_keywords_in_file(file, keywords)
        for key in keywords:
            partial_results[key].extend(result[key])
    queue.put(partial_results)



def multiprocess_search(files, keywords):
    num_processes = min(2, len(files))
    chunk_size = len(files) // num_processes
    queue = multiprocessing.Queue()
    processes = []

    for i in range(num_processes):
        chunk = files[i * chunk_size: (i + 1) * chunk_size]
        p = multiprocessing.Process(target=process_worker, args=(chunk, keywords, queue))
        p.start()
        processes.append(p)

    results = {word: [] for word in keywords}
    for _ in range(num_processes):
        partial_results = queue.get()
        for key in keywords:
            results[key].extend(partial_results[key])

    for p in processes:
        p.join()

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
        proceesor_results = multiprocess_search(files, keywords)
        print("Threading results:", proceesor_results)
        print("Threading time:", time.time() - start_time)

