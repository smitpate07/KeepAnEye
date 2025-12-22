import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from keepaneye.read_creds import AppConfig
from keepaneye.price_monitor import PriceMonitor

class NotifyUser:
    """
    Class to handle email notifications for price drops
    """
    def __init__(self):
        """
        Initialize email notifier with SMTP credentials from config
        """
        try:
            self.config = AppConfig()
            self.smtp_server = self.config.SMTP_SERVER
            self.smtp_port = self.config.SMTP_PORT
            self.sender_email = self.config.SENDER_EMAIL
            self.sender_password = self.config.SENDER_PASSWORD
            self.recipient_email = self.config.RECIPIENT_EMAIL
        except Exception as e:
            raise e
    
    def send_price_drop_alert(self, product_data):
        """
        Send price drop notification email
        
        Args:
            product_data: Dictionary containing product information
                - asin: Product ASIN
                - title: Product title
                - current_price: Current price
                - previous_price: Previous price
                - price_drop: Amount saved
                - stock: Stock status
                - brand: Brand name
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Extract product information
            asin = product_data['asin']
            title = product_data['title']
            current_price = product_data['current_price']
            previous_price = product_data['previous_price']
            price_drop = product_data['price_drop']
            stock_status = product_data.get('stock', 'Unknown')
            brand_raw = product_data.get('brand', 'N/A')
            # Remove "Brand: " prefix if it exists
            brand = brand_raw.replace('Brand: ', '').replace('brand: ', '') if brand_raw != 'N/A' else 'N/A'
            
            # Generate Amazon product URL
            product_url = f"https://www.amazon.com/dp/{asin}"
            
            # Create email subject
            subject = f"🎉 Price Drop Alert: {title[:50]}... - Save ${price_drop:.2f}!"
            
            # Create HTML email body
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 20px;
                    }}
                    .email-wrapper {{
                        max-width: 650px;
                        margin: 0 auto;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: white;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    }}
                    .header {{
                        background: linear-gradient(135deg, #232F3E 0%, #131921 100%);
                        color: white;
                        padding: 30px 20px;
                        text-align: center;
                        position: relative;
                    }}
                    .amazon-logo {{
                        width: 120px;
                        height: auto;
                        margin-bottom: 15px;
                    }}
                    .header h1 {{
                        margin: 10px 0 0 0;
                        font-size: 28px;
                        font-weight: bold;
                    }}
                    .alert-badge {{
                        display: inline-block;
                        background-color: #ff4757;
                        color: white;
                        padding: 5px 15px;
                        border-radius: 20px;
                        font-size: 14px;
                        margin-top: 10px;
                        animation: pulse 2s infinite;
                    }}
                    @keyframes pulse {{
                        0%, 100% {{ transform: scale(1); }}
                        50% {{ transform: scale(1.05); }}
                    }}
                    .content {{
                        padding: 30px;
                        background-color: white;
                    }}
                    .product-title {{
                        font-size: 22px;
                        color: #232F3E;
                        margin-bottom: 20px;
                        font-weight: 600;
                        line-height: 1.4;
                    }}
                    .price-section {{
                        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
                        padding: 25px;
                        border-radius: 10px;
                        margin: 25px 0;
                        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.15);
                        border-left: 5px solid #4caf50;
                    }}
                    .price-row {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin: 10px 0;
                    }}
                    .price-label {{
                        font-weight: 600;
                        color: #555;
                        font-size: 16px;
                    }}
                    .price-old {{
                        text-decoration: line-through;
                        color: #999;
                        font-size: 24px;
                    }}
                    .price-new {{
                        color: #4caf50;
                        font-size: 36px;
                        font-weight: bold;
                    }}
                    .savings {{
                        color: #d32f2f;
                        font-size: 24px;
                        font-weight: bold;
                    }}
                    .savings-badge {{
                        background-color: #ff4757;
                        color: white;
                        padding: 8px 16px;
                        border-radius: 25px;
                        display: inline-block;
                        font-size: 16px;
                        font-weight: bold;
                        margin-top: 10px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 18px 40px;
                        background: linear-gradient(135deg, #ff9900 0%, #ff6b00 100%);
                        color: white;
                        text-decoration: none;
                        border-radius: 30px;
                        font-weight: bold;
                        font-size: 18px;
                        margin: 25px 0;
                        text-align: center;
                        box-shadow: 0 6px 20px rgba(255, 153, 0, 0.4);
                        transition: all 0.3s ease;
                    }}
                    .button:hover {{
                        background: linear-gradient(135deg, #e68a00 0%, #e65c00 100%);
                        box-shadow: 0 8px 25px rgba(255, 153, 0, 0.5);
                        transform: translateY(-2px);
                    }}
                    .product-details {{
                        margin: 25px 0;
                        padding: 20px;
                        background: linear-gradient(135deg, #f5f7fa 0%, #e8ecef 100%);
                        border-radius: 10px;
                        border-left: 4px solid #232F3E;
                    }}
                    .detail-row {{
                        display: flex;
                        justify-content: space-between;
                        padding: 8px 0;
                        border-bottom: 1px solid #ddd;
                    }}
                    .detail-row:last-child {{
                        border-bottom: none;
                    }}
                    .detail-label {{
                        font-weight: 600;
                        color: #555;
                    }}
                    .detail-value {{
                        color: #333;
                    }}
                    .stock-badge {{
                        display: inline-block;
                        background-color: #4caf50;
                        color: white;
                        padding: 4px 12px;
                        border-radius: 12px;
                        font-size: 13px;
                    }}
                    .footer {{
                        text-align: center;
                        padding: 25px;
                        background-color: #f5f5f5;
                        color: #666;
                        font-size: 13px;
                        border-top: 1px solid #e0e0e0;
                    }}
                    .divider {{
                        height: 2px;
                        background: linear-gradient(90deg, transparent, #ff9900, transparent);
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="email-wrapper">
                    <div class="container">
                        <div class="header">
                            <svg class="amazon-logo" viewBox="0 0 603 182" fill="white" xmlns="http://www.w3.org/2000/svg">
                                <path d="M374.1 120.8c-33.8 25-82.8 38.3-125 38.3-59.2 0-112.5-21.9-152.8-58.3-3.2-2.9-.3-6.8 3.5-4.6 43.8 25.5 98 40.8 153.8 40.8 37.7 0 79.2-7.8 117.3-24 5.8-2.5 10.7 3.8 5 8.8z"/>
                                <path d="M387.5 105.5c-4.3-5.5-28.5-2.6-39.4-1.3-3.3.4-3.8-2.5-.8-4.6 19.3-13.6 50.9-9.6 54.6-5.1 3.7 4.6-.9 36.4-19.1 51.6-2.8 2.3-5.5 1.1-4.2-2 4.1-10.5 13.4-34.1 9-38.6z"/>
                                <path d="M347.4 16.3v-12c0-1.8 1.4-3 3-3h53.1c1.7 0 3.1 1.2 3.1 3v10.3c0 1.7-1.5 4-4.1 7.5l-27.5 39.3c10.2-.2 21 1.3 30.3 6.3 2.1 1.1 2.7 2.8 2.8 4.4v12.8c0 1.8-1.9 3.8-3.9 2.7-16.6-8.7-38.6-9.7-56.9.1-1.8 1-3.8-1-3.8-2.8v-12.1c0-2 0-5.3 2-8.3l31.9-45.7H350.5c-1.7 0-3.1-1.2-3.1-3z"/>
                                <path d="M124.8 82.6h-16.4c-1.6-.1-2.8-1.3-2.9-2.8V16.6c0-1.7 1.4-3 3.1-3h15.3c1.6.1 2.9 1.3 3 2.9v8.2h.3c4-8.6 11.5-12.5 21.6-12.5 10.3 0 16.7 4 21.3 12.5 4-8.6 13.9-12.5 22.6-12.5 6.9 0 14.4 2.8 19 9.2 5.2 7 4.1 17.2 4.1 26.1l-.1 32.9c0 1.7-1.4 3-3.1 3h-16.4c-1.6-.1-2.9-1.4-2.9-3V37.2c0-3.5.3-12.3-.5-15.6-1.2-5.5-4.8-7.1-9.5-7.1-3.9 0-8 2.6-9.6 6.8-1.7 4.2-1.5 11.2-1.5 15.9v42.2c0 1.7-1.4 3-3.1 3h-16.4c-1.6-.1-2.9-1.4-2.9-3l-.1-42.2c0-8.9 1.4-21.9-10-21.9-11.6 0-11.2 13.2-11.2 21.9v42.2c0 1.7-1.4 3-3.1 3z"/>
                                <path d="M433.7 12.3c24.3 0 37.5 20.9 37.5 47.4 0 25.7-14.6 46-37.5 46-23.9 0-36.9-20.9-36.9-46.9 0-26.2 13.2-46.5 36.9-46.5zm.1 17.1c-12.1 0-12.8 16.4-12.8 26.6 0 10.3-.2 32.1 12.7 32.1 12.7 0 13.3-17.7 13.3-28.5 0-7.1-.3-15.5-2.1-22.2-1.5-5.8-4.6-8-11.1-8z"/>
                                <path d="M503.3 82.6h-16.3c-1.6-.1-2.9-1.4-2.9-3l-.1-63.1c0-1.6 1.3-2.9 3-2.9h15.2c1.4.1 2.6 1.1 2.9 2.4v9.7h.3c4.5-9.1 10.9-13.6 21.9-13.6 7.2 0 14.3 2.6 18.8 9.7 4.2 6.5 4.2 17.4 4.2 25.2v35.4c0 1.6-1.3 2.9-3 2.9h-16.4c-1.5-.1-2.7-1.2-2.8-2.7V47.7c0-8.9 1-21.9-10-21.9-3.9 0-7.5 2.6-9.3 6.5-2.2 4.9-2.5 9.7-2.5 15v32.5c0 1.6-1.3 2.9-3 2.8z"/>
                                <path d="M266.6 66.8c0 6.1.2 11.2-2.9 16.6-2.6 4.4-6.7 7.1-11.2 7.1-6.2 0-9.8-4.7-9.8-11.7 0-13.8 12.4-16.3 24.1-16.3v4.3zm16.5 15.7c-1.1 1-2.6.9-3.8.3-5.4-4.4-6.3-6.5-9.3-10.7-8.9 9-15.2 11.7-26.7 11.7-13.7 0-24.3-8.4-24.3-25.3 0-13.2 7.2-22.2 17.4-26.6 8.8-3.9 21.1-4.6 30.5-5.7v-2.1c0-3.9.3-8.4-2-11.9-2.1-3.1-6.1-4.4-9.6-4.4-6.5 0-12.3 3.3-13.7 10.2-.3 1.5-1.4 3-2.9 3.1l-15.8-1.7c-1.4-.3-2.9-1.4-2.5-3.5 3.7-19.5 21.3-25.4 37.1-25.4 8.1 0 18.6 2.1 25 8.2 8.1 7.6 7.3 17.7 7.3 28.7v26c0 7.8 3.2 11.2 6.3 15.4 1.1 1.5 1.3 3.3-.1 4.4-3.5 3-9.8 8.4-13.3 11.5l-.1-.1z"/>
                                <path d="M48.2 66.8c0 6.1.2 11.2-2.9 16.6-2.6 4.4-6.7 7.1-11.2 7.1-6.2 0-9.8-4.7-9.8-11.7 0-13.8 12.4-16.3 24.1-16.3v4.3zm16.5 15.7c-1.1 1-2.6.9-3.8.3-5.4-4.4-6.3-6.5-9.3-10.7-8.9 9-15.2 11.7-26.7 11.7C11.2 83.8.6 75.4.6 58.5c0-13.2 7.2-22.2 17.4-26.6 8.8-3.9 21.1-4.6 30.5-5.7v-2.1c0-3.9.3-8.4-2-11.9-2.1-3.1-6.1-4.4-9.6-4.4-6.5 0-12.3 3.3-13.7 10.2-.3 1.5-1.4 3-2.9 3.1L4.5 19.4c-1.4-.3-2.9-1.4-2.5-3.5C5.7-3.6 23.3-9.5 39.1-9.5c8.1 0 18.6 2.1 25 8.2 8.1 7.6 7.3 17.7 7.3 28.7v26c0 7.8 3.2 11.2 6.3 15.4 1.1 1.5 1.3 3.3-.1 4.4-3.5 3-9.8 8.4-13.3 11.5l-.6-.2z"/>
                            </svg>
                            <h1>🔔 Price Drop Alert!</h1>
                            <span class="alert-badge">Limited Time Offer</span>
                        </div>
                        
                        <div class="content">
                            <div class="product-title">{title}</div>
                            
                            <div class="divider"></div>
                            
                            <div class="price-section">
                                <div class="price-row">
                                    <span class="price-label">Previous Price:</span>
                                    <span class="price-old">${previous_price:.2f}</span>
                                </div>
                                <div class="price-row">
                                    <span class="price-label">Current Price:</span>
                                    <span class="price-new">${current_price:.2f}</span>
                                </div>
                                <div class="divider" style="margin: 15px 0;"></div>
                                <div style="text-align: center;">
                                    <div class="savings">Save ${price_drop:.2f}</div>
                                    <span class="savings-badge">{(price_drop/previous_price*100):.1f}% OFF</span>
                                </div>
                            </div>
                            
                            <div class="product-details">
                                <div class="detail-row">
                                    <span class="detail-label">Brand:</span>
                                    <span class="detail-value">{brand}</span>
                                </div>
                                <div class="detail-row">
                                    <span class="detail-label">Stock Status:</span>
                                    <span class="stock-badge">{stock_status}</span>
                                </div>
                                <div class="detail-row">
                                    <span class="detail-label">ASIN:</span>
                                    <span class="detail-value">{asin}</span>
                                </div>
                            </div>
                            
                            <center>
                                <a href="{product_url}" class="button">🛒 Buy Now on Amazon</a>
                            </center>
                            
                            <p style="text-align: center; margin-top: 20px; color: #888; font-size: 14px;">
                                <em>Act fast! Prices may change at any time.</em>
                            </p>
                        </div>
                        
                        <div class="footer">
                            <p style="margin: 5px 0;">📊 <strong>KeepAnEye</strong> - Your Smart Shopping Assistant</p>
                            <p style="margin: 5px 0; color: #999;">Notification sent on {datetime.now().strftime("%B %d, %Y at %I:%M %p UTC")}</p>
                            <p style="margin: 15px 0 5px 0; font-size: 11px; color: #aaa;">This is an automated notification. You're receiving this because you're monitoring this product.</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create plain text version as fallback
            text_body = f"""
            PRICE DROP ALERT!
            
            Product: {title}
            
            Previous Price: ${previous_price:.2f}
            Current Price: ${current_price:.2f}
            You Save: ${price_drop:.2f} ({(price_drop/previous_price*100):.1f}% OFF)
            
            Brand: {brand}
            Stock Status: {stock_status}
            ASIN: {asin}
            
            Buy Now: {product_url}
            
            ---
            This is an automated notification from your AWS Price Tracker.
            Sent on {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
            """
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = self.recipient_email
            
            # Attach both plain text and HTML versions
            part1 = MIMEText(text_body, "plain")
            part2 = MIMEText(html_body, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Enable security
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            print(f"✓ Price drop alert email sent to {self.recipient_email}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send email: {str(e)}")
            return False
    
    def check_and_notify(self, asin):
        """
        Check for price drops and send notification if detected
        
        Args:
            asin: Product ASIN to check
        
        Returns:
            bool: True if notification was sent, False otherwise
        """
        try:
            print(f"\n📊 Checking for price changes...")
            
            # Initialize price monitor
            monitor = PriceMonitor()
            
            # Check for price changes
            result = monitor.check_price_changes(asin, 'asin')
            
            if result is None:
                print("ℹ️  Not enough data for price comparison")
                return False
            
            # If price dropped, send notification
            if result['price_dropped']:
                print("\n📧 Sending email notification...")
                success = self.send_price_drop_alert(result['product_data'])
                return success
            else:
                print("\nℹ️  No price drop - no notification sent")
                return False
                
        except Exception as e:
            print(f"✗ Error in check_and_notify: {str(e)}")
            return False