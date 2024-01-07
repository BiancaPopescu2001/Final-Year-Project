import webbrowser

import praw
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPainter
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication, QFrame, QPushButton, QHBoxLayout, QDialog, \
    QTextEdit, QScrollArea
from collections import Counter
from praw.models import MoreComments
from textblob import TextBlob


class SentimentCommentWindow(QDialog):
    def __init__(self, sentiment, comments):
        super().__init__()
        self.setWindowTitle(f"{sentiment.capitalize()} Comments")

        layout = QVBoxLayout(self)

        self.background_image = QPixmap("fundal.jpeg")

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        formatted_comments = []
        for idx, comment in enumerate(comments):
            comment_text = f"{idx + 1}) {comment[0]}\n"
            vote_text = f"[{comment[1]} votes]"

            # Stilizare pentru textul comentariului
            comment_text = f"<div style='color: blue; font-size: 20px;'>{comment_text}</div>"

            # Stilizare pentru textul numărului de voturi cu dimensiune mărită
            vote_text = f"<span style='color: green; font-size: 18px;'>{vote_text}</span>"

            formatted_comment = f"{comment_text}{vote_text}"

            # Adăugăm un rând liber după fiecare comentariu
            formatted_comment += "<br>"

            formatted_comments.append(formatted_comment)

        text = "\n".join(formatted_comments)
        text_edit.setHtml(text)  # Utilizăm setHtml pentru a interpreta stilizarea HTML

        layout.addWidget(text_edit)

        self.resize(1000, 800)


class SentimentAnalysisTab(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

        self.background_image = QPixmap("fundal.jpeg")

    def paintEvent(self, event):
        # Desenează imaginea de fundal
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background_image)

    def analyze_sentiment(self, text):
        analysis = TextBlob(text)
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity < 0:
            return 'negative'
        else:
            return 'neutral'

    def show_sentiment_comments(self, sentiment, comments):
        sentiment_window = SentimentCommentWindow(sentiment, comments)
        sentiment_window.exec_()

    def open_reddit_post(self, post_url):
        webbrowser.open(post_url)

    def init_ui(self):
        app = QApplication.instance()
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        layout = QVBoxLayout(self)

        subreddit_name = 'CryptoCurrency'
        post_limit = 10

        reddit = praw.Reddit(
            client_id='KCs71Zxi_4aoUg-XC959qw',
            client_secret='fGzl6Pm2zVOnjD-3zCI_LG7hoiofog',
            user_agent='-6YnCe9mHUZB_bG3_faEJQ',
            username='Longjumping-Nature94',
            password='f#dD8frsNSB?/u4'
        )

        subreddit = reddit.subreddit(subreddit_name)
        post_count = 0

        title_font = QFont()
        title_font.setPointSize(13)  # Mărimea fontului pentru titluri



        for post in subreddit.hot(limit=None):
            if post_count >= post_limit:
                break

            post_count += 1

            title_label = QLabel(f"{post.title}")
            title_label.setWordWrap(True)

            title_label.setFont(title_font)

            # Add a label with a link image
            link_label = QLabel()
            link_pixmap = QPixmap("link.png")  # Replace with the actual path to your link image
            link_pixmap = link_pixmap.scaledToWidth(20)  # Scale the link icon
            link_label.setPixmap(link_pixmap)
            link_label.setCursor(Qt.PointingHandCursor)
            link_label.mousePressEvent = lambda event, url=post.url: self.open_reddit_post(url)

            title_layout = QHBoxLayout()
            title_layout.addWidget(title_label)
            title_layout.addWidget(link_label)  # Add link icon immediately after the title

            layout.addLayout(title_layout)

            positive_comments = []
            negative_comments = []
            neutral_comments = []

            post.comments.replace_more(limit=0)
            for comment in post.comments.list()[:50]:
                if isinstance(comment, MoreComments):
                    continue
                sentiment = self.analyze_sentiment(comment.body)
                if sentiment == 'positive':
                    positive_comments.append((comment.body, comment.score))
                elif sentiment == 'negative':
                    negative_comments.append((comment.body, comment.score))
                else:
                    neutral_comments.append((comment.body, comment.score))

            sentiment_counts = Counter([self.analyze_sentiment(comment.body) for comment in post.comments.list()[:50]])
            most_common_sentiment = sentiment_counts.most_common(1)[0][0]

            positive_button = QPushButton(f"Positive ({sentiment_counts['positive']})")
            negative_button = QPushButton(f"Negative ({sentiment_counts['negative']})")
            neutral_button = QPushButton(f"Neutral ({sentiment_counts['neutral']})")

            positive_icon = QIcon(QPixmap("positiv.png"))  # Replace with the actual path to your image
            negative_icon = QIcon(QPixmap("negativ.png"))  # Replace with the actual path to your image
            neutral_icon = QIcon(QPixmap("neutral.png"))  # Replace with the actual path to your image

            positive_button.setIcon(positive_icon)
            negative_button.setIcon(negative_icon)
            neutral_button.setIcon(neutral_icon)

            button_size = QSize(60, 60)  # Adjust the width and height as needed
            positive_button.setIconSize(button_size)
            negative_button.setIconSize(button_size)
            neutral_button.setIconSize(button_size)

            if most_common_sentiment == 'positive':
                positive_button.setStyleSheet("background-color: #29a329; color: white;")
                negative_button.setStyleSheet("")
                neutral_button.setStyleSheet("")
            elif most_common_sentiment == 'negative':
                positive_button.setStyleSheet("")
                negative_button.setStyleSheet("background-color: #cc0000; color: white;")
                neutral_button.setStyleSheet("")
            else:
                positive_button.setStyleSheet("")
                negative_button.setStyleSheet("")
                neutral_button.setStyleSheet("background-color: orange; color: white;")

            positive_button.clicked.connect(lambda _, c=positive_comments: self.show_sentiment_comments("positive", c))
            negative_button.clicked.connect(lambda _, c=negative_comments: self.show_sentiment_comments("negative", c))
            neutral_button.clicked.connect(lambda _, c=neutral_comments: self.show_sentiment_comments("neutral", c))

            button_layout = QHBoxLayout()
            button_layout.addWidget(positive_button)
            button_layout.addWidget(negative_button)
            button_layout.addWidget(neutral_button)
            layout.addLayout(button_layout)

            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            layout.addWidget(line)

        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_content.setLayout(layout)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_content)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    tab = SentimentAnalysisTab()
    tab.show()
    sys.exit(app.exec_())
