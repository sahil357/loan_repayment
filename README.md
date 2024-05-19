# Loan Repayment

Mini-Aspire API:
This app allows authenticated users to apply for a loan. The application needs to include at least the fields "amount required" and "loan term." All loans are assumed to have a "weekly" repayment frequency. After the loan is approved, users must be able to submit weekly loan repayments. The repayment functionality will be simplified and won't need to check if the dates are correct but will just set the weekly amount to be repaid.

## Basic Features as Requested

- Authenticated customers can submit a loan application.
- Authenticated admins can approve a loan application.
- Authenticated admins can view a list of loans assigned to them.
- Authenticated customers can view a list of loans they have applied for.
- Authenticated customers can view a list of all loan repayments to be handled by them.
- Authenticated customers can repay a particular installment.

## Extra Features Added

- Create admin.
- Create customer.
- Customer/admin login.
- Customer/admin logout.
- Maintaining extra credit amount: If a customer pays an amount greater than the required repayment amount, we store the difference in a credit amount, which could be added to the next repayment amount if needed.

## Prerequisites

Make sure you have the following installed:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/) (if using Docker Compose)

## Installation

Git clone the project:
```bash
git clone git@github.com:sahil357/loan_repayment.git
cd loan_repayment
git checkout master
```
Build the project
```bash
docker-compose up --build
```

Apply Database Migrations
```bash
docker-compose exec -it loan_repayment_web python manage.py makemigrations
docker-compose exec -it loan_repayment_web python manage.py migrate
```

Build the project
```bash
docker-compose up --build
```

Apply Database Migrations
```bash
docker-compose exec -it loan_repayment_web python manage.py makemigrations
docker-compose exec -it loan_repayment_web python manage.py migrate
```


    
## Assumptions
Based on the information provided by the document, I have made some assumptions in the project for now. Please note that these assumptions could easily be modified based on new requirements
- There is only one admin (the last admin created using api becomes the primary admin)
- Extra credit amount can will be stores in the database
## Postman collection
- postman collection link: https://api.postman.com/collections/16733694-8e3352c8-a17e-4d7b-90b8-50b622838181?access_key=PMAT-01HY9BCN7XVQG0JFMMQWM826J5

- Screenshots from postman: https://docs.google.com/document/d/1iTFVEkZb2RAEGAA48iyXoTc6scNJtzg8uQ0n1FU2X9I/edit?usp=sharing
## Running Tests

Generate code coverage report
```bash
docker exec -it loan_repayment_web pytest --cov=loan --cov-report=html
```

