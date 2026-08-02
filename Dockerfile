ARG PYTHON_VERSION=3.11-slim
ARG PIP_INDEX_URL=https://pypi.org/simple
ARG PIP_TIMEOUT=300

FROM python:${PYTHON_VERSION} as builder

WORKDIR /install
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout ${PIP_TIMEOUT} -i "${PIP_INDEX_URL}" -r requirements.txt


FROM python:${PYTHON_VERSION}

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/

# Streamlit config: bind to 0.0.0.0 for container access
RUN mkdir -p ~/.streamlit && \
    echo "[server]\nheadless = true\nport = 8888\naddress = \"0.0.0.0\"\n\n[runner]\nfastReruns = true\n\n[theme]\nprimaryColor = \"#1f77b4\"" > ~/.streamlit/config.toml

EXPOSE 8888

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; r = urllib.request.urlopen('http://localhost:8888/_stcore/health'); assert r.status == 200" || exit 1

ENTRYPOINT ["streamlit", "run", "app/app.py", "--server.port=8888", "--server.address=0.0.0.0"]