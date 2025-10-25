# Restaurant Review Collection System

A comprehensive Python system for cataloging restaurant reviews from Google Places and Yelp APIs with advanced data management, deduplication, and storage capabilities.

## 🏗️ Project Structure

```
restaurant_reviews/
├── main.py                 # Main execution script
├── config.py              # Configuration and credentials
├── requirements.txt       # Dependencies
├── data/
│   └── reviews.csv       # Output CSV file
├── src/
│   ├── __init__.py
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base_scraper.py      # Abstract base class
│   │   ├── google_scraper.py    # Google Places API handler
│   │   └── yelp_scraper.py      # Yelp Fusion API handler
│   ├── models/
│   │   ├── __init__.py
│   │   └── review.py            # Review data model
│   ├── storage/
│   │   ├── __init__.py
│   │   └── csv_handler.py       # CSV storage operations
│   └── utils/
│       ├── __init__.py
│       ├── logger.py            # Logging configuration
│       └── validators.py        # Data validation
```

## 🚀 Features

### Core Functionality
- **Multi-source Review Collection**: Fetch reviews from Google Places and Yelp APIs
- **Intelligent Deduplication**: Prevent duplicate reviews based on review ID and source
- **Incremental Updates**: Only add new reviews, preserving existing data
- **Data Normalization**: Standardize date formats, rating scales, and text content
- **Backup System**: Automatic backups before updates with cleanup of old backups

### Data Management
- **Comprehensive Review Model**: Capture all relevant review metadata
- **CSV Storage**: Efficient storage with pandas for data manipulation
- **Data Validation**: Robust validation of review data and API responses
- **Statistics Generation**: Detailed reporting on collected reviews

### Error Handling & Reliability
- **API Rate Limiting**: Configurable delays and exponential backoff
- **Network Timeout Handling**: Graceful handling of network issues
- **Invalid Response Validation**: Comprehensive API response validation
- **Graceful Degradation**: Continue operation if one API fails
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## 📋 Data Fields Captured

### Core Review Information
- `source`: Platform (Google/Yelp)
- `review_id`: Unique identifier from source
- `author_name`: Reviewer name
- `rating`: Normalized 5-star rating
- `review_text`: Full review content
- `review_date`: Date when review was posted

### Additional Metadata
- `helpful_votes`: Number of helpful votes (Yelp)
- `response_from_owner`: Owner response text
- `verified_purchase`: Verification status
- `profile_photo_url`: Reviewer profile photo
- `language`: Review language
- `photos_attached`: Number of attached photos
- `owner_response_date`: Date of owner response

### System Fields
- `fetched_timestamp`: When review was collected
- `sentiment_score`: Computed sentiment analysis (optional)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd restaurant_reviews
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API credentials**:
   ```bash
   export GOOGLE_API_KEY="your_google_api_key"
   export YELP_API_KEY="your_yelp_api_key"
   ```

## ⚙️ Configuration

### Environment Variables
- `GOOGLE_API_KEY`: Google Places API key
- `YELP_API_KEY`: Yelp Fusion API key
- `CSV_FILE_PATH`: Path to CSV file (default: `data/reviews.csv`)
- `BACKUP_PATH`: Backup directory (default: `data/backups/`)
- `API_RETRY_ATTEMPTS`: Number of retry attempts (default: 3)
- `API_TIMEOUT`: Request timeout in seconds (default: 30)
- `RATE_LIMIT_DELAY`: Delay between requests in seconds (default: 1.0)
- `LOG_LEVEL`: Logging level (default: INFO)

### Restaurant Configuration
Configure your restaurant details in the config:

