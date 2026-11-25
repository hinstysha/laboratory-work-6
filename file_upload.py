"""Повышенная сложность, задание 4: загрузка файлов через HTML-форму."""

from pathlib import Path
from secrets import token_hex
from typing import Optional, Union
from uuid import uuid4

from flask import (
    Flask,
    Response,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from form_security import protect_forms


ALLOWED_EXTENSIONS = {"txt", "csv", "png", "jpg", "jpeg", "pdf"}


def create_app(upload_directory: Optional[Union[str, Path]] = None) -> Flask:
    """Создаёт приложение с лимитом запроса 2 МиБ и отдельной папкой файлов."""
    app = Flask(__name__)
    folder = (
        Path(upload_directory) if upload_directory is not None
        else Path(app.instance_path) / "uploads"
    )
    folder.mkdir(parents=True, exist_ok=True)
    app.config.update(
        SECRET_KEY=token_hex(32),
        SESSION_COOKIE_NAME="lab6_upload_session",
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
        UPLOAD_FOLDER=str(folder),
    )
    protect_forms(app)

    @app.get("/")
    def index() -> str:
        """Показывает форму загрузки с разрешёнными расширениями."""
        return render_template(
            "file_upload.html", extensions=sorted(ALLOWED_EXTENSIONS)
        )

    @app.post("/upload")
    def upload_file() -> Response:
        """Проверяет файл и сохраняет его под безопасным уникальным именем."""
        uploaded = request.files.get("file")
        if uploaded is None or not uploaded.filename:
            flash("Выберите файл.")
            return redirect(url_for("index"))
        original_name = uploaded.filename
        extension = original_name.rsplit(".", 1)[-1].lower()
        if "." not in original_name or extension not in ALLOWED_EXTENSIONS:
            flash("Это расширение файла не разрешено.")
            return redirect(url_for("index"))
        if not uploaded.stream.read(1):
            flash("Пустой файл загружать нельзя.")
            return redirect(url_for("index"))
        uploaded.stream.seek(0)
        safe_name = secure_filename(original_name)
        if not safe_name or "." not in safe_name:
            safe_name = f"file.{extension}"
        stored_name = f"{uuid4().hex}_{safe_name}"
        target = Path(app.config["UPLOAD_FOLDER"]) / stored_name
        try:
            uploaded.save(target)
        except OSError:
            target.unlink(missing_ok=True)
            flash("Не удалось сохранить файл. Проверьте доступ к папке.")
            return redirect(url_for("index"))
        flash(f"Файл сохранён: {stored_name}")
        return redirect(url_for("index"))

    @app.errorhandler(RequestEntityTooLarge)
    def file_too_large(error: RequestEntityTooLarge) -> tuple[str, int]:
        """Возвращает понятную страницу для слишком большого запроса."""
        return render_template(
            "file_upload.html",
            extensions=sorted(ALLOWED_EXTENSIONS),
            error="Запрос превышает 2 МиБ. Выберите файл меньшего размера.",
        ), 413

    return app


def main() -> None:
    """Запускает локальную загрузку файлов на порту 5005."""
    create_app().run(host="127.0.0.1", port=5005, debug=False)


if __name__ == "__main__":
    main()
