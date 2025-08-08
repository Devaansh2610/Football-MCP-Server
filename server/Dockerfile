
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /footy-mcp-server

# Copy the current directory contents into the container
COPY requirements.txt /footy-mcp-server/

# Install any necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . /footy-mcp-server

# Expose the port that your app will run on
EXPOSE 8080

# Run the server when the container launches
CMD ["python", "footy.py"]