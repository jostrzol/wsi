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


</div>