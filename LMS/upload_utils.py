from pathlib import Path
from django.core.exceptions import ValidationError
from django.utils.text import slugify


def sanitize_filename(filename, default_stem='upload'):
    suffix = Path(filename or '').suffix.lower()
    stem = Path(filename or '').stem
    safe_stem = slugify(stem) or default_stem
    return f'{safe_stem}{suffix}'


def validate_uploaded_file(upload, *, allowed_extensions, allowed_mime_types, max_size_bytes):
    if not upload:
        raise ValidationError('No file was uploaded.')

    extension = Path(upload.name).suffix.lower()
    if extension not in {ext.lower() for ext in allowed_extensions}:
        raise ValidationError(f'Unsupported file type: {extension or "unknown"}.')

    content_type = (getattr(upload, 'content_type', '') or '').lower()
    if allowed_mime_types and content_type and content_type not in {mime.lower() for mime in allowed_mime_types}:
        raise ValidationError('Unsupported file content type.')

    if max_size_bytes and upload.size > max_size_bytes:
        raise ValidationError(
            f'File is too large. Maximum allowed size is {max_size_bytes // (1024 * 1024)} MB.'
        )
