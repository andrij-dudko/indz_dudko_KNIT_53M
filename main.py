import networkx as nx # Підключаємо бібліотеку NetworkX для роботи з графами
import pandas as pd # Підключаємо бібліотеку Pandas для таблиць і CSV
import matplotlib.pyplot as plt # Підключаємо Matplotlib для побудови графіків
from pathlib import Path # Імпортуємо Path для зручної роботи зі шляхами
import sys # Імпортуємо sys для налаштування системного виводу
sys.stdout.reconfigure(encoding="utf-8") # Встановлюємо кодування UTF-8 для коректного друку кирилиці в консолі

DATA_PATH = Path("data/facebook_combined.txt") 

RESULTS_DIR = Path("results")

RESULTS_DIR.mkdir(exist_ok=True) # Створюємо папку results, якщо вона ще не існує

G = nx.read_edgelist( # Зчитуємо граф зі списку ребер у текстовому файлі
    DATA_PATH, # Передаємо шлях до файлу з даними
    nodetype=int, # Перетворюємо ідентифікатори вершин на цілі числа
    create_using=nx.Graph() # Створюємо звичайний неорієнтований граф
)


# АНАЛІЗ ГРАФА 
nodes_count = G.number_of_nodes() # Рахуємо загальну кількість вершин у графі

edges_count = G.number_of_edges() # Рахуємо загальну кількість ребер у графі

degree_values = dict(G.degree()) # Отримуємо кількість сусідів кожної вершини

total_degree = sum(degree_values.values()) # Підсумовуємо ступені всіх вершин графа

avg_degree = total_degree / nodes_count # Обчислюємо середню кількість зв'язків на одну вершину

density = nx.density(G) # Обчислюємо щільність графа 

components_count = nx.number_connected_components(G) # Визначаємо кількість зв'язних компонент у графі



print("АНАЛІЗ СОЦІАЛЬНОГО ГРАФА") 
print("---------------------------------") 
print("Кількість вершин:", nodes_count)
print("Кількість ребер:", edges_count) 
print("Середній ступінь:", round(avg_degree, 4)) 
print("Щільність графа:", round(density, 6)) 
print("Кількість компонентів:", components_count) 


# -------------------- СТВОРЕННЯ ТАБЛИЦІ --------------------

summary = pd.DataFrame({ # Створюємо DataFrame з основними характеристиками графа
    "Показник": [ # Назва першого стовпця таблиці
        "Кількість вершин", # Назва першого показника
        "Кількість ребер", # Назва другого показника
        "Середній ступінь", # Назва третього показника
        "Щільність графа", # Назва четвертого показника
        "Кількість компонентів" # Назва п'ятого показника
    ],
    "Значення": [ # Назва другого стовпця таблиці
        nodes_count, # Значення кількості вершин
        edges_count, # Значення кількості ребер
        avg_degree, # Значення середнього ступеня
        density, # Значення щільності графа
        components_count # Значення кількості компонент
    ]
})


summary.to_csv( # Зберігаємо підсумкову таблицю у CSV-файл
    RESULTS_DIR / "graph_summary.csv", # Шлях до вихідного файлу в папці results
    index=False, # Не записуємо номери рядків (індекси) у файл
    encoding="utf-8-sig" # Зберігаємо в UTF-8 з BOM для коректного відкриття в Excel
)


print("\nРОЗРАХУНОК ЦЕНТРАЛЬНОСТЕЙ") 
print("---------------------------------") 

degree = nx.degree_centrality(G) # Рахуємо центральність за ступенем для кожної вершини

closeness = nx.closeness_centrality(G) # Рахуємо центральність за близькістю (середня відстань до інших вершин)

betweenness = nx.betweenness_centrality( # Наближено рахуємо центральність за посередництвом (важливість як «містка»)
    G, # Передаємо граф G
    k=min(1000, G.number_of_nodes()), # Обираємо вибірку до 1000 вершин для пришвидшення обчислень
    normalized=True, # Нормалізуємо значення у діапазон від 0 до 1
    seed=42 # Фіксуємо зерно генератора випадкових чисел для відтворюваності
)

eigenvector = nx.eigenvector_centrality( # Рахуємо центральність за ввпливовістю сусідів
    G, # Передаємо граф G
    max_iter=1000, # Задаємо максимум ітерацій алгоритму
    tol=1e-6 # Задаємо поріг точності зупинки ітерацій
)

print("Усі 4 центральності розраховано.") 

centrality_df = pd.DataFrame({ # Формуємо таблицю з усіма метриками центральності для кожного користувача
    "User_ID": list(G.nodes()), # Стовпець з ID користувачів
    "Degree": [degree[node] for node in G.nodes()], # Стовпець значень Degree centrality
    "Closeness": [closeness[node] for node in G.nodes()], # Стовпець значень Closeness centrality
    "Betweenness": [betweenness[node] for node in G.nodes()], # Стовпець значень Betweenness centrality
    "Eigenvector": [eigenvector[node] for node in G.nodes()] # Стовпець значень Eigenvector centrality
})

centrality_df = centrality_df.sort_values( # Сортуємо таблицю за спаданням показника Degree
    by="Degree", # Стовпець, за яким виконується сортування
    ascending=False # Порядок за спаданням (від найбільшого значення до найменшого)
)

centrality_df.to_csv( # Зберігаємо повну таблицю центральностей у CSV-файл
    RESULTS_DIR / "all_centralities.csv", # Шлях до файлу всередині папки results
    index=False, # Не зберігаємо індекси рядків
    encoding="utf-8-sig" # Кодування UTF-8 з BOM для Excel
)

print("\nПерші 10 рядків таблиці:") 
print(centrality_df.head(10).to_string(index=False))



print("\nTOP-10 ЗА КОЖНИМ МЕТОДОМ") 
print("---------------------------------") 

top_degree = centrality_df.nlargest(10, "Degree") # Відбираємо 10 користувачів з найбільшим Degree
print("\nTOP-10 за Degree:") 
print(top_degree[["User_ID", "Degree"]].to_string(index=False)) 

top_closeness = centrality_df.nlargest(10, "Closeness") # Відбираємо 10 користувачів з найбільшим Closeness
print("\nTOP-10 за Closeness:")
print(top_closeness[["User_ID", "Closeness"]].to_string(index=False)) 

top_betweenness = centrality_df.nlargest(10, "Betweenness") # Відбираємо 10 користувачів з найбільшим Betweenness
print("\nTOP-10 за Betweenness:") 
print(top_betweenness[["User_ID", "Betweenness"]].to_string(index=False)) 

top_eigenvector = centrality_df.nlargest(10, "Eigenvector") # Відбираємо 10 користувачів з найбільшим Eigenvector
print("\nTOP-10 за Eigenvector:") 
print(top_eigenvector[["User_ID", "Eigenvector"]].to_string(index=False))




print("\nПОРІВНЯННЯ РЕЗУЛЬТАТІВ") 
print("---------------------------------") 

for user in top_degree["User_ID"]: # Перебираємо кожного користувача з топ-10 за Degree
    count = 0 # Лічильник, у скількох топ-10 списках зустрічається користувач

    if user in top_degree["User_ID"].values: # Перевіряємо наявність користувача в топ-10 за Degree
        count += 1 # Збільшуємо лічильник на 1
    if user in top_closeness["User_ID"].values: # Перевіряємо наявність користувача в топ-10 за Closeness
        count += 1 # Збільшуємо лічильник на 1
    if user in top_betweenness["User_ID"].values: # Перевіряємо наявність користувача в топ-10 за Betweenness
        count += 1 # Збільшуємо лічильник на 1
    if user in top_eigenvector["User_ID"].values: # Перевіряємо наявність користувача в топ-10 за Eigenvector
        count += 1 # Збільшуємо лічильник на 1

    print(f"Користувач {user}: {count} з 4 методів") 


print("\nПОБУДОВА ГРАФІКІВ")
print("---------------------------------") 

fig, ax = plt.subplots(2, 2, figsize=(12, 8)) # Створюємо сітку графіків 2x2 розміром 12x8 дюймів

ax[0, 0].bar(top_degree["User_ID"].astype(str), top_degree["Degree"]) # Будуємо стовпчикову діаграму для топ-10 за Degree
ax[0, 0].set_title("Кількість зв'язків") # Задаємо назву першого графіка
ax[0, 0].set_xlabel("ID користувача") # Підписуємо вісь X першого графіка
ax[0, 0].set_ylabel("Центральність") # Підписуємо вісь Y першого графіка

ax[0, 1].bar(top_closeness["User_ID"].astype(str), top_closeness["Closeness"]) # Будуємо стовпчикову діаграму для топ-10 за Closeness
ax[0, 1].set_title("Близькість") # Задаємо назву другого графіка
ax[0, 1].set_xlabel("ID користувача") # Підписуємо вісь X другого графіка
ax[0, 1].set_ylabel("Центральність") # Підписуємо вісь Y другого графіка

ax[1, 0].bar(top_betweenness["User_ID"].astype(str), top_betweenness["Betweenness"]) # Будуємо стовпчикову діаграму для топ-10 за Betweenness
ax[1, 0].set_title("Посередництво") # Задаємо назву третього графіка
ax[1, 0].set_xlabel("ID користувача") # Підписуємо вісь X третього графіка
ax[1, 0].set_ylabel("Центральність") # Підписуємо вісь Y третього графіка

ax[1, 1].bar(top_eigenvector["User_ID"].astype(str), top_eigenvector["Eigenvector"]) # Будуємо стовпчикову діаграму для топ-10 за Eigenvector
ax[1, 1].set_title("Власний вектор") # Задаємо назву четвертого графіка
ax[1, 1].set_xlabel("ID користувача") # Підписуємо вісь X четвертого графіка
ax[1, 1].set_ylabel("Центральність") # Підписуємо вісь Y четвертого графіка

plt.tight_layout() # Автоматично підбираємо відступи між графіками, щоб підписи не накладалися
plt.show()