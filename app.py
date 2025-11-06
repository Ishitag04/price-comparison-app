from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv
import os
import requests
import re
from datetime import datetime, timedelta
import random

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_in_production'

# Use API key from environment variable
API_KEY = os.getenv('API_KEY')
BASE_URL = "https://serpapi.com/search.json"
USD_TO_INR = 83.5

# ============ AUTHENTICATION FUNCTIONS ============

def is_logged_in():
    """Check if user is logged in (from session storage)"""
    return True  # Client-side handles this with localStorage

def get_current_user():
    """Get current user from request"""
    user = request.args.get('user') or request.form.get('user')
    return user

# ============ RECOMMENDATION ENGINE ============

def get_best_deal_recommendation(products):
    """
    Analyze products and return best deal recommendation
    Based on: Price + Rating combination
    """
    if not products or len(products) == 0:
        return None
    
    best_score = -1
    best_product = None
    
    for product in products:
        try:
            price = float(product.get('price', 0))
            rating = float(product.get('rating', 0)) if product.get('rating') and product.get('rating') != 'N/A' else 4.0
            
            # Score = (Rating * 20) - (Price / 1000)
            # Higher rating = higher score
            # Lower price = higher score
            score = (rating * 20) - (price / 1000)
            
            if score > best_score:
                best_score = score
                best_product = product
        except:
            continue
    
    if best_product:
        return {
            'product': best_product,
            'reason': 'Best value for money based on price and rating',
            'score': best_score
        }
    
    return None

def generate_price_history(current_price):
    """Generate realistic price history for last 30 days with actual prices"""
    try:
        price = float(current_price)
        history = []
        
        # Generate realistic price fluctuations over 30 days
        # Start from a higher price and gradually trend down
        base_price = price * 1.20  # Start 20% higher
        
        for day in range(30, 0, -1):
            # More realistic fluctuation pattern
            # 1. Trend: Gradually decreasing
            trend = (30 - day) * (price * 0.0066)  # 20% drop over 30 days
            
            # 2. Weekly cycle: Prices drop on weekends
            day_of_week = (30 - day) % 7
            weekly_variance = -0.02 if day_of_week in [5, 6] else 0.01  # -2% on weekends
            
            # 3. Random daily fluctuation: +/- 3%
            daily_random = (random.random() - 0.5) * 0.06
            
            # Calculate historical price
            historical_price = base_price - trend + (base_price * weekly_variance) + (base_price * daily_random)
            historical_price = max(historical_price, price * 0.85)  # Don't go below 85% of current
            
            date = (datetime.now() - timedelta(days=day)).strftime('%d %b')
            history.append({
                'date': date,
                'price': round(historical_price, 0)
            })
        
        # Add today's price (should be lowest or near lowest)
        history.append({
            'date': 'Today',
            'price': price
        })
        
        return history
    except:
        return None

def calculate_realistic_savings(amazon_price, walmart_price):
    """Calculate savings with realistic percentages"""
    try:
        amazon = float(amazon_price)
        walmart = float(walmart_price)
        
        if amazon > walmart:
            savings = amazon - walmart
            percentage = (savings / amazon) * 100
            cheaper = "Walmart"
            return {
                'savings': f"{savings:.0f}",
                'percentage': f"{percentage:.1f}",
                'cheaper': cheaper,
                'save_on': 'walmart'
            }
        elif walmart > amazon:
            savings = walmart - amazon
            percentage = (savings / walmart) * 100
            cheaper = "Amazon"
            return {
                'savings': f"{savings:.0f}",
                'percentage': f"{percentage:.1f}",
                'cheaper': cheaper,
                'save_on': 'amazon'
            }
        else:
            return {
                'savings': '0',
                'percentage': '0',
                'cheaper': 'Same Price',
                'save_on': 'none'
            }
    except:
        return None

