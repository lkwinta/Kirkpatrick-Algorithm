# Instalacja

Najpierw sklonuj repozytorium będąc w folderze do którego chcesz je sklonować, na przykład za pomocą:

```
git clone https://github.com/lkwinta/Kirkpatrick-Algorithm.git
```

Pobierz Anacondę, odpal Anaconda Prompt i przejdź do folderu Algorytmy-Geometryczne, tam stwórz środowisko:

```
conda create --name kirkpatrick python=3.9
conda activate kirkpatrick
```

Następnie uruchom:

```
python3 setup.py sdist
python3 -m pip install -e .
```
Otwórz Jupyter Notebook z listy programów w Conda Navigator, pamiętaj, żeby na górze zaznaczyć Twoje środowisko (kirkpatrick). Jeśli nie znajduje modułu kirkpatrick spróbój zrestartować środowisko i jupytera:
```
conda deactivate
conda activate kirkpatrick
```


W celu uniknięcia błędów wziązanych ze ścieżkami do różnych wersji interpreterów pythona sugerujemy korzystanie z Linuxa, a na Windowsie zainstalowanie WSL-a i właśnie w nim uruchamianie wszystkich komend 

# Opis działania algorytmu

# Żródła
https://ics.uci.edu/~goodrich/teach/geom/notes/Kirkpatrick.pdf
