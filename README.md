

-----

# Shopify Store Insights-Fetcher Application

## Table of Contents

1.  [Introduction](https://www.google.com/search?q=%231-introduction)
2.  [Features](https://www.google.com/search?q=%232-features)
      * [Mandatory Features](https://www.google.com/search?q=%23mandatory-features)
      * [Bonus Features](https://www.google.com/search?q=%23bonus-features)
3.  [Project Structure](https://www.google.com/search?q=%233-project-structure)
4.  [Setup and Installation](https://www.google.com/search?q=%234-setup-and-installation)
      * [Prerequisites](https://www.google.com/search?q=%23prerequisites)
      * [Deployment with Docker Compose](https://www.google.com/search?q=%23deployment-with-docker-compose)
5.  [Usage](https://www.google.com/search?q=%235-usage)
      * [API Documentation (Swagger UI)](https://www.google.com/search?q=%23api-documentation-swagger-ui)
      * [Fetching Brand Insights](https://www.google.com/search?q=%23fetching-brand-insights)
6.  [Technologies Used](https://www.google.com/search?q=%236-technologies-used)
7.  [Design Principles and Best Practices](https://www.google.com/search?q=%237-design-principles-and-best-practices)
8.  [Future Enhancements](https://www.google.com/search?q=%238-future-enhancements)
9.  [License](https://www.google.com/search?q=%239-license)

-----

## 1\. Introduction

The **Shopify Store Insights-Fetcher Application** is a Python-based backend system designed to extract structured data from Shopify-powered e-commerce websites **without relying on the official Shopify API**. Many businesses utilize Shopify to build their online stores, and this application aims to gather valuable public insights from these webstores.

The core problem it solves is providing a structured data output (JSON) for key brand information, policies, products, and contact details, which can be crucial for market research, competitor analysis, or data aggregation.

## 2\. Features

This application implements all mandatory requirements and a significant portion of the bonus requirements.

### Mandatory Features

  * **Whole Product Catalog:** Fetches a list of products available on the store. (Note: Currently fetches the first page of `/products.json`. Further pagination logic can be added.)
  * **Hero Products:** Identifies and extracts information about products prominently displayed on the store's homepage.
  * **Privacy Policy:** Scrapes and provides the full text and URL of the brand's privacy policy.
  * **Return, Refund Policies:** Extracts the full text and URL of the brand's return and refund policies.
  * **Brand FAQs:** Collects frequently asked questions and their answers. The parsing logic is designed to handle common FAQ structures.
  * **Social Handles:** Identifies and extracts URLs for the brand's social media profiles (e.g., Instagram, Facebook, TikTok, YouTube).
  * **Contact Details:** Extracts available email addresses and phone numbers from the website.
  * **Brand Text Context:** Gathers general "About Us" or brand descriptive text content.
  * **Important Links:** Identifies and provides URLs for key navigational links such as Order Tracking, Contact Us, and Blogs.
  * **RESTful API Endpoint:** Exposes a `/api/fetch-insights` endpoint that accepts a Shopify store URL and returns a `BrandContext` JSON object.
  * **Robust Error Handling:** Provides appropriate HTTP status codes and error messages for various scenarios:
      * `400 Bad Request`: For invalid URL formats or if the URL is unlikely to be a Shopify store.
      * `404 Not Found`: If the website is unreachable or no meaningful data can be retrieved.
      * `500 Internal Server Error`: For data validation issues (Pydantic) or unexpected server-side errors.

### Bonus Features

  * **Persist all data in a SQL DB (MySQL):**

      * All scraped brand data (products, policies, FAQs, etc.) is automatically persisted into a MySQL database.
      * Before scraping, the application checks if insights for the given URL already exist in the database, demonstrating a caching mechanism to avoid redundant scraping.
      * Utilizes SQLAlchemy ORM for efficient and object-oriented database interactions.

  * **Competitor Analysis (Conceptual/Planned for Future Implementation):**

      * While the full "Competitor Analysis" feature (which would involve using external search APIs to *identify* competitors) is not fully implemented in the provided code, the architecture is designed to support it. The existing `fetch_shopify_insights` endpoint can be re-used to scrape data for identified competitor URLs.
      * The README explains the approach using third-party APIs like Google Custom Search or specialized SEO tools as the recommended robust method for competitor identification, rather than direct, fragile web scraping of search results.

## 3\. Project Structure

The project follows a modular and scalable structure to separate concerns, enhance readability, and facilitate maintenance:

```
shopify_insights_app/
├── main.py                 # FastAPI application entry point
├── api/
│   └── routes.py           # Defines API endpoints and orchestrates data flow
├── services/
│   ├── scraper.py          # Handles HTTP requests and fetches raw web content
│   ├── parser.py           # Parses HTML/JSON content using Beautiful Soup and regex
│   └── competitor_finder.py# (Placeholder/Mock) Service for identifying competitors via external APIs
├── models/
│   └── brand_data.py       # Pydantic models for data validation and serialization
├── database/
│   ├── __init__.py         # Python package marker
│   ├── models.py           # SQLAlchemy ORM models (defines database schema)
│   ├── crud.py             # Create, Read, Update, Delete (CRUD) operations for the DB
│   └── dependencies.py     # FastAPI dependency for managing database sessions
├── utils/
│   └── helpers.py          # Utility functions (e.g., URL normalization, basic validation)
├── config.py               # Configuration settings (DB credentials, API keys)
└── requirements.txt        # Python dependencies
```

## 4\. Setup and Installation

This application is designed to be easily deployed using Docker Compose, which will set up both the FastAPI application and the MySQL database with a single command.

### Prerequisites

  * **Docker:** Ensure Docker Desktop (for Windows/macOS) or Docker Engine (for Linux) is installed and running on your system.

### Deployment with Docker Compose

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/Samyakshrma/Shopify-Insights-Fetcher.git
    cd Shopify-Insights-Fetcher # Navigate into the cloned directory
    ```

2.  **Configure Database Connection:**
    Open `config.py` located in `shopify_insights_app/config.py`. The `DATABASE_URL` is set via environment variables in `docker-compose.yml`, but ensure the default value matches the credentials used in `docker-compose.yml` for clarity and local testing (if applicable).

    ```python
    # shopify_insights_app/config.py
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+mysqlconnector://shopify:shopifypassword@db:3306/shopify_insights_db")
    ```

    The `db` hostname here correctly points to the MySQL service name within the Docker Compose network.

3.  **Run the Application Stack:**
    From the root directory of the cloned repository (`Shopify-Insights-Fetcher/`), execute the Docker Compose command:

    ```bash
    docker compose up --build -d
    ```

      * `--build`: This will build the Docker image for your `app` service using the `Dockerfile` in the `shopify_insights_app/` directory.
      * `-d`: Runs the containers in detached mode (in the background).

    Docker Compose will:

      * Set up a dedicated network.
      * Start the MySQL `db` container (including creating the `shopify_insights_db` database and user based on environment variables).
      * Wait for the MySQL container to be healthy using its `healthcheck`.
      * Build your FastAPI `app` container.
      * Start the FastAPI `app` container, which will execute `python3 main.py`. During the `app` container's startup, `main.py` will automatically call `create_db_tables()`, ensuring your database schema is initialized.

    You might see a warning about the `version` attribute being obsolete in `docker-compose.yml`; this is harmless and can be ignored or the line removed.

## 5\. Usage

### API Documentation (Swagger UI)

Once the Docker Compose stack is running, you can access the interactive API documentation and test the endpoints directly from your browser:

  * **Swagger UI:** Open `http://localhost:8000/docs` in your web browser.
  * **ReDoc:** Alternatively, you can view the documentation at `http://localhost:8000/redoc`.

### Fetching Brand Insights

1.  **Navigate to Swagger UI:** Go to `http://localhost:8000/docs`.
2.  **Expand `/api/fetch-insights`:** Click on the endpoint to reveal its details.
3.  **Click "Try it out":** This enables the input fields.
4.  **Enter a Shopify Store URL:** In the `website_url` field, paste a valid Shopify store URL.
      * Examples: `https://memy.co.in/`, `https://hairoriginals.com/`, `https://www.allbirds.com/`, `https://gymshark.com/`
5.  **Click "Execute":** The API will process the request.

**Expected Behavior:**

  * **First Request for a URL:** The application will scrape the website, process the data, and persist it to your MySQL database. You will receive a `200 OK` response with the `BrandContext` JSON object in the "Response Body" section of Swagger UI. To monitor the scraping process and backend logs, use `docker compose logs -f app` in your terminal.
  * **Subsequent Requests for the Same URL:** The application will retrieve the data from the MySQL database (cache) directly, avoiding re-scraping. This will be significantly faster. Your terminal logs (`docker compose logs -f app`) will show: `Insights for [URL] found in DB. Returning cached data.`

**Verifying Data in Database (Optional):**

You can use the MySQL command-line client or a GUI tool (like DBeaver, MySQL Workbench) to inspect the data in your `shopify_insights_db` database.

**To connect via command-line:**

```bash
docker exec -it shopify-insights-fetcher-db-1 mysql -u shopify -p shopify_insights_db
```

(Enter `shopifypassword` when prompted)

**Then, run SQL queries (remember the semicolon `;`):**

```sql
USE shopify_insights_db;

-- List all tables
SHOW TABLES;

-- Check data in the main brands table
SELECT id, website_url, brand_name, last_fetched FROM brands;

-- Check products for a specific brand (replace 1 with the brand's ID from the 'brands' table)
SELECT title, price, currency, product_url FROM products WHERE brand_id = 1;

-- Check policies
SELECT policy_type, title, url FROM policies WHERE brand_privacy_id = 1 OR brand_return_refund_id = 1;

-- Check FAQs
SELECT question, answer FROM faqs WHERE brand_id = 1;

-- Explore other tables similarly: contact_details, social_handles, important_links, hero_products
```

## 6\. Technologies Used

  * **Python 3.9+**: Core programming language.
  * **FastAPI**: High-performance web framework for building APIs.
  * **Uvicorn**: ASGI server used by FastAPI.
  * **Pydantic**: Data validation and settings management, used for defining API request/response models and internal data structures.
  * **Requests**: HTTP library for making web requests (fetching HTML/JSON).
  * **Beautiful Soup 4 (bs4)**: Python library for parsing HTML and XML documents.
  * **`re` (Regular Expressions)**: For pattern matching in text extraction (e.g., emails, phone numbers).
  * **SQLAlchemy**: Python SQL toolkit and Object-Relational Mapper (ORM) for interacting with the database.
  * **MySQL (via `mysql-connector-python`)**: The chosen relational database for data persistence.
  * **Docker**: Used for easy setup and management of the entire application stack.

## 7\. Design Principles and Best Practices

  * **OOP Principles:** The application leverages Object-Oriented Programming with classes like `WebScraper`, `ShopifyParser`, and SQLAlchemy ORM models, encapsulating logic and data.
  * **SOLID Design Patterns:**
      * **Single Responsibility Principle:** Each module and class generally has a single, well-defined responsibility (e.g., `scraper.py` fetches, `parser.py` parses, `crud.py` handles DB operations).
      * **Open/Closed Principle:** Designed to be extensible; new parsing rules or data points can be added without modifying core fetching/API logic.
  * **Clean Code:** Focus on readability, maintainability, and clear naming conventions.
  * **RESTful API Design:** The API endpoint follows REST principles for resource interaction.
  * **Data Validation:** Extensive use of Pydantic models ensures data integrity at the API boundaries and before persistence.
  * **Modular Project Structure:** Organized into logical directories (`api`, `services`, `models`, `database`, `utils`) for better separation of concerns and maintainability.
  * **Error Handling:** Comprehensive `try-except` blocks with specific exception handling and appropriate HTTP status codes for robust operation.
  * **Code Deduplication:** Logic for fetching and parsing is centralized in `services` to avoid repetition.
  * **Edge-Cases Handling:** Basic handling for invalid URLs, network errors, and missing content sections.

## 8\. Future Enhancements

  * **Full Product Catalog Pagination:** Implement logic to automatically traverse all pages of `/products.json` to fetch the complete product catalog.
  * **Advanced Parsing:** Enhance parsing logic for FAQs, policies, and brand context to handle more diverse and complex website structures (e.g., JavaScript-rendered content requiring headless browsers like Selenium/Playwright).
  * **Competitor Analysis (Full Implementation):**
      * Integrate with a reliable third-party search API (e.g., Google Custom Search API, SerpApi, Klazify's competitor API) to programmatically identify competitor URLs.
      * Orchestrate the scraping and persistence of insights for these identified competitors.
  * **Rate Limiting/Retry Logic:** Implement more sophisticated rate-limiting and retry mechanisms for web scraping to avoid being blocked by websites.
  * **Anti-Bot Measures:** Incorporate strategies to bypass advanced anti-bot measures if necessary (e.g., proxy rotation, headless browser automation).
  * **More Insights:** Identify and extract additional common data points from Shopify stores (e.g., shipping information, payment options, customer reviews).
  * **Data Updates:** Implement logic for updating existing brand insights in the database (e.g., a scheduled task to re-scrape periodically).
  * **Authentication/Authorization:** Add API key or token-based authentication for the `/fetch-insights` endpoint.
  * **Logging:** Implement structured logging for better monitoring and debugging in production.

## 9\. License

This project is open-source and available under the [MIT License](https://www.google.com/search?q=LICENSE).