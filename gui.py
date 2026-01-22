"""
PyQt5 GUI for NLP Comment Processing
Provides a user-friendly interface for processing JSON files with user comments.
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QFileDialog, QMessageBox, QTextEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from nlp import NLPProcessor


class ProcessingThread(QThread):
    """Thread for processing comments without blocking the UI."""
    
    progress_updated = pyqtSignal(int, int)  # current, total
    processing_complete = pyqtSignal(dict)  # statistics
    processing_error = pyqtSignal(str)  # error message
    
    def __init__(self, input_path, output_path):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.processor = NLPProcessor()
    
    def run(self):
        """Run the processing in a separate thread."""
        try:
            def progress_callback(current, total):
                self.progress_updated.emit(current, total)
            
            stats = self.processor.process_file(
                self.input_path,
                self.output_path,
                progress_callback=progress_callback
            )
            self.processing_complete.emit(stats)
        except Exception as e:
            self.processing_error.emit(str(e))


class NLPProcessorGUI(QMainWindow):
    """Main GUI window for NLP Comment Processor."""
    
    def __init__(self):
        super().__init__()
        self.input_file_path = None
        self.output_file_path = None
        self.processing_thread = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('NLP Comment Processor')
        self.setGeometry(100, 100, 700, 500)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title_label = QLabel('NLP Comment Processor')
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Description
        description = QLabel(
            'Process JSON files containing user comments with sentiment analysis.\n'
            'Select an input file, choose an output location, and click Process.'
        )
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        main_layout.addWidget(description)
        
        main_layout.addSpacing(20)
        
        # Input file selection
        input_layout = QHBoxLayout()
        input_label = QLabel('Input File:')
        input_label.setMinimumWidth(100)
        input_layout.addWidget(input_label)
        
        self.input_file_label = QLabel('No file selected')
        self.input_file_label.setStyleSheet('padding: 5px; background-color: #f0f0f0; border: 1px solid #ccc;')
        input_layout.addWidget(self.input_file_label, 1)
        
        self.select_input_btn = QPushButton('Browse...')
        self.select_input_btn.clicked.connect(self.select_input_file)
        input_layout.addWidget(self.select_input_btn)
        
        main_layout.addLayout(input_layout)
        
        # Output file selection
        output_layout = QHBoxLayout()
        output_label = QLabel('Output File:')
        output_label.setMinimumWidth(100)
        output_layout.addWidget(output_label)
        
        self.output_file_label = QLabel('No file selected')
        self.output_file_label.setStyleSheet('padding: 5px; background-color: #f0f0f0; border: 1px solid #ccc;')
        output_layout.addWidget(self.output_file_label, 1)
        
        self.select_output_btn = QPushButton('Browse...')
        self.select_output_btn.clicked.connect(self.select_output_file)
        output_layout.addWidget(self.select_output_btn)
        
        main_layout.addLayout(output_layout)
        
        main_layout.addSpacing(20)
        
        # Progress bar
        progress_layout = QVBoxLayout()
        self.progress_label = QLabel('Ready to process')
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        main_layout.addLayout(progress_layout)
        
        main_layout.addSpacing(10)
        
        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(150)
        self.results_text.setPlaceholderText('Processing results will appear here...')
        main_layout.addWidget(self.results_text)
        
        # Process button
        self.process_btn = QPushButton('Process Comments')
        self.process_btn.setMinimumHeight(40)
        self.process_btn.setStyleSheet(
            'QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }'
            'QPushButton:hover { background-color: #45a049; }'
            'QPushButton:disabled { background-color: #cccccc; }'
        )
        self.process_btn.clicked.connect(self.process_comments)
        self.process_btn.setEnabled(False)
        main_layout.addWidget(self.process_btn)
        
        # Status bar
        self.statusBar().showMessage('Ready')
    
    def select_input_file(self):
        """Open file dialog to select input JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select Input JSON File',
            '',
            'JSON Files (*.json);;All Files (*)'
        )
        
        if file_path:
            # Validate it's a JSON file
            if not file_path.lower().endswith('.json'):
                QMessageBox.warning(
                    self,
                    'Invalid File Type',
                    'Please select a JSON file (.json)'
                )
                return
            
            self.input_file_path = file_path
            # Show just the filename if path is too long
            display_name = os.path.basename(file_path)
            if len(file_path) > 50:
                self.input_file_label.setText(f'...{display_name}')
                self.input_file_label.setToolTip(file_path)
            else:
                self.input_file_label.setText(file_path)
                self.input_file_label.setToolTip(file_path)
            
            self.check_ready_to_process()
            self.statusBar().showMessage(f'Input file selected: {display_name}')
    
    def select_output_file(self):
        """Open file dialog to select output JSON file location."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'Select Output JSON File',
            'processed_comments.json',
            'JSON Files (*.json);;All Files (*)'
        )
        
        if file_path:
            # Ensure .json extension
            if not file_path.lower().endswith('.json'):
                file_path += '.json'
            
            self.output_file_path = file_path
            # Show just the filename if path is too long
            display_name = os.path.basename(file_path)
            if len(file_path) > 50:
                self.output_file_label.setText(f'...{display_name}')
                self.output_file_label.setToolTip(file_path)
            else:
                self.output_file_label.setText(file_path)
                self.output_file_label.setToolTip(file_path)
            
            self.check_ready_to_process()
            self.statusBar().showMessage(f'Output file location set: {display_name}')
    
    def check_ready_to_process(self):
        """Enable process button if both files are selected."""
        if self.input_file_path and self.output_file_path:
            self.process_btn.setEnabled(True)
        else:
            self.process_btn.setEnabled(False)
    
    def process_comments(self):
        """Start processing the comments."""
        if not self.input_file_path or not self.output_file_path:
            QMessageBox.warning(
                self,
                'Missing Files',
                'Please select both input and output files.'
            )
            return
        
        # Disable controls during processing
        self.select_input_btn.setEnabled(False)
        self.select_output_btn.setEnabled(False)
        self.process_btn.setEnabled(False)
        
        # Reset progress
        self.progress_bar.setValue(0)
        self.progress_label.setText('Processing...')
        self.results_text.clear()
        self.statusBar().showMessage('Processing comments...')
        
        # Create and start processing thread
        self.processing_thread = ProcessingThread(
            self.input_file_path,
            self.output_file_path
        )
        self.processing_thread.progress_updated.connect(self.update_progress)
        self.processing_thread.processing_complete.connect(self.processing_finished)
        self.processing_thread.processing_error.connect(self.processing_failed)
        self.processing_thread.start()
    
    def update_progress(self, current, total):
        """Update the progress bar."""
        percentage = int((current / total) * 100)
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(f'Processing: {current}/{total} comments')
    
    def processing_finished(self, stats):
        """Handle successful processing completion."""
        # Update UI
        self.progress_bar.setValue(100)
        self.progress_label.setText('Processing complete!')
        
        # Display results
        results_text = "Processing Complete!\n\n"
        results_text += f"Total Comments: {stats['total_comments']}\n"
        results_text += f"Successfully Processed: {stats['successful']}\n"
        results_text += f"Errors: {stats['errors']}\n\n"
        results_text += "Sentiment Distribution:\n"
        results_text += f"  Positive: {stats['sentiment_distribution']['positive']}\n"
        results_text += f"  Negative: {stats['sentiment_distribution']['negative']}\n"
        results_text += f"  Neutral: {stats['sentiment_distribution']['neutral']}\n\n"
        results_text += f"Results saved to:\n{self.output_file_path}"
        
        self.results_text.setPlainText(results_text)
        
        # Show success message
        QMessageBox.information(
            self,
            'Success',
            f'Processing complete!\n\n'
            f'Processed {stats["successful"]} comments.\n'
            f'Results saved to:\n{os.path.basename(self.output_file_path)}'
        )
        
        self.statusBar().showMessage('Processing complete!')
        
        # Re-enable controls
        self.select_input_btn.setEnabled(True)
        self.select_output_btn.setEnabled(True)
        self.process_btn.setEnabled(True)
    
    def processing_failed(self, error_message):
        """Handle processing errors."""
        # Update UI
        self.progress_bar.setValue(0)
        self.progress_label.setText('Processing failed')
        self.results_text.setPlainText(f'Error: {error_message}')
        
        # Show error message
        QMessageBox.critical(
            self,
            'Processing Error',
            f'An error occurred during processing:\n\n{error_message}'
        )
        
        self.statusBar().showMessage('Processing failed')
        
        # Re-enable controls
        self.select_input_btn.setEnabled(True)
        self.select_output_btn.setEnabled(True)
        self.process_btn.setEnabled(True)


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for better cross-platform appearance
    
    window = NLPProcessorGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
