# === STAGE 1: BUILDER (Compiles dependencies) ===
FROM mambaorg/micromamba as builder

WORKDIR /app

COPY requirements.txt .

RUN micromamba install -y python=3.11 pip && \
    micromamba run pip wheel --no-cache-dir --wheel-dir=/app/wheels -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# Copy compiled wheels from the builder stage
COPY --from=builder /app/wheels /app/wheels
# Install packages from the local wheels directory
RUN pip install --no-cache-dir --no-index --find-links=/app/wheels /app/wheels/* && \
    rm -rf /app/wheels

# Copy application code
COPY api.py .

# Copy and install the requirements file for simple packages not included in the wheelhouse
# (This step is often omitted if all packages are in wheels, but is kept for safety)
# COPY rag-gateway/requirements.txt .

EXPOSE 8001
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]