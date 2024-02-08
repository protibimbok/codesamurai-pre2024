FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
        build-essential \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*


# Copy the current directory contents into the container at /app
COPY ./django_app /app

# Set the working directory in the container
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Command to run your FastAPI application
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
