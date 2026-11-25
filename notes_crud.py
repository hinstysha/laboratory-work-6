"""Повышенная сложность, задание 1: CRUD заметок на Flask и SQLite."""

import sqlite3
from contextlib import closing
from pathlib import Path
from secrets import token_hex
from typing import Optional, Union

from flask import (
    Flask,
    Response,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from form_security import protect_forms


def create_app(database_path: Optional[Union[str, Path]] = None) -> Flask:
    """Создаёт приложение и таблицу заметок в SQLite при необходимости."""
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=token_hex(32), MAX_CONTENT_LENGTH=65536,
        SESSION_COOKIE_NAME="lab6_notes_session",
    )
    database = (
        Path(database_path) if database_path is not None
        else Path(app.instance_path) / "notes.sqlite3"
    )
    database.parent.mkdir(parents=True, exist_ok=True)
    app.config["DATABASE"] = str(database)
    with closing(sqlite3.connect(database)) as connection:
        with connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS notes ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "title TEXT NOT NULL, content TEXT NOT NULL)"
            )
    protect_forms(app)

    def execute_write(query: str, parameters: tuple) -> int:
        """Выполняет параметризованный запрос и закрывает соединение."""
        with closing(sqlite3.connect(app.config["DATABASE"])) as connection:
            with connection:
                cursor = connection.execute(query, parameters)
                return cursor.rowcount

    def read_fields() -> tuple[str, str]:
        """Проверяет название и содержимое заметки из отправленной формы."""
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        if not title or len(title) > 100:
            abort(400, description="Название: от 1 до 100 символов.")
        if len(content) > 5000:
            abort(400, description="Текст: не более 5000 символов.")
        return title, content

    @app.get("/")
    def index() -> str:
        """Показывает список заметок и формы создания и изменения."""
        with closing(sqlite3.connect(app.config["DATABASE"])) as connection:
            connection.row_factory = sqlite3.Row
            notes = connection.execute(
                "SELECT id, title, content FROM notes ORDER BY id DESC"
            ).fetchall()
        return render_template("notes_crud.html", notes=notes)

    @app.post("/notes")
    def add_note() -> Response:
        """Создаёт заметку из проверенных полей формы."""
        title, content = read_fields()
        execute_write(
            "INSERT INTO notes (title, content) VALUES (?, ?)",
            (title, content),
        )
        flash("Заметка добавлена.")
        return redirect(url_for("index"))

    @app.post("/notes/<int:note_id>/update")
    def update_note(note_id: int) -> Response:
        """Изменяет существующую заметку; для отсутствующей возвращает 404."""
        title, content = read_fields()
        changed = execute_write(
            "UPDATE notes SET title = ?, content = ? WHERE id = ?",
            (title, content, note_id),
        )
        if not changed:
            abort(404)
        flash("Заметка изменена.")
        return redirect(url_for("index"))

    @app.post("/notes/<int:note_id>/delete")
    def delete_note(note_id: int) -> Response:
        """Удаляет существующую заметку по идентификатору."""
        changed = execute_write("DELETE FROM notes WHERE id = ?", (note_id,))
        if not changed:
            abort(404)
        flash("Заметка удалена.")
        return redirect(url_for("index"))

    return app


def main() -> None:
    """Запускает локальное CRUD-приложение на порту 5004."""
    create_app().run(host="127.0.0.1", port=5004, debug=False)


if __name__ == "__main__":
    main()
