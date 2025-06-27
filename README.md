<div align="center">

# 🍽️ Little Pequi Restaurant - Backend

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg?style=flat&logo=python)](https://www.python.org)
[![Django](https://img.shields.io/badge/Django-5.2.1-green.svg?style=flat&logo=django)](https://www.djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.16.0-red.svg?style=flat&logo=)](https://www.django-rest-framework.org/)
[![Simple JWT](https://img.shields.io/badge/Simple%20JWT-5.5.0-green)](https://github.com/jazzband/djangorestframework-simplejwt)

[![Frontend](https://img.shields.io/badge/Littl%20Pequi%20Frontend-0.0.1-F9D259)](https://github.com/pedroskzt/little-pequi-fe)
![Dynamic JSON Badge](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fpedroskzt%2Flittle-pequi-be%2Frefs%2Fheads%2Fmaster%2Fcoverage.json&query=%24.totals.percent_covered_display&label=Coverage&color=green)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit%20Site-brightgreen)](https://littlepequi.live)

</div>

## Project Overview
 
The Little Pequi restaurant project is a comprehensive restaurant management solution developed to showcase my full-stack web application development skills.
The project is structured using a modern microservices architecture, with clear separation between the frontend and backend services.

The backend simulates the functionality of a restaurant management solution, including APIs to handle menu items, orders, and other customer interactions.
This service is a modern, Python and Django-based REST API backend, built with Django REST Framework to provide robust, and secure API endpoints.

## 🌐 Live Demo

**API Backend**: [https://api.littlepequi.live](https://api.littlepequi.live/api/schema/swagger)  
**Frontend Application**: [https://littlepequi.live](https://littlepequi.live)


## ✨ Features

- **🔐 JWT Authentication** - Secure access with JSON Web Tokens
- **👤 User Management** - Complete user registration and authentication system
- **📝 API Documentation** - Interactive documentation with Swagger
- **🔄 RESTful API** - Well-structured endpoints following REST principles
- **🍕 Menu Management** - Full CRUD operations for menu items
- **🐳 Docker Support** - Containerized application for easy deployment
- **🧪 Testing** - Comprehensive test coverage for reliability

## 🛠️ Tech Stack

<table>
  <tr>
    <td align="center"><b>Core</b></td>
    <td align="center"><b>Database</b></td>
    <td align="center"><b>API</b></td>
    <td align="center"><b>Authentication</b></td>
    <td align="center"><b>DevOps</b></td>
    <td align="center"><b>Documentation</b></td>
  </tr>
  <tr>
    <td>
      • Python 3.12<br/>
      • Django 5.2.1<br/>
    </td>
    <td>
      • MySQL 8 (prod)<br/>
      • SQLite (dev)
    </td>
    <td>
      • Django REST Framework<br/>
    </td>
    <td>
      • JWT<br/>
      • Djoser<br/>
    </td>
   <td>
      • Docker<br/>
      • GitHub Actions<br/>
    </td>
    <td>
      • drf-spectacular<br/>
      • Swagger UI<br/>
    </td>
  </tr>
</table>

## 📁️ Project Structure

```
.
├── api/                            # Main API application
│   ├── menu/                       # Menu API components
│   │   ├── menu_models.py          # Menu data models
│   │   ├── menu_serializers.py     # Serializers for menu items
│   │   └── menu_views.py           # ViewSets for menu endpoints
│   └── urls.py                     # API route definitions
├── authentication/                 # User authentication app
│   ├── models.py                   # Custom User model
│   ├── views.py                    # Authentication views (JWT)
│   ├── backends.py                 # User Email Backend method
│   ├── manager.py                  # Create User Email Manager
│   └── urls.py                     # Authentication routes
├── backend/                        # Project configuration
│   ├── settings.py                 # Django settings
│   └── urls.py                     # Main URL routing
├── tests/                          # Test suite
│   ├── unit/                       # Unit tests
│   │   ├── authentication/         # Tests for authentication app
│   │   │   ├── test_models.py      # Authentication Models tests
│   │   │   ├── test_serializers.py # Authentication Serializers tests
│   │   │   └── test_views.py       # Authentication Views tests
│   │   ├── test_models.py          # Api app Models tests
│   │   ├── test_serializers.py     # Api app Serializers test
│   │   └── test_views.py           # Api app Views tests
│   └── helpers.py                  # Test suite helper functions
├── .github/                        # CI/CD workflows
├── Dockerfile                      # Docker configuration
├── entrypoint.sh                   # Docker entrypoint
├── migrate.sh                      # Database migration script
├── manage.py                       # Django command-line utility
└── requirements.txt                # Project dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12
- pip
- Docker (optional, for containerized deployment)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/pedroskzt/little-pequi-be.git
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

   Those are a few examples of the apis. For the complete list, check the [Swagger Schema](schema.yml).

### Category

| Endpoint                     | Method | Description               | Permissions         |
|------------------------------|--------|---------------------------|---------------------|
| `/api/v1/category/`          | GET    | List all categories       | Public              |
| `/api/v1/category/{slug}/`   | GET    | Get a category details    | Public              |
| `/api/v1/category/`          | POST   | Create a new category     | Admin/Staff users   |
| `/api/v1/category/{slug}/`   | PUT    | Update a category         | Admin/Staff users   |
| `/api/v1/category/{slug}/`   | PATCH  | Partial update a category | Admin/Staff users   |
| `/api/v1/category/{slug}/`   | DELETE | Delete a category         | Admin/Staff users   |

### Menu Items

| Endpoint             | Method | Description              | Permissions         |
|----------------------|--------|--------------------------|---------------------|
| `/api/v1/menu/`      | GET    | List all menu items      | Public              |
| `/api/v1/menu/{id}/` | GET    | Get a menu item details  | Public              |
| `/api/v1/menu/`      | POST   | Create new menu item     | Admin/Staff users   |
| `/api/v1/menu/{id}/` | PUT    | Update menu item         | Admin/Staff users   |
| `/api/v1/menu/{id}/` | PATCH  | Partial update menu item | Admin/Staff users   |
| `/api/v1/menu/{id}/` | DELETE | Delete menu item         | Admin/Staff users   |

### Authentication

| Endpoint           | Method | Description                 | Permissions   |
|--------------------|--------|-----------------------------|---------------|
| `/auth/sign-in/`   | POST   | Sign-in to obtain JWT token | Public        |
| `/auth/refresh/`   | POST   | Refresh JWT token           | Public        |
| `/auth/verify/`    | POST   | Verify JWT token            | Public        |
| `/auth/users/`     | POST   | Register new user           | Public        |
| `/auth/users/me/`  | GET    | Get current user info       | Authenticated |

## 📖 API Documentation

Interactive API documentation is available at:

- **Swagger UI**: `/api/schema/swagger/`
- **Swagger Schema file**: [Schema File](schema.yml)

## 🔐 Authentication

To authenticate API requests:

1. Get a token by sending a POST request to `/auth/sign-in/` with:
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

## 🧪 Testing

Run the test suite with:

```bash
python manage.py test
```

For test coverage reports:

```bash
coverage run manage.py test
coverage report
# Optional
coverage html
coverage json
```

## Related Projects

- Frontend Repository: [Little Pequi Restaurant Frontend](https://github.com/pedroskzt/little-pequi-fe)

## 🚧 Development Status and Contributions

The project is currently under development, contributions are welcome!

If you have suggestions for improving the project, feel free to fork the repository and create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.