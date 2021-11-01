<div style="padding: 2% 5%;">

<h1 style="text-align: center;">
<div style="color:grey; font-size: 0.6em;">Jakub Ostrzołek</div>
<div>WSI ćwiczenie 2 - algorytm genetyczny</div>
</h1>

## Opis ćwiczenia
Celem ćwiczenia było zaimplementowanie algorytmu genetycznego Hollanda oraz użycie go w problemie poszukiwania minimum dla funkcji czterech zmiennych.

Funkcja implementująca algorytm przyjmuje następujące główne argumenty:
* `fitness_fnc` - funkcja oceny (musi przyjmować jako argument jednego osobnika - wektor wartości boolowskich)
* `population` - populacja początkowych osobników
* `iterations` - liczba iteracji, po której algorytm ma zakończyć działanie
* `mutation_prob` - szansa, że dany gen w osobniku ulegnie mutacji
* `crossover_prob` - szansa, że para osobników ulegnie krzyżowaniu

Funkcja zwraca krotkę `(ocena, osobnik)`, która reprezentuje najlepsze rozwiązanie, lub, po ustawieniu argumentu `return_generations=True`, listę obiektów klasy `Generation`, reprezentujących stan populacji w kolejnych iteracjach przebiegu algorytmu.

## Wykorzystane zewnętrzne biblioteki
* `numpy`
* `matplotlib`
* `pytest`
* `pytest-benchmark`

## Użycie
Aby użyć algorytmu dla wybranych parametrów algorytmu należy uruchomić skrypt `main.py` i postępować zgodnie z instrukcjami (`main.py --help`).

## Ocena parametrów algorytmu
**Aby szybko dokonać oceny i wygenerować wykresy użyte w tej dokumentacji należy uruchomić skrypt bashowy `plots.sh`**  

Do oceny parametrów algorytmu użyta została bilbioteka `pytest` oraz `pytest-benchmark`.  
Ocenę należy uruchomić komendą `pytest --benchmark-json=<ścieżka_do_pliku_z_oceną>.json`. Można zmieniać oceniane zbiory parametrów zmieniając wartości stałych `SIZES`, `ITERATIONS`, `MUTATION_PROBS`, `CROSSOVER_PROBS`. Aby ograniczyć liczbę wykonywanych testów, zamiast oceniania każdej kombinacji parametrów algorytmu, są testowane kolejno parametry o wartościach pochodzących z wyżej wymienionych stałych, a reszta parametrów pochodzi ze stałej `STD_PARAMS`. Dodatkowo jest jeszcze stała `SEPARATE_PARAMS`, służąca do dodania osobnych zestawów parametrów. 
Można również regulować ilość powtórzeń stałą `REPEAT`.
 
## Analiza
Aby poddać wyniki analizie, należy wykonać skrypt `analyze.py` i postępować zgodnie z instrukcjami (`analyze.py --help`). Za pomocą skryptu można wygenerować:
* wykresy zależności oceny rozwiązań populacji od numeru iteracji algorytmu (`plot_type=scatter`); większe punkty na wykresie oznaczają więcej osobników o dokładnie tej samej ocenie (ten typ wykresu staje się mało czytelny dla dużej liczby iteracji, powtórzeń i rozmiaru populacji),
* wykresy zależności średniej oceny rozwiązań populacji wraz z odchyleniem standardowym reprezentowanym poprzez słupek błędu od numeru iteracji algorytmu (`plot_type=mean-std`) (ten typ wykresu staje się mało czytelny dla dużej liczby iteracji),
* wykresy porównujące wydajność algorytmu w zależności od zmieniającego się jednego parametru algorytmu przy stałej reszcie (`plot_type=compare`).

Oto przykładowe wyniki:

* Ocena kolejnych populacji:  

![wykres](plots/scatter/s=20,i=100,m=0.05,c=0.1.png)
* Średnia ocena i odchylenie standardowe kolejnych populacji:  

![wykres](plots/mean-std/s=20,i=100,m=0.05,c=0.1.png)
* Porównanie wydajności algorytmu dla różnych warości rozmiaru populacji:  

![wykres](plots/compare/i=500,m=0.05,c=0.1.png)
* Porównanie wydajności algorytmu dla różnych warości iteracji algorytmu:  

![wykres](plots/compare/s=20,m=0.05,c=0.1.png)
* Porównanie wydajności algorytmu dla różnych warości szansy na mutację:  

![wykres](plots/compare/s=20,i=500,c=0.1.png)
* Porównanie wydajności algorytmu dla różnych warości szansy na krzyżowanie:  

![wykres](plots/compare/s=20,i=500,m=0.05.png)

## Wnioski
Z wykresów porównujących można wywnioskować, że:
* zwiększanie zarówno liczby iteracji jak i rozmiaru populacji wpływa pozytywnie na rozwiązanie. Im większe są warości tych parametrów, tym mniej ich wzrost wpływa na zbliżenie do rozwiązania. 
* zarówno za duża jak i za mała szansa na mutację wpływa negatywnie na rozwiązanie. Najlepsza wartość wydaje się być w pobliżu $`0.03`$.
* szansa na krzyżowanie nie wpływa znacząco na wynik algorytmu. Najlepsza wartość tego parametru mieści się w okolicach $`0.5`$.

Stąd można wnioskować, że najlepsze parametry dla algorytmu mieszczą się w okolicach:
* `size=40`
* `iterations=500`
* `mutation_prob=0.03`
* `crossover_prob=0.5`

Wykresy typu `scatter` i `mean-std` dla tak dobranych parametrów:

![wykres](plots/scatter/s=40,i=500,m=0.03,c=0.5.png)
![wykres](plots/mean-std/s=40,i=500,m=0.03,c=0.5.png)

Dla porównania zbiór parametrów wybranych przeze mnie "na wyczucie" (użyty jako `STD_PARAMS` w `test_benchmark.py`):

![wykres](plots/scatter/s=20,i=500,m=0.05,c=0.1.png)
![wykres](plots/mean-std/s=20,i=500,m=0.05,c=0.1.png)

Jak widać, w przypadku parametrów dobranych eksperymentalnie, osobniki mają trochę mniejsze odchylenie standardowe, dzięki czemu są w stanie dokładniej znaleźć minimum (średnie rozwiązanie jest trochę mniejsze od średniego rozwiązania parametrów dobranych "na wyczucie"), jednak nie są to duże różnice. Z drugiej strony oznacza to, że nie są w stanie tak efektywnie eksplorować przestrzeni, więc w innym zastosowaniu mogłoby się okazać, że ten zestaw parametrów jest gorszy.

</div>