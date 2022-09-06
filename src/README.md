# HKEX CCASS Shareholding Dashboard

A dashboard application written in Python using Dash, with a Selenium backend to scrape the required data from the HKEX's official [CCASS shareholding search page](https://www3.hkexnews.hk/sdw/search/searchsdw.aspx).

## Requirements
- Docker >= 20.10.17
- Docker Compose >= 1.29.2

## How to run it
Run the following command in the project directory (`shareholding-app`)

`docker compose up`

## Issues
- The AWS `t2-micro` instance type lacks the performance to efficiently run the Selenium data scraper. This may cause freezing or slowness when requesting data that hasn't already been stored in the database.

## Remarks
Development was done on a machine with an Apple M1 processor, so the development environment specified in `docker-compose-env.yml` using an experimental `seleniarm/standalone-chromium` Docker image for the standalone Selenium Grid instance.
