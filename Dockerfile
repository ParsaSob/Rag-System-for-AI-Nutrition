# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /workspace

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables for Streamlit
ENV STREAMLIT_SERVER_PORT=8080 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Expose the port
EXPOSE 8080

# Run the application with explicit port
CMD streamlit run --server.port=8080 --server.address=0.0.0.0 app.py 