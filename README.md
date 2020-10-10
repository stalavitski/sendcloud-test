# Development Test from SendCloud

### Installation

Use [docker-compose](https://docs.docker.com/compose/) in order to install application:

`docker-compose up`

_Note: Application is developed and tested using docker-compose v1.24.0. 
Compatibility with other versions is not guaranteed._ 


### Usage
By default application is available at http://0.0.0.0:8000/. 
See **Specification** section for details.


### Specification

API Specification is available at `/swagger/`.


### Testing

To run tests use following command:

`docker-compose exec web python manage.py test`


### Automatic feed update

By default feed automatically updated every 10 minutes. It specified in `settings.py` under
`CELERY_BEAT_SCHEDULE.update_feeds.schedule`.


### Build steps

- Install and run `db` service with `postgres` image to serve a PostgreSQL database;
- Install and run `redis` service with `redis:alpine` image to serve a Redis;
- Install and run `web` from `Dockerfile` with `python:3` image;
- Create directory and copy application code.
- Install requirements using pip.
- Run migrations and server.
- Install and run `celery` to serve a Celery worker;
- Install and run `celery-beat` to serve a Celery beat;



