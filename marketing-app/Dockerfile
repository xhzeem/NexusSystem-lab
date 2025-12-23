FROM php:7.4-apache

# Install dependencies if needed
RUN apt-get update && apt-get install -y iputils-ping && rm -rf /var/lib/apt/lists/*

COPY . /var/www/html/

# Ensure permissions
RUN chown -R www-data:www-data /var/www/html

EXPOSE 80
