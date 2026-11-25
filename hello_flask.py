"""Средняя сложность, задание 1: Flask-приложение Hello World."""

from flask import Flask


def create_app() -> Flask:
    """Создаёт приложение с единственным маршрутом приветствия."""
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        """Возвращает приветствие в браузер."""
        return "Hello World!"

    return app


def main() -> None:
    """Запускает локальный сервер первого задания на порту 5001."""
    create_app().run(host="127.0.0.1", port=5001, debug=False)


if __name__ == "__main__":
    main()
