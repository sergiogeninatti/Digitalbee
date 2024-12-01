# Telegram Bot Project

Este proyecto es un bot de Telegram desarrollado en Python, diseñado para ser fácil de usar, extender y mantener.  

## Ejecución del Proyecto

### Requisitos
Antes de comenzar, asegúrate de tener instalados los siguientes requisitos:  
- [Docker](https://docs.docker.com/get-docker/)  
- [Docker Compose](https://docs.docker.com/compose/install/)  

### Pasos para ejecutar el proyecto
1. Clona este repositorio:  
   ```bash
   git clone https://github.com/tu-usuario/telegram-bot-project.git
   cd telegram-bot-project
   ```

2. Configura tu archivo `.env`:  
   Crea un archivo llamado `.env` en el directorio raíz del proyecto y agrega tu token de bot de Telegram:  
   ```
   TELEGRAM_BOT_TOKEN=<tu-token-aqui>
   ```

3. Construye la imagen de Docker:  
   ```bash
   make build
   ```

4. Inicia el bot:  
   ```bash
   make up
   ```

5. Abre Telegram y envía el comando `/start` a tu bot para verificar que esté funcionando.  

---

## Ejecución del Entorno de Desarrollo

### Requisitos
Además de Docker y Docker Compose, instala las siguientes herramientas:  
- [Python 3.10 o superior](https://www.python.org/downloads/)  
- [Poetry](https://python-poetry.org/docs/#installation)  

### Pasos para configurar el entorno de desarrollo
1. Instala las dependencias de Python con Poetry:  
   ```bash
   poetry install
   ```

2. Verifica que todo esté funcionando correctamente ejecutando las pruebas:  
   ```bash
   make test
   ```

3. Usa el siguiente comando para verificar el estilo del código:  
   ```bash
   make style
   ```

4. Si necesitas acceder a una shell dentro del contenedor Docker para depuración:  
   ```bash
   make shell
   ```

---

## Dependencias del Proyecto

Este proyecto utiliza las siguientes dependencias y herramientas:

### **1. Docker y Docker Compose**  
- **Propósito:** Contenerizar la aplicación y ejecutarla de manera consistente en cualquier entorno.  
- **Instalación en Windows:**  
  1. Descarga e instala [Docker Desktop](https://www.docker.com/products/docker-desktop/).  
  2. Habilita la integración con WSL 2 (si usas Windows 10/11).  

### **2. Python**  
- **Versión:** 3.10 o superior  
- **Propósito:** Lenguaje de programación principal del proyecto.  
- **Instalación en Windows:**  
  1. Descarga el instalador desde [python.org](https://www.python.org/downloads/).  
  2. Durante la instalación, marca la opción "Add Python to PATH".  

### **3. Poetry**  
- **Propósito:** Gestionar dependencias y entornos virtuales.  
- **Instalación en Windows:**  
  1. Abre una terminal de Windows (PowerShell).  
  2. Ejecuta:  
     ```bash
     (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
     ```  
  3. Agrega Poetry al PATH si no lo está automáticamente.  

### **4. Pytest**  
- **Propósito:** Framework para ejecutar pruebas automáticas.  
- **Instalación:** Se incluye como dependencia de desarrollo en Poetry.  

### **5. Python Telegram Bot**  
- **Propósito:** Librería para interactuar con la API de Telegram.  
- **Instalación:** Se incluye como dependencia principal en Poetry.  

### **6. Ruff**  
- **Propósito:** Linter para verificar el estilo y la calidad del código.  
- **Instalación:** Se incluye como dependencia principal en Poetry.  

### **7. Herramientas de Documentación**  
- **Propósito:** Crear documentación en formato compatible con Read the Docs.  
- **Instalación:** Usa el archivo `docs/index.rst` como base para la documentación.  

---

## Comandos del Makefile

El proyecto incluye un `Makefile` con los siguientes comandos:  

- **`make build`**  
  Construye la imagen Docker para el proyecto.  

- **`make up`**  
  Ejecuta el bot en un contenedor Docker.  

- **`make shell`**  
  Abre una shell dentro del contenedor Docker del proyecto.  

- **`make test`**  
  Ejecuta la suite de pruebas con Pytest.  

- **`make style`**  
  Ejecuta el linter Ruff para verificar el estilo del código.  

---

## Contribuciones  

¡Contribuciones son bienvenidas! Por favor, abre un issue o envía un pull request con tus sugerencias.  

## Licencia  

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.  