```python
from config import AgentConfig, RestaurantConfig

# Create restaurant configuration
restaurant = RestaurantConfig(
    name="Your Restaurant Name",
    google_place_id="ChIJ...",  # Google Place ID
    yelp_business_id="restaurant-name-city",  # Yelp Business ID
    address="123 Main St, City, State",
    phone="+1-555-123-4567",
    website="https://yourrestaurant.com"
)

# Create main configuration
config = AgentConfig(
    google_api_key="your_google_api_key",
    yelp_api_key="your_yelp_api_key",
    restaurant=restaurant,
    csv_file_path="data/reviews.csv",
    backup_path="data/backups/"
)
```

## 🚀 Usage

### Basic Usage
```bash
python main.py
```

### Programmatic Usage
```python
import asyncio
from config import AgentConfig, RestaurantConfig
from main import RestaurantReviewCollector

async def main():
    # Configure restaurant
    restaurant = RestaurantConfig(
        name="Example Restaurant",
        google_place_id="ChIJ...",
        yelp_business_id="example-restaurant-city"
    )
    
    # Create configuration
    config = AgentConfig(
        google_api_key="your_key",
        yelp_api_key="your_key",
        restaurant=restaurant
    )
    
    # Create collector
    collector = RestaurantReviewCollector(config)
    
    # Run collection cycle
    results = await collector.run_collection_cycle()
    
    if results['success']:
        print(f"Collected {sum(results['reviews_fetched'].values())} reviews")
    else:
        print(f"Error: {results['error']}")

# Run the collection
asyncio.run(main())
```

## 📊 Data Output

### CSV Format
Reviews are stored in CSV format with the following columns:
- `source`, `review_id`, `author_name`, `rating`, `review_text`
- `review_date`, `helpful_votes`, `response_from_owner`
- `verified_purchase`, `profile_photo_url`, `language`
- `fetched_timestamp`, `sentiment_score`, `photos_attached`
- `owner_response_date`

### Statistics
The system provides comprehensive statistics:
- Total review count by source
- Date range of reviews
- Average ratings
- Review collection metrics
- API usage statistics

## 🔧 Advanced Features

### Custom Scrapers
Extend the system with custom scrapers:

```python
from scrapers.base_scraper import BaseScraper
from models.review import Review

class CustomScraper(BaseScraper):
    async def fetch_reviews(self, business_id: str) -> List[Review]:
        # Implement custom scraping logic
        pass
    
    async def validate_credentials(self) -> bool:
        # Implement credential validation
        pass
    
    async def get_business_info(self, business_id: str) -> Optional[Dict]:
        # Implement business info retrieval
        pass
    
    def get_source_name(self) -> str:
        return "custom"
```

### Data Validation
Customize data validation:

```python
from utils.validators import DataValidator

validator = DataValidator()

# Validate review data
is_valid, errors = validator.validate_review_data(review_data)

# Validate API response
is_valid, errors = validator.validate_api_response(response, "google")
```

### Storage Customization
Extend storage capabilities:

```python
from storage.csv_handler import CSVHandler

csv_handler = CSVHandler("data/reviews.csv", "data/backups/")

# Get statistics
stats = csv_handler.get_review_statistics()

# Export to JSON
csv_handler.export_to_json("data/reviews.json")

# Clean up old backups
deleted_count = csv_handler.cleanup_old_backups(keep_days=30)
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## 📝 Logging

The system provides comprehensive logging:
- Console output for real-time monitoring
- File logging for persistent records
- Configurable log levels
- Structured logging with timestamps

## 🔒 Security Considerations

- API keys are loaded from environment variables
- No sensitive data is logged
- Backup files are stored securely
- Rate limiting prevents API abuse

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review the logs for error messages
3. Verify API credentials and configuration
4. Open an issue on GitHub

## 🔮 Future Enhancements

- **Database Integration**: SQLite/PostgreSQL support
- **Scheduling**: Automated periodic collection
- **Notifications**: Email/Slack alerts for new reviews
- **Analytics**: Advanced sentiment analysis and trends
- **Web Interface**: Dashboard for review management
- **API Endpoints**: REST API for external access
- **Machine Learning**: Predictive analytics and insights