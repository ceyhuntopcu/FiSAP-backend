# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask runs on
EXPOSE 4000

# Define environment variable
ENV FLASK_APP="src/app.py"

# Run Flask when the container launches
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
