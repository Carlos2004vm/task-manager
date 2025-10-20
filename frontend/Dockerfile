# Imagen base de Node 16
FROM node:16-alpine

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar package.json y package-lock.json
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto del código
COPY . .

# Exponer el puerto 4200
EXPOSE 4200

# Comando para iniciar Angular en modo desarrollo
CMD ["npm", "start", "--", "--host", "0.0.0.0", "--poll", "2000"]
