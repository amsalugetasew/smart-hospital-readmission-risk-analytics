# Use the official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create models directory and train model
RUN mkdir -p models
RUN python train_model.py

# Expose ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000
EXPOSE 8501

# Create a startup script to run both services
RUN echo '#!/bin/bash\n\
# Start backend in background\n\
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &\n\
\n\
# Wait for backend to start\n\
sleep 5\n\
\n\
# Start frontend\n\
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0\n\
' > start.sh
RUN chmod +x start.sh

# Run the startup script
CMD ["./start.sh"]
