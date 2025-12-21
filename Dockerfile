FROM python:3.11-slim
WORKDIR /CRIRA
COPY requirements.txt /CRIRA/
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ /CRIRA/src/
COPY reviews.json /CRIRA/reviews.json
ENV PYTHONPATH=/CRIRA/src
CMD ["python", "-m", "src.main", "--reviews", "reviews.json", "--output", "results.json"]
