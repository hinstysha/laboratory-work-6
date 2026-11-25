"""Средняя сложность, задание 3: HTML-страница с отдельным CSS."""

from flask import Flask, render_template


def create_app() -> Flask:
    """Создаёт приложение для показа страницы с CSS-оформлением."""
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        """Возвращает HTML-страницу с подключённым файлом стилей."""
        return render_template("styled_page.html")

    return app


def main() -> None:
    """Запускает локальный сервер третьего задания на порту 5002."""
    create_app().run(host="127.0.0.1", port=5002, debug=False)


if __name__ == "__main__":
    main()
