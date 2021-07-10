FROM nginx:1.19.2

COPY nginx.conf /etc/nginx/nginx.conf
RUN rm -rf /etc/nginx/conf.d/default.conf

COPY conf.d/movies.conf /etc/nginx/conf.d/movies.conf
COPY favicon_movie.ico /src/media/images/favicon_movie.ico
WORKDIR /src