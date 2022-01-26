<div style="padding: 2% 5%;">

<h1 style="text-align: center;">
<div style="color:grey; font-size: 0.6em;">Jakub Ostrzołek</div>
<div>WSI ćwiczenie 7 - Modele bayesowskie</div>
</h1>

## Opis ćwiczenia
Celem ćwiczenia była implementacja naiwnego klasyfikatora Bayesa.

Model ma następujące metody (zgodne z biblioteką `sklearn`):
* `fit(X, y)` - trenowanie modelu dla danych wejść X i spodziewanych wyjść y
* `predict(X)` - przewidywanie wyjść y dla danych wejść X za pomocą modelu

Aby klasyfikator dział dobrze, należy przed użyciem zdyskretyzować dane wejściowe

## Wykorzystane zewnętrzne biblioteki
* `numpy`
* `matplotlib`
* `sklearn`
* `pandas`

## Testowanie klasyfikatora
Aby przetestować klasyfikator należy wykonać skrypt `main.py`, uprzednio zmieniając jego parametry zgodnie z zapotrzebowaniem.  
Skrypt wygeneruje nowy model i wytrenuje go używając n-walidacji krzyżowej, a następnie wyświetli porównanie osiągów dla każdego podziału zbiorów. Na koniec zostaną pokazane osiągi najlepszego przebiegu (tego z najwyższą sumą metryk) dla zbioru testowego.

## Wykresy i wnioski

### Parametr `TEST_SIZE`
Parametr ten kontroluje jaka część zbioru wine jest przeznaczona na zbiór testowy.

`TEST_SIZE` | porównanie przebiegów krzyżowania | osiągi najlepszego przebiegu krzyżowania
-|-|-
0,1 | ![wykres](plots/test-size/val-0,10.png) | ![wykres](plots/test-size/test-0,10.png)
0,2 | ![wykres](plots/test-size/val-0,20.png) | ![wykres](plots/test-size/test-0,20.png)
0,3 | ![wykres](plots/test-size/val-0,30.png) | ![wykres](plots/test-size/test-0,30.png)
0,4 | ![wykres](plots/test-size/val-0,40.png) | ![wykres](plots/test-size/test-0,40.png)
0,5 | ![wykres](plots/test-size/val-0,50.png) | ![wykres](plots/test-size/test-0,50.png)

* zbyt duża wartość tego parametru zmniejsza osiągi modelu, ponieważ zawęża się liczność jak i różnorodność zbioru treningowego
* zbyt mała wartość może powodować większe wachania oceny modelu, przez co jest ona niepewna. Zjawisko to może występować w obie strony (zbyt optymistyczna lub zbyt pesymistyczna ocena). 

### Parametr `N_SPLITS`
Parametr ten kontroluje na ile równych części dzielony jest zbiór, który zostaje rozdysponowany na zbiór treningowy i walidacyjny (1 część na walidacyjny, reszta na treningowy).

`N_SPLITS` | porównanie przebiegów krzyżowania | osiągi najlepszego przebiegu krzyżowania
-|-|-
2 | ![wykres](plots/n-splits/val-2.png) | ![wykres](plots/n-splits/test-2.png)
3 | ![wykres](plots/n-splits/val-3.png) | ![wykres](plots/n-splits/test-3.png)
4 | ![wykres](plots/n-splits/val-4.png) | ![wykres](plots/n-splits/test-4.png)
5 | ![wykres](plots/n-splits/val-5.png) | ![wykres](plots/n-splits/test-5.png)
6 | ![wykres](plots/n-splits/val-6.png) | ![wykres](plots/n-splits/test-6.png)

* zbyt duża wartość parametru sprzyja przetrenowaniu
* zbyt mała wartość parametru sprzyja niedotrenowaniu
* może to być efekt zwiększania rozmiaru zbioru treningowego w porównaniu do zbioru walidacyjnego

### Parametr `N_BINS`
Parametr ten kontroluje ilość przedziałów w dyskretyzacji każdej kolumny danych wejściowych do klasyfikatora.

`N_BINS` | porównanie przebiegów krzyżowania | osiągi najlepszego przebiegu krzyżowania
-|-|-
2 | ![wykres](plots/n-bins/val-2.png) | ![wykres](plots/n-bins/test-2.png)
3 | ![wykres](plots/n-bins/val-3.png) | ![wykres](plots/n-bins/test-3.png)
5 | ![wykres](plots/n-bins/val-5.png) | ![wykres](plots/n-bins/test-5.png)
7 | ![wykres](plots/n-bins/val-7.png) | ![wykres](plots/n-bins/test-7.png)
10 | ![wykres](plots/n-bins/val-10.png) | ![wykres](plots/n-bins/test-10.png)

* zbyt duża wartość parametru sprzyja przetrenowaniu
* zbyt mała wartość parametru sprzyja niedotrenowaniu


</div>