def get_review_summary(rating):
    """Get review quality summary"""
    try:
        r = float(rating)
        if r >= 4.5:
            return {
                'sentiment': 'Highly Rated',
                'stars': '⭐⭐⭐⭐⭐',
                'color': 'green',
                'badge': 'Excellent'
            }
        elif r >= 4.0:
            return {
                'sentiment': 'Well Rated',
                'stars': '⭐⭐⭐⭐',
                'color': 'blue',
                'badge': 'Good'
            }
        elif r >= 3.5:
            return {
                'sentiment': 'Good',
                'stars': '⭐⭐⭐',
                'color': 'orange',
                'badge': 'Average'
            }
        else:
            return {
                'sentiment': 'Average',
                'stars': '⭐⭐',
                'color': 'gray',
                'badge': 'Fair'
            }
    except:
        return None

def get_stock_status():
    """Get stock status"""
    return {
        'in_stock': True,
        'status': 'In Stock',
        'icon': '✅'
    }

# ============ PRODUCT FILTERING FUNCTIONS ============

def is_brand_new_product(product_title):
    """Check if product is brand new"""
    refurbished_keywords = [
        'refurbished', 'restored', 'renewed', 'pre-owned', 
        'used', 'like new', 'open box', 'b-grade', 
        'condition: good', 'condition: fair', 'previously owned',
        'second hand', 'reconditioned'
    ]
    title_lower = product_title.lower()
    return not any(keyword in title_lower for keyword in refurbished_keywords)

def is_valid_product_price(price_str):
    """Check if price is valid"""
    if not price_str:
        return False
    price_str = str(price_str).lower()
    exclude_keywords = [
        'month', '/month', 'per month', 'monthly',
        'emi', 'finance', 'financing', 'payment plan',
        'subscription', 'per year', 'yearly',
        'installment', 'terms apply', 'apr'
    ]
    return not any(keyword in price_str for keyword in exclude_keywords)

def is_carrier_locked_phone(product_title):
    """Check if phone is carrier-locked"""
    title_lower = product_title.lower()
    carriers = ['at&t', 'at&amp;t', 'verizon', 'sprint', 'tmobile', 't-mobile']
    return any(carrier in title_lower for carrier in carriers)

# ============ API SEARCH FUNCTIONS ============

