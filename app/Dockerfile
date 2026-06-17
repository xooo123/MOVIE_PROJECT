FROM nginx:alpine

# Custom nginx config (static files + /api/ reverse proxy to the backend)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Only the static frontend belongs in the web root
COPY static/ /usr/share/nginx/html/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
