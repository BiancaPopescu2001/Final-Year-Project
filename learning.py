import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QLabel, QPushButton, QFrame, QWidget, QDialog, QTextEdit, \
    QScrollArea
from PyQt5.QtGui import QFont, QPainter, QPixmap  # Importați QFont pentru a modifica dimensiunea textului

class LearningTab(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

        self.background_image = QPixmap("fundal.jpeg")

    def show_example_text(self, example_text):
        example_window = ExampleTextWindow(example_text)
        example_window.exec_()

    def run_suprapunere(self):
        # Get the full path to the Python interpreter
        python_executable = sys.executable

        # Execute the "suprapunere.py" file using subprocess with the Python interpreter path
        subprocess.run([python_executable, "suprapunere.py"])

    def show_rsi(self):
        # Call the indicators.py script for displaying RSI
        subprocess.run([sys.executable, "suprapunere.py", "RSI"])

    def show_vwap(self):
        # Call the indicators.py script for displaying VWAP
        subprocess.run([sys.executable, "suprapunere.py", "VWAP"])

    def show_ema(self):
        # Call the indicators.py script for displaying EMA
        subprocess.run([sys.executable, "suprapunere.py", "EMA"])

    def show_aroon(self):
        subprocess.run([sys.executable, "suprapunere.py", "AROON"])

    def show_bollinger(self):
        subprocess.run([sys.executable, "suprapunere.py", "BOLLINGER"])

    def show_roc(self):
        subprocess.run([sys.executable, "suprapunere.py", "ROC"])


    def show_sar(self):
        subprocess.run([sys.executable, "suprapunere.py", "SAR"])

    def paintEvent(self, event):
        # Desenează imaginea de fundal
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background_image)

    def execute_action(self, action_name):
        if action_name == "Show MACD on graphic":
            self.run_suprapunere()
        elif action_name == "Show RSI on graphic":
            self.show_rsi()
        elif action_name == "Show VWAP on graphic":
            self.show_vwap()
        elif action_name == "Show EMA on graphic":
            self.show_ema()
        elif action_name == "Show Aroon on graphic":
            self.show_aroon()
        elif action_name == "Show B.B. on graphic":
            self.show_bollinger()
        elif action_name == "Show ROC on graphic":
            self.show_roc()
        elif action_name == "Show SAR on graphic":
            self.show_sar()

    def init_ui(self):
        self.setWindowTitle("Learning")
        layout = QVBoxLayout(self)

        # Create a scroll area for vertical scrolling
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # Create a widget for the scroll area
        scroll_widget = QWidget(scroll_area)
        scroll_area.setWidget(scroll_widget)
        scroll_layout = QVBoxLayout(scroll_widget)

        # Lista cu texte pentru 8 exemple
        example_texts = [
            '<span style="color:blue; font-weight:bold;">INFO:</span><br> MACD (Moving Average Convergence Divergence) generates a trading signal when the signal line (Signal line, red in this <br> case) crosses the main MACD line (MACD line, blue in this case), indicating potential changes in the direction of a price.<br><br>'
    'When the signal line crosses above the MACD line, it may suggest a buy (bullish) signal, while a signal line crossing <br> below the MACD line may suggest a sell (bearish) signal.<br><br>'
    '<span style="color:red;"><b>INTERPRETATION:</b></span><br> On the chart below, the MACD indicator is not transmitting a trade signal, but in the next period there is a chance <br> that the two lines will intersect, most likely generating a buy signal.',

    '<span style="color:blue; font-weight:bold;">INFO:</span><br> The RSI (Relative Strength Index) provides a trading signal when it reaches or exceeds the overbought level (usually the <br> 70 level), indicating a possible trend reversal.<br><br>'
    'Likewise, when the RSI reaches or falls below the oversold level (usually the 30 level), it can also suggest a potential trend <br> reversal.<br><br>'
    '<span style="color:red; font-weight:bold;">INTERPRETATION:</span><br> In this case, the indicator is suggesting that there is a possibility that the price may rise, with the RSI line being in an <br> oversold area.',

    '<span style="color:blue; font-weight:bold;">INFO:</span><br> VWAP (Volume Weighted Average Price) provides trading signals when the current price of an asset exceeds or falls <br> below the VWAP level, indicating possible changes in the balance between buyers and sellers and providing clues as to the <br> future direction of prices.<br><br>'
    '<span style="color:red; font-weight:bold;">INTERPRETATION:</span><br> Thus, on the chart below we find a signal that the price is likely to rise, so it may be a good time to <br> buy.',

    '<span style="color:blue; font-weight:bold;">INFO:</span><br> The EMA (Exponential Moving Average) provides trading signals when the asset price moves above or below the EMA <br> line, indicating possible changes in the price trend and providing clues as to the future direction of the market.<br><br>'
    '<span style="color:red; font-weight:bold;">INTERPRETATION:</span><br> On the chart below we don\'t yet have a trade signal according to.',


    '<span style="color:blue; font-weight:bold;">INFO:</span><br> AROON provides trading signals by identifying the strength and direction of a price trend.<br><br> When Aroon Up (which measures the time since the last high) intersects Aroon Down (which measures the time since the <br> last low) from bottom to top, this indicates a possible start of an uptrend.'
    'Conversely, when Aroon Down crosses Aroon Up <br> from bottom to top, a downtrend can be anticipated.<br><br>'
    '<span style="color:red; font-weight:bold;">INTERPRETATION:</span><br> In the example below, the AROON indicator has not yet generated a market entry signal, but we can <br> expect this in the fairly near future.',


    '<span style="color:blue; font-weight:bold;">INFO:</span><br> Bollinger Bands provide trading signals when the price reaches or approaches the upper or lower band.<br><br>'
    'A touch of the upper band may suggest that the price is overbought and a correction could follow, while a touch of the lower <br> band may indicate overselling and possible price upside.<br><br>'
    '<span style="color:red; font-weight:bold;">INTERPRETATION:</span><br> From the chart below we can read a buy signal as the candles touch the lower band of the indicator.',


    '<span style="color:blue; font-weight:bold;">INFO:</span><br> Rate of Change (ROC) provides trading signals when the indicator goes above or below its reference level, such as <br> zero.<br><br>'
    'A large positive ROC value may indicate accelerating price increases, suggesting a possible uptrend, while a large negative <br> value may indicate accelerating declines, signalling a possible downtrend.<br><br>'
    '<span style="color:red; font-weight:bold;">INTERPRETATION:</span><br> The ROC indicator values in the example below do not yet suggest a change in trend, but we can <br> expect one if we use several indicators simultaneously in our analysis.',


    '<span style="color:blue; font-weight:bold;">INFO:</span><br> The SAR (Stop and Reverse) indicator gives a trading signal when the price crosses its line.'
    'If the price crosses above <br> the line, the indicator may suggest a possible start of an uptrend, and if the price crosses below the SAR line, this may <br> indicate a possible start of a downtrend in price.<br><br>'
    '<span style="color:red; font-weight:bold;">INTERPRETATION:</span><br> According to the chart below, we can expect an increase in price, with the last candle that forms <br> remaining to confirm whether it is indeed a good time to buy.'
        ]




        # Lista cu etichetele butoanelor pentru fiecare exemplu
        action_labels = ["Show MACD on graphic", "Show RSI on graphic", "Show VWAP on graphic", "Show EMA on graphic", "Show Aroon on graphic", "Show B.B. on graphic", "Show ROC on graphic", "Show SAR on graphic"]

        for i, example_text in enumerate(example_texts):
            example_frame = QFrame()
            example_frame.setFrameShape(QFrame.Box)
            example_layout = QVBoxLayout()

            # Modifică dimensiunea textului
            example_label = QLabel(example_text)
            font = QFont()
            font.setPointSize(12)  # Modificați dimensiunea textului aici
            example_label.setFont(font)
            example_layout.addWidget(example_label)

            # Adăugați un buton cu eticheta corespunzătoare din lista action_labels
            action_name = action_labels[i] if i < len(action_labels) else "Not Defined"
            action_button = QPushButton(action_name)
            action_button.setStyleSheet("font-weight: bold;")  # Folosește CSS pentru a face textul bold
            action_button.clicked.connect(lambda _, action=action_name: self.execute_action(action))
            action_button.setFixedSize(160, 30)  # Dimensiunea butonului

            example_layout.addWidget(action_button)
            example_frame.setLayout(example_layout)
            scroll_layout.addWidget(example_frame)  # Add the frame to the scroll layout

class ExampleTextWindow(QDialog):
    def __init__(self, example_text):
        super().__init__()

        self.setWindowTitle("Exemplu de Text")
        layout = QVBoxLayout(self)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(example_text)

        layout.addWidget(text_edit)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    tab = LearningTab()
    tab.show()
    sys.exit(app.exec_())


