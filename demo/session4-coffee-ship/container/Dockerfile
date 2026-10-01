# coffee-ship container image: stdlib-only Python 3.12 HTTP service for ECS/Fargate.
FROM python:3.12-slim

WORKDIR /app

# No external dependencies (stdlib-only); copy requirements for parity/future use.
COPY requirements.txt ./
COPY app.py ./

# Container port; matches the ECS taskdef portMapping and the ALB target.
ENV PORT=8080
EXPOSE 8080

CMD ["python", "app.py"]
