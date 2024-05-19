FROM python:3.12
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT LOCAL
RUN mkdir /loan_repayment
WORKDIR /loan_repayment
COPY requirements.txt /loan_repayment/
RUN pip install -r requirements.txt
COPY . /loan_repayment/
