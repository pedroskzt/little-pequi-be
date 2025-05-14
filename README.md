# 🍽️ Little Pequi Restaurant - Backend

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg?style=flat&logo=python)](https://www.python.org)
[![Django](https://img.shields.io/badge/Django-5.2.1-green.svg?style=flat&logo=django)](https://www.djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.16.0-red.svg?style=flat&logo=)](https://www.django-rest-framework.org/)
[![Simple JWT](https://img.shields.io/badge/Simple%20JWT-5.5.0-green)](https://github.com/jazzband/djangorestframework-simplejwt)

[![Frontend](https://img.shields.io/badge/Littl%20Pequi%20Frontend-0.0.1-F9D259)](https://github.com/pedroskzt/portfolio-FE)

## Project Overview
 
The Little Pequi restaurant project is a comprehensive restaurant management solution developed to showcase my full-stack web application development skills.
The project is structured using a modern microservices architecture, with clear separation between the frontend and backend services.

The backend simulates the functionality of a restaurant management solution, including APIs to handle menu items, orders, and other customer interactions.
This service is a modern, Python and Django-based REST API backend, built with Django REST Framework to provide robust, and secure API endpoints.


## ✨ Features

- **🔐 JWT Authentication** - Secure access with JSON Web Tokens
- **👤 User Management** - Complete user registration and authentication system
- **📝 API Documentation** - Interactive documentation with Swagger
- **🔄 RESTful API** - Well-structured endpoints following REST principles
- **🍕 Menu Management** - Full CRUD operations for menu items

## 🛠️ Tech Stack

<table>
  <tr>
    <td align="center"><b>Core</b></td>
    <td align="center"><b>API</b></td>
    <td align="center"><b>Authentication</b></td>
    <td align="center"><b>Documentation</b></td>
  </tr>
  <tr>
    <td>
      • Python 3.12<br/>
      • Django 5.2.1<br/>
      • SQLite (default)
    </td>
    <td>
      • Django REST Framework<br/>
    </td>
    <td>
      • JWT<br/>
      • Djoser<br/>
    </td>
    <td>
      • drf-spectacular<br/>
      • Swagger UI<br/>
    </td>
  </tr>
</table>



## 📁️ Application Structure

```
.
├── api/                        # Main API application
│   ├── menu/                   # Menu API components
│   │   ├── menu_models.py      # Menu data models
│   │   ├── menu_serializers.py # Serializers for menu items
│   │   └── menu_views.py       # ViewSets for menu endpoints
│   └── urls.py                 # API route definitions
├── backend/                    # Project configuration
│   ├── settings.py             # Django settings
│   └── urls.py                 # Main URL routing
├── manage.py                   # Django command-line utility
└── requirements.txt            # Project dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12
- pip

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/pedroskzt/portfolio-BE.git
   cd portfolio-BE
   ```

2. **Set up a virtual environment**

   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the root directory:
   
   ```
   SECRET_KEY=your_secret_key_here
   DEBUG=True
   ```

5. **Run migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

7. **Launch the development server**

   ```bash
   python manage.py runserver
   ```

8. **Access the API**

   The API will be available at: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)

## 📚 API Endpoints

### Menu Items

| Endpoint             | Method | Description           | Permissions         |
|----------------------|--------|-----------------------|---------------------|
| `/api/v1/menu/`      | GET    | List all menu items   | Public              |
| `/api/v1/menu/{id}/` | GET    | Get menu item details | Public              |
| `/api/v1/menu/`      | POST   | Create new menu item  | Authenticated users |
| `/api/v1/menu/{id}/` | PUT    | Update menu item      | Authenticated users |
| `/api/v1/menu/{id}/` | DELETE | Delete menu item      | Authenticated users |

### Authentication

| Endpoint             | Method | Description       |
|----------------------|--------|-------------------|
| `/auth/jwt/create/`  | POST   | Obtain JWT token  |
| `/auth/jwt/refresh/` | POST   | Refresh JWT token |
| `/auth/users/`       | POST   | Register new user |

## 📖 API Documentation

Interactive API documentation is available at:

- **Swagger UI**: `/api/schema/swagger/`

## 🔐 Authentication

To authenticate API requests:

1. Get a token by sending a POST request to `/auth/jwt/create/` with:
   ```json
   {
     "username": "your_username",
     "password": "your_password"
   }
   ```

2. Include the token in the Authorization header:
   ```
   Authorization: JWT <your_token>
   ```
## Related Projects

- Frontend Repository: [Little Pequi Restaurant Frontend](https://github.com/pedroskzt/portfolio-FE)

## 🚧 Development Status and Contributions

The project is currently under development, contributions are welcome!

If you have suggestions for improving the project, feel free to fork the repository and create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
