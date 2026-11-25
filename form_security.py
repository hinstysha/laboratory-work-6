"""Минимальная защита HTML-форм от межсайтовой отправки POST-запросов."""

from secrets import compare_digest, token_hex

from flask import Flask, abort, request, session


def protect_forms(app: Flask) -> None:
    """Добавляет токен формы в шаблоны и проверяет его в POST-запросах."""

    def csrf_token() -> str:
        """Создаёт и возвращает случайный токен текущей сессии."""
        if "csrf_token" not in session:
            session["csrf_token"] = token_hex(32)
        return session["csrf_token"]

    @app.context_processor
    def form_context() -> dict:
        """Предоставляет функцию получения токена HTML-шаблонам."""
        return {"csrf_token": csrf_token}

    @app.before_request
    def check_token() -> None:
        """Отклоняет POST-запросы без правильного токена сессии."""
        if request.method != "POST":
            return
        expected = session.get("csrf_token")
        provided = request.form.get("csrf_token", "")
        if (not expected or not provided.isascii()
                or not compare_digest(expected, provided)):
            abort(400, description="Неверный токен формы. Обновите страницу.")
