# Luftkissentisch


## Buttons

File: �ffnet eine neue .csv Datei, in der die Messergebnisse gespeichert werden k�nnen. Es werden Dezimalpunkte und Kommata als Trennzeichen verwendet. Eine neue Datei wird nur erstellt, falls sich in der aktuellen Datei bereits Daten befinden, d.h. wenn mindestens einmal gespeichert wurde.

Start: Startet eine neue Aufzeichnung, falls die Leinwand (schwarzes Quadrat) zu sehen ist. Die Messung l�uft f�r sechs Sekunden. Werden innerhalb dieser sechs Sekunden keine Positionen mehr erfasst, so endet die Messung f�nf Sekunden nach der letzten Datenerfassung. Die erfassten Positionen werden direkt auf die Leinwand gezeichnet. Es wird zwischen den beiden erfassten Objekten unterschieden. Das erste Objekt erh�lt eine blaue, das zweite eine rote Farbe. Mehr als zwei Objekte k�nnen nicht erfasst werden.
Ist die Leinwand nicht zu sehen, wird diese angezeigt.

Save: Schreibt die Messwerte des aktuellen Durchlaufs in die oben angegebene Datei. Neue Daten in der selben Datei werden hinten angeh�ngt. Mehrfaches Speichern der selben Daten ist deaktiviert.

x(t), y(t): Stellt die Positionen der eizelnen Objekte nach der Zeit dar.

s(t): Stellt die von den Objekten zur�ckgelegte Strecke nach der Zeit dar.

v(t): Stellt die Geschwindigkeit der einzelnen Objekte zu den einzelnen Zeitpunkten dar.

Quit: Beendet das Programm und verwirft alle nicht gespeicherten Daten.

## Funktionalit�ten
Winkelbestimmung: Nachdem ein Sto� aufgezechnent wurde, k�nnen auf der Leinwand Positionen markiert werden, die f�r die Berechnung des Bahnwinkels (bez�glich der x-Achse) genutzt werden sollen. 

Slotkorrektur: 