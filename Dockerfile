FROM python:3.10.13

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get -y upgrade && \
    pip install -r requirements.txt && \
    pip install streamlit

#ポート
EXPOSE 8501

COPY . /app

ENTRYPOINT ["streamlit", "run"]

CMD ["streamlit_app.py"]