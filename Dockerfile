FROM python:3.10

WORKDIR /epfa
 
COPY  . .
RUN pip install --no-cache-dir --upgrade -r requirements.txt


EXPOSE 80

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]