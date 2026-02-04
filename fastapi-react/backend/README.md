


pip install alembic
alembic init alembic

<!-- user is the schema name -->
alembic revision --autogenerate -m "update user schema" 
<!-- specfic filed -->
alembic revision --autogenerate -m "add phone_number to users"


alembic upgrade head
