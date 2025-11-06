# 💰 Price Compare - Shop Mitra

A Flask-based web application for comparing product prices across Amazon India and Walmart USA with real-time price tracking, AI-powered recommendations, and wishlist management.

## Features

✅ **Price Comparison** - Compare Amazon & Walmart prices instantly
✅ **Brand New Products Only** - Filter refurbished/used items automatically
✅ **Price Range Sorting** - Sort by low to high or high to low prices
✅ **Best Deal Recommendation** - AI algorithm suggests best value (Mitra's Recommendation)
✅ **Price Trend Charts** - 30-day price history with realistic fluctuations
✅ **Wishlist Management** - Save favorite products for later
✅ **Multi-Platform Sharing** - Share on WhatsApp, Email, Twitter, Facebook
✅ **Dark Mode** - Comfortable viewing in low light
✅ **User Authentication** - Sign-in system (no database required)
✅ **Responsive Design** - Works on desktop and mobile

## Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JavaScript
- **API:** SerpAPI for web scraping
- **Charts:** Plotly.js for price visualizations
- **Storage:** LocalStorage for user preferences

## Installation

### Prerequisites

- Python 3.7+
- pip (Python package manager)
- Git

### Setup Instructions

1. **Clone the repository:**

2. **Create a virtual environment:**

3. **Install dependencies:**

4. **Create `.env` file:**
Create a `.env` file in the project root and add your SerpAPI key:

Get your API key from [SerpAPI](https://serpapi.com)

5. **Run the application:**

6. **Open in browser:**
Navigate to `http://localhost:5000`

## Project Structure


## How to Use

1. **Sign In:** Enter your name on the login page
2. **Search:** Enter a product name (e.g., iPhone, Laptop)
3. **Compare:** See prices from Amazon & Walmart
4. **Filter:** Sort by price, rating, or best deals
5. **Analyze:** View 30-day price trends
6. **Save:** Add to wishlist for later
7. **Share:** Share with friends on social media

## Key Algorithms

### Best Deal Recommendation
Higher rating = higher score, Lower price = higher score

### Price History
- Realistic 30-day price simulation
- Downward trend (prices decrease over time)
- Weekly patterns (weekend discounts)
- Daily fluctuations (+/- 6%)

## Configuration

- **API Key:** Add to `.env` file
- **Currency Conversion:** USD_TO_INR = 83.5 (editable in app.py)
- **Max Products:** 3 per store (editable in app.py)

## Future Enhancements

- [ ] Add more e-commerce platforms
- [ ] Email price alerts
- [ ] Historical price database
- [ ] Mobile app
- [ ] User accounts with database
- [ ] Advanced analytics dashboard

## Contributing

Feel free to fork this project and submit pull requests for improvements!

## Author

Built with ❤️ for InnoTech

## Support

For issues or questions, open an issue on GitHub.

---
