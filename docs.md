# WSI ćwiczenie 1

## Opis ćwiczenia
Celem ćwiczenia było zaimplementowanie algorytmu wyznaczającego minimum lokalne funkcji za pomocą metody gradientu prostego (gradient descend).

Funkcja implementująca algorytm przyjmuje następujące główne argumenty:
* `fnc` - funkcja, której minimum ma znaleźć,
* `grad` - gradient tej funkcji,
* `start_pnt` - punkt początkowy,
* `learn_coef` - początkowy współczynnik uczenia się.

Funkcja zwraca obiekt klasy `Minimum`, który zawiera punkt i wartość minimum oraz pola do analizy wydajności algorytmu.

## Testowanie
Do testowania użyłem bilbioteki `pytest` oraz `pytest-benchmark`.  
Dla każdej funkcji wybieranych jest kilka początkowych punktów oraz wartości współczynnika uczenia się. Następnie algorytm jest wykonywany dla tych parametrów oraz generowany jest plik formatu JSON z wynikami. Widnieją tu m. in. po kroki wykonywane przez algorytm, liczba iteracji potrzebna na wykonanie się danego przykładu czy czas jaki zajęła praca funkcji.  
## Analiza
Aby poddać wyniki analizie należy wykonać skrypt `test_benchmark.py` i postępować zgodnie z instrukcjami. Za pomocą skryptu można wygenerować:
* wykresy funkcji z zaznaczonymi kolejnymi krokami algorytmu,
* wykresy porównujące wydajność algorytmu w zależności od zmieniającego się początkowego współczynnika uczenia się przy stałym punkcie początkowym,
* wykresy porównujące wydajność algorytmu w zależności od zmieniającego się początkowego punktu przy stałym początkowym współczynniku uczenia się.

Oto przykładowe wyniki:
* Kroki dla funkcji f
![wykres](graphs/f/steps/x=(-10,-30),a=0.1.svg)
* Kroki dla funkcji g
![wykres](graphs/g/steps/x=-1.7,a=0.1.svg)
* Wydajność dla funkcji f w zależności od początkowego współczynnika uczenia się
![wykres](graphs/f/performance/x=(-10,-30).svg)
* Wydajność dla funkcji f w zależności od punktu początkowego
![wykres](graphs/f/performance/a=0.8.svg)
* Wydajność dla funkcji g w zależności od początkowego współczynnika uczenia się
![wykres](graphs/g/performance/x=1.8.svg)
* Wydajność dla funkcji g w zależności od punktu początkowego
![wykres](graphs/g/performance/a=1.2.svg)

Z wykresów widać, że większy wpływ na wydajność algorytmu ma dobranie odpowiedniego 


