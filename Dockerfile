FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# --- FIX ADDED HERE ---
# Temporary fallback variables to pass Render's asset collection phase safely
ENV SECRET_KEY=render-build-placeholder-value
ENV DB_NAME=placeholder
ENV DB_USER=placeholder
ENV DB_PASSWORD=placeholder
ENV DB_HOST=localhost
ENV DB_PORT=5432
ENV CLOUDINARY_CLOUD_NAME=placeholder
ENV CLOUDINARY_API_KEY=placeholder
ENV CLOUDINARY_API_SECRET=placeholder
ENV ADMIN_WHATSAPP=placeholder
ENV ADMIN_PHONE=placeholder
# ----------------------

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
