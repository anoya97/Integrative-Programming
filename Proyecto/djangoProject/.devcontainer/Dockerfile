FROM python:latest

ENV PYTHONUNBUFFERED 1

RUN mkdir /workspace
WORKDIR /workspace

RUN pip install --upgrade pip

# Install Python dependencies from requirements.txt if it exists
COPY /requirements/requirements.txt requirements.txt* /workspace/
RUN if [ -f "requirements.txt" ]; then pip install --no-cache-dir -r requirements.txt && rm requirements.txt; fi
COPY /requirements/development.txt development.txt* /workspace/
RUN if [ -f "development.txt" ]; then pip install --no-cache-dir -r development.txt && rm development.txt; fi

# Clean up
RUN apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*