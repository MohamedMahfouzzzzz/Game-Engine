# /**************************************************************************/
# /*  node_documentation_dialog.py                                          */
# /**************************************************************************/
# /*                         This file is part of:                          */
# /*                             GAME ENGINE                                */
# /**************************************************************************/

"""Dialog for displaying node type documentation."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QListWidget, QListWidgetItem, QTabWidget, QWidget,
    QPushButton, QSplitter, QTreeWidget, QTreeWidgetItem,
    QMessageBox
)

from docs.node_types import NodeTypeDoc


class NodeDocumentationDialog(QDialog):
    """Dialog showing comprehensive documentation for a node type."""
    
    def __init__(self, node_doc: NodeTypeDoc, parent=None):
        super().__init__(parent)
        self.node_doc = node_doc
        self.setWindowTitle(f"📖 {node_doc.icon} {node_doc.type_name} Documentation")
        self.setMinimumSize(700, 500)
        self._build_ui()
    
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel(f"<h1>{self.node_doc.icon} {self.node_doc.type_name}</h1>")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Brief description
        brief = QLabel(f"<b>{self.node_doc.brief}</b>")
        brief.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(brief)
        
        layout.addSpacing(10)
        
        # Tabs for different sections
        tabs = QTabWidget()
        
        # Description tab
        desc_tab = self._create_description_tab()
        tabs.addTab(desc_tab, "📝 Description")
        
        # Properties tab
        props_tab = self._create_properties_tab()
        tabs.addTab(props_tab, "⚙️ Properties")
        
        # Methods tab
        methods_tab = self._create_methods_tab()
        tabs.addTab(methods_tab, "🔧 Methods")
        
        # Examples tab
        examples_tab = self._create_examples_tab()
        tabs.addTab(examples_tab, "💡 Examples")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("❌ Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def _create_description_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Full description
        desc = QTextEdit()
        desc.setReadOnly(True)
        desc.setPlainText(self.node_doc.description)
        layout.addWidget(desc)
        
        # Use cases
        if self.node_doc.use_cases:
            layout.addWidget(QLabel("<b>💡 Best Used For:</b>"))
            cases_text = "\n".join(f"• {case}" for case in self.node_doc.use_cases)
            cases = QTextEdit()
            cases.setReadOnly(True)
            cases.setPlainText(cases_text)
            layout.addWidget(cases)
        
        return widget
    
    def _create_properties_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        tree = QTreeWidget()
        tree.setHeaderLabels(["Property", "Type", "Default", "Description"])
        tree.setColumnWidth(0, 150)
        tree.setColumnWidth(1, 100)
        tree.setColumnWidth(2, 100)
        
        for prop in self.node_doc.properties:
            item = QTreeWidgetItem()
            item.setText(0, prop.name)
            item.setText(1, prop.type_name)
            item.setText(2, str(prop.default_value))
            item.setText(3, prop.description)
            tree.addTopLevelItem(item)
        
        layout.addWidget(tree)
        return widget
    
    def _create_methods_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        tree = QTreeWidget()
        tree.setHeaderLabels(["Method", "Signature", "Description"])
        tree.setColumnWidth(0, 200)
        tree.setColumnWidth(1, 250)
        
        for method in self.node_doc.methods:
            item = QTreeWidgetItem()
            item.setText(0, method.name)
            item.setText(1, method.signature)
            item.setText(2, method.description)
            tree.addTopLevelItem(item)
        
        layout.addWidget(tree)
        
        # Signals
        if self.node_doc.signals:
            layout.addWidget(QLabel("<b>📡 Signals:</b>"))
            signals_list = QListWidget()
            for signal in self.node_doc.signals:
                signals_list.addItem(signal)
            layout.addWidget(signals_list)
        
        return widget
    
    def _create_examples_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Example code
        if self.node_doc.example_code:
            layout.addWidget(QLabel("<b>💡 Example Code:</b>"))
            code = QTextEdit()
            code.setReadOnly(True)
            code.setPlainText(self.node_doc.example_code)
            code.setStyleSheet("background-color: #2a2a2a; color: #ffffff; font-family: monospace;")
            layout.addWidget(code)
        
        return widget
