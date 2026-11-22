# Use a minimal base image with Python 3.9 installed
FROM python:3.9-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy all files from the current directory on the host to the container's /app directory
COPY . .

# Install the Python dependencies listed in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Streamlit listens on port 8501
EXPOSE 8501

# Run the Streamlit app on port 8501 and make it accessible from outside the container
# (XSRF protection is disabled so that file uploads work behind the Codespaces port-forwarding proxy)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false"]
