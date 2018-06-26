# Luftkissentisch


## Buttons

File: Öffnet eine neue .csv Datei, in der die Messergebnisse gespeichert werden können. Es werden Dezimalpunkte und Kommata als Trennzeichen verwendet. Eine neue Datei wird nur erstellt, falls sich in der aktuellen Datei bereits Daten befinden, d.h. wenn mindestens einmal gespeichert wurde.

Start: Startet eine neue Aufzeichnung, falls die Leinwand (schwarzes Quadrat) zu sehen ist. Die Messung läuft für sechs Sekunden. Werden innerhalb dieser sechs Sekunden keine Positionen mehr erfasst, so endet die Messung fünf Sekunden nach der letzten Datenerfassung. Die erfassten Positionen werden direkt auf die Leinwand gezeichnet. Es wird zwischen den beiden erfassten Objekten unterschieden. Das erste Objekt erhält eine blaue, das zweite eine rote Farbe. Mehr als zwei Objekte können nicht erfasst werden.
Ist die Leinwand nicht zu sehen, wird diese angezeigt.

Save: Schreibt die Messwerte des aktuellen Durchlaufs in die oben angegebene Datei. Neue Daten in der selben Datei werden hinten angehängt. Mehrfaches Speichern der selben Daten ist deaktiviert.

x(t), y(t): Stellt die Positionen der eizelnen Objekte nach der Zeit dar.

s(t): Stellt die von den Objekten zurückgelegte Strecke nach der Zeit dar.

v(t): Stellt die Geschwindigkeit der einzelnen Objekte zu den einzelnen Zeitpunkten dar.

Quit: Beendet das Programm und verwirft alle nicht gespeicherten Daten.

## Funktionalitäten
Winkelbestimmung: Nachdem ein Stoß aufgezechnent wurde, können auf der Leinwand Positionen markiert werden, die für die Berechnung des Bahnwinkels (bezüglich der x-Achse) genutzt werden sollen. 

Slotkorrektur: 