FROM nginx:alpine
RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf
ARG SITE_DIR=/site
COPY ${SITE_DIR}/ /usr/share/nginx/html/
# mount optional secrets -> /etc/secrets/htpasswd
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:8080/ || exit 1
CMD ["nginx", "-g", "daemon off;"]