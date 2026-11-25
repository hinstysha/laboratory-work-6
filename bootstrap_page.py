"""Средняя сложность, задание 5: страница с Bootstrap."""

from flask import Flask, render_template


def create_app() -> Flask:
    """Создаёт приложение со страницей на локальных стилях Bootstrap."""
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        """Возвращает страницу с сеткой, карточками и кнопкой Bootstrap."""
        return render_template("bootstrap_page.html")

    return app


def main() -> None:
    """Запускает локальный сервер пятого задания на порту 5003."""
    create_app().run(host="127.0.0.1", port=5003, debug=False)


if __name__ == "__main__":
    main()
