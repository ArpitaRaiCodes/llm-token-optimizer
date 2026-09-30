FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-download the tiktoken encoding at build time so the container never
# needs outbound internet access at runtime just to count tokens.
RUN python -c "import tiktoken; tiktoken.get_encoding('cl100k_base')"

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
