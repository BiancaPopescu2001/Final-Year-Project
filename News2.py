import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea, QFrame, \
    QHBoxLayout, QSizePolicy, QTextBrowser, QPushButton
from PyQt5.QtGui import QFont, QPixmap, QPainter
from PyQt5.QtCore import Qt, QSize
from datetime import datetime
import webbrowser

# Function to split text into lines with word boundaries
def split_text(text, max_length):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_length:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return "\n".join(lines)

# Function to open the article link in a web browser
def open_link(link):
    webbrowser.open(link)

class CryptoChartApp(QMainWindow):
    def __init__(self, indicator='MACD'):
        super().__init__()

        # Create a central widget and set it as the main window's central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a vertical layout for the central widget
        layout = QVBoxLayout(central_widget)

        # Set a larger font size for article labels
        font = QFont()
        font.setPointSize(14)

        self.background_image = QPixmap("fundal.jpeg")

        # Replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
        url = 'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=COIN&limit=50&apikey=WSQO8RRXYJPTR6GG'
        r = requests.get(url)
        data = r.json()

        # Check if "feed" key exists in the data
        if "feed" in data:
            # Create a scroll area for vertical scrolling
            scroll_area = QScrollArea(self)
            scroll_area.setWidgetResizable(True)
            layout.addWidget(scroll_area)

            # Create a widget for the scroll area
            scroll_widget = QWidget(scroll_area)
            scroll_area.setWidget(scroll_widget)
            scroll_layout = QVBoxLayout(scroll_widget)

            # Define sentiment colors
            sentiment_colors = {
                "Bullish": "background-color: #29a329;",  # Green
                "Somewhat-Bullish": "background-color: #5cd65c;",  # Light Green
                "Bearish": "background-color: #cc0000;",  # Red
                "Somewhat-Bearish": "background-color: #ff3333;",  # Light Red
                "Neutral": "background-color: orange;"  # Orange
            }

            # Iterate through each item in the "feed"
            for item in data["feed"]:
                # Create a widget for each article
                article_widget = QWidget()
                article_layout = QVBoxLayout(article_widget)



                # Create a horizontal layout for the title and icon
                title_layout = QHBoxLayout()

                # Add title label to the title_layout
                title_label = QLabel("Title: " + item["title"])
                title_label.setFont(font)
                title_layout.addWidget(title_label)

                # Add a clickable PNG icon next to the title
                icon_label = QLabel()
                icon_pixmap = QPixmap("link.png")  # Replace "icon.png" with your PNG icon file
                if not icon_pixmap.isNull():
                    icon_pixmap = icon_pixmap.scaled(20, 20, Qt.KeepAspectRatio)  # Resize the icon
                    icon_label.setPixmap(icon_pixmap)
                    icon_label.setCursor(Qt.PointingHandCursor)  # Change cursor to hand when hovering
                    icon_label.mousePressEvent = lambda event, url=item["url"]: open_link(url)  # Open link on click
                    title_layout.addWidget(icon_label)

                article_layout.addLayout(title_layout)

                # Split the summary text into lines with word boundaries
                max_chars_per_line = 100  # You can adjust this value
                summary_text = item["summary"]
                summary_lines = split_text(summary_text, max_chars_per_line)

                # Create a QTextBrowser for the summary with HTML formatting for text wrapping
                summary_browser = QTextBrowser()
                summary_browser.setOpenExternalLinks(True)  # Allow external links to be opened
                summary_browser.setHtml("Summary:<br>" + summary_lines)  # Set HTML content
                summary_browser.setFont(font)

                # Set background color based on sentiment
                sentiment = item["overall_sentiment_label"]
                if sentiment in sentiment_colors:
                    summary_browser.setStyleSheet(sentiment_colors[sentiment])

                # Limit the maximum width of summary_browser
                summary_browser.setMaximumWidth(1000)  # Adjust the maximum width as needed

                # Restrict the summary field's width to the text size
                summary_browser.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

                article_layout.addWidget(summary_browser)

                # Parse the timestamp and format it as desired
                timestamp = datetime.strptime(item["time_published"], "%Y%m%dT%H%M%S")
                formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M")
                time_published_label = QLabel("Time Published: " + formatted_timestamp)
                time_published_label.setFont(font)
                article_layout.addWidget(time_published_label)

                # Add overall_sentiment_label to the article
                overall_sentiment_label = QLabel("Overall Sentiment: " + sentiment)
                overall_sentiment_label.setFont(font)

                # Set background color based on sentiment
                if sentiment in sentiment_colors:
                    overall_sentiment_label.setStyleSheet(sentiment_colors[sentiment])

                # Limit the maximum width of overall_sentiment_label
                overall_sentiment_label.setMaximumWidth(400)  # Adjust the maximum width as needed

                article_layout.addWidget(overall_sentiment_label)

                # Add a horizontal line to separate articles
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setFrameShadow(QFrame.Sunken)
                article_layout.addWidget(line)

                scroll_layout.addWidget(article_widget)

            # Limit the maximum width of the scroll_widget
            scroll_widget.setMaximumWidth(800)  # Adjust the maximum width as needed

            # Set the scroll area as the central widget
            self.setCentralWidget(scroll_area)

def main():
    app = QApplication(sys.argv)
    window = CryptoChartApp()
    window.setWindowTitle('Crypto News')
    window.setGeometry(100, 100, 1300, 700)  # Adjust the window dimensions here
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
