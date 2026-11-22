# Use a lightweight Python 3.13 base image: the same Python version as the Google Colab runtime
# where the model was trained, so the pinned libraries are installed the same way in both places
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the current directory (app.py, requirements.txt, superkart_model.joblib) into the container
COPY . .

# Install the dependencies without caching the downloaded packages, to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# The API listens on port 7860
EXPOSE 7860

# Start the application with Gunicorn:
# -w 4              -> 4 worker processes handle requests in parallel
# -b 0.0.0.0:7860   -> bind the server to port 7860 on all network interfaces
# app:superkart_api -> the Flask instance named superkart_api in app.py
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]
