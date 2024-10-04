# Dockerfile para MySQL
FROM mysql:8.0

# Copia tu script SQL al contenedor
COPY init.sql /docker-entrypoint-initdb.d/

# Configuración de las variables de entorno
ENV MYSQL_ROOT_PASSWORD=piero
ENV MYSQL_DATABASE=DAEAlab08
ENV MYSQL_USER=user1
ENV MYSQL_PASSWORD=piero
