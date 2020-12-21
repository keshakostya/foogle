# Поисковой движок над локальными файлами

Программа — поисковой движок

## Установка

Для работы программы вам нужен интерпретатор языка Python версии не ниже 3.7

Рекомендую все делать в виртуальном окружении

```bash
$ git clone https://github.com/keshakostya/foogle.git
$ pip install foogle
```

## Принцип работы
Программа может строить индекс над локальными файлами и искать их по названию или содержимому

## Помощь

Чтобы открыть помощь

```bash
$ python3 -m foogle -h
```

## Запустить тесты

```bash
$ python3 -m pytest
```

## Пример использования

```bash
$ python -m foogle cli
Welcome to search engine shell.
Type help or ? to list commands.
Type ? "command", to see help for command
>  build_index root
Built index in "root"
```

## Автор

Козлов Константин, матмех