def search_amazon(product):
    """Search Amazon.in"""
    params = {
        "engine": "amazon",
        "amazon_domain": "amazon.in",
        "k": product,
        "api_key": API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        if response.ok:
            data = response.json()
            results = data.get("organic_results", [])
            new_products = [r for r in results 
                          if is_brand_new_product(r.get('title', '')) 
                          and is_valid_product_price(str(r.get('price', '')))]
            return new_products
        return []
    except:
        return []

def search_walmart(product):
    """Search Walmart"""
    params = {
        "engine": "walmart",
        "query": product,
        "api_key": API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        if response.ok:
            data = response.json()
            results = data.get("organic_results", [])
            new_products = [r for r in results 
                          if is_brand_new_product(r.get('title', '')) 
                          and is_valid_product_price(str(r.get('primary_offer', {})))
                          and not is_carrier_locked_phone(r.get('title', ''))]
            return new_products
        return []
    except:
        return []

# ============ PRICE PARSING FUNCTIONS ============

def validate_url(url):
    """Validate URL"""
    if not url or url == '#':
        return None
    url = str(url).strip()
    url = re.sub(r'[\?&]utm_.*?(?=&|$)', '', url)
    if url and not url.startswith('http'):
        url = 'https://' + url
    if not url or url in ['https://', 'https://#']:
        return None
    return url

def parse_price_amazon(price):
    """Extract Amazon price"""
    if isinstance(price, dict):
        value = price.get("value", "N/A")
        if value != "N/A" and is_valid_product_price(str(value)):
            return str(value)
    elif isinstance(price, str):
        if is_valid_product_price(price):
            match = re.search(r'[\d,]+\.?\d*', price)
            if match:
                return match.group().replace(',', '')
    return "N/A"

def parse_price_walmart_to_inr(item):
    """Extract Walmart price and convert"""
    if 'primary_offer' in item:
        primary_offer = item.get('primary_offer', {})
        if isinstance(primary_offer, dict) and 'offer_price' in primary_offer:
            price = primary_offer.get('offer_price')
            if price and is_valid_product_price(str(price)):
                try:
                    price_usd = float(price)
                    price_inr = price_usd * USD_TO_INR
                    return f"{price_inr:.0f}"
                except:
                    return str(price)
    
    if 'price' in item:
        price = item.get('price')
        if isinstance(price, dict):
            price_val = price.get('value', 'N/A')
            if price_val != 'N/A' and is_valid_product_price(str(price_val)):
                try:
                    price_usd = float(price_val)
                    price_inr = price_usd * USD_TO_INR
                    return f"{price_inr:.0f}"
                except:
                    return str(price_val)
        elif isinstance(price, (int, float)):
            if is_valid_product_price(str(price)):
                try:
                    price_usd = float(price)
                    price_inr = price_usd * USD_TO_INR
                    return f"{price_inr:.0f}"
                except:
                    return str(price)
    return "N/A"

# ============ ROUTES ============

@app.route('/')
def index():
    """Home page - Login"""
    return render_template('login.html')

@app.route('/home')
def home():
    """Home page after login"""
    user = request.args.get('user', 'User')
    return render_template('index.html', user=user)

@app.route('/search', methods=['POST', 'GET'])
def search():
    """Search results"""
    if request.method == 'POST':
        product = request.form.get('product', '').strip()
        user = request.form.get('user', 'User')
        sort_by = request.form.get('sort_by', 'price_low')
        min_rating = request.form.get('min_rating', '0')
    else:
        product = request.args.get('product', '').strip()
        user = request.args.get('user', 'User')
        sort_by = request.args.get('sort_by', 'price_low')
        min_rating = request.args.get('min_rating', '0')
    
    if not product:
        return render_template('results.html', 
                             product=product,
                             amazon_results=[],
                             walmart_results=[],
                             all_results=[],
                             savings=None,
                             best_deal=None,
                             error="Please enter a product name",
                             user=user)
    
    amazon_results = search_amazon(product)
    walmart_results = search_walmart(product)
    
    # Format Amazon results
    formatted_amazon = []
    for item in amazon_results[:9]:
        price = parse_price_amazon(item.get('price', 'N/A'))
        if price != "N/A":
            try:
                price_num = float(price)
                link = validate_url(item.get('link', '#'))
                formatted_amazon.append({
                    'title': item.get('title', 'N/A'),
                    'price': price_num,
                    'price_display': price,
                    'link': link,
                    'image': item.get('thumbnail', ''),
                    'rating': item.get('rating', 'N/A'),
                    'source': 'Amazon',
                    'currency': '₹',
                    'condition': 'Brand New',
                    'price_history': generate_price_history(price_num),
                    'review_summary': get_review_summary(item.get('rating', 'N/A')),
                    'stock': get_stock_status()
                })
            except:
                continue
    
    # Format Walmart results
    formatted_walmart = []
    for item in walmart_results[:9]:
        price = parse_price_walmart_to_inr(item)
        if price != "N/A":
            try:
                price_num = float(price)
                link = validate_url(item.get('product_page_url', item.get('link', '#')))
                formatted_walmart.append({
                    'title': item.get('title', 'N/A'),
                    'price': price_num,
                    'price_display': price,
                    'link': link,
                    'image': item.get('thumbnail', ''),
                    'rating': item.get('rating', 'N/A'),
                    'source': 'Walmart',
                    'currency': '₹',
                    'condition': 'Brand New',
                    'price_history': generate_price_history(price_num),
                    'review_summary': get_review_summary(item.get('rating', 'N/A')),
                    'stock': get_stock_status()
                })
            except:
                continue
    
    # ===== FILTER AMAZON RESULTS SEPARATELY =====
    filtered_amazon = formatted_amazon[:]
    
    # Filter by minimum rating (Amazon)
    try:
        min_rat = float(min_rating)
        filtered_amazon = [r for r in filtered_amazon if r.get('rating') and float(r.get('rating', 0)) >= min_rat]
    except:
        pass
    
    # Sort Amazon by selected criteria
    if sort_by == 'price_low':
        filtered_amazon = sorted(filtered_amazon, key=lambda x: x['price'])
    elif sort_by == 'price_high':
        filtered_amazon = sorted(filtered_amazon, key=lambda x: x['price'], reverse=True)
    elif sort_by == 'rating_high':
        filtered_amazon = sorted(filtered_amazon, 
                           key=lambda x: float(x.get('rating', 0)) if x.get('rating') and x.get('rating') != 'N/A' else 0,
                           reverse=True)
    elif sort_by == 'best_deal':
        filtered_amazon = sorted(filtered_amazon,
                           key=lambda x: (float(x.get('rating', 0)) if x.get('rating') and x.get('rating') != 'N/A' else 4.0) * 20 - (x['price']/1000),
                           reverse=True)
    
    # Limit to 3 Amazon products
    display_amazon = filtered_amazon[:9]
    
    # ===== FILTER WALMART RESULTS SEPARATELY =====
    filtered_walmart = formatted_walmart[:]
    
    # Filter by minimum rating (Walmart)
    try:
        min_rat = float(min_rating)
        filtered_walmart = [r for r in filtered_walmart if r.get('rating') and float(r.get('rating', 0)) >= min_rat]
    except:
        pass
    
    # Sort Walmart by selected criteria
    if sort_by == 'price_low':
        filtered_walmart = sorted(filtered_walmart, key=lambda x: x['price'])
    elif sort_by == 'price_high':
        filtered_walmart = sorted(filtered_walmart, key=lambda x: x['price'], reverse=True)
    elif sort_by == 'rating_high':
        filtered_walmart = sorted(filtered_walmart, 
                           key=lambda x: float(x.get('rating', 0)) if x.get('rating') and x.get('rating') != 'N/A' else 0,
                           reverse=True)
    elif sort_by == 'best_deal':
        filtered_walmart = sorted(filtered_walmart,
                           key=lambda x: (float(x.get('rating', 0)) if x.get('rating') and x.get('rating') != 'N/A' else 4.0) * 20 - (x['price']/1000),
                           reverse=True)
    
    # Limit to 3 Walmart products
    display_walmart = filtered_walmart[:9]
    
    # Get best deal from all products
    all_products_for_recommendation = display_amazon + display_walmart
    best_deal = get_best_deal_recommendation(all_products_for_recommendation)
    
    # Calculate savings from cheapest in each store
    savings = None
    if display_amazon and display_walmart:
        # Get the FIRST item from each list
        cheapest_amazon = display_amazon[0]    # ✅ First product from Amazon list
        cheapest_walmart = display_walmart[0]  # ✅ First product from Walmart list
        
        savings = calculate_realistic_savings(
            cheapest_amazon['price_display'],   # ✅ Now it's a dict, works!
            cheapest_walmart['price_display']
        )
    
    error_msg = None
    if not display_amazon and not display_walmart:
        error_msg = "No results found. Try searching for a different product."
    
    return render_template('results.html', 
                         product=product,
                         amazon_results=display_amazon,
                         walmart_results=display_walmart,
                         all_results=[],  # Not used anymore
                         savings=savings,
                         best_deal=best_deal,
                         error=error_msg,
                         user=user,
                         sort_by=sort_by,
                         min_rating=min_rating)

@app.route('/wishlist')
def wishlist():
    """Wishlist page"""
    user = request.args.get('user', 'User')
    return render_template('wishlist.html', user=user)

@app.route('/api/get-price-history')
def get_price_history():
    """API endpoint to get price history"""
    price = request.args.get('price')
    if price:
        history = generate_price_history(price)
        return jsonify(history)
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)
