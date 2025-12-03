# app/ui/views/history.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                               QLabel, QHeaderView, QPushButton, QHBoxLayout, QMessageBox)
from app.db.database import DatabaseManager

class HistoryView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # 头部
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("📊 历史运行数据记录"))
        
        btn_export = QPushButton("📥 导出 CSV")
        btn_export.setStyleSheet("background-color: #2e7d32; color: white; padding: 8px 15px; border-radius: 4px;")
        btn_export.clicked.connect(self.export_data)
        header_layout.addStretch()
        header_layout.addWidget(btn_export)
        
        layout.addLayout(header_layout)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["时间", "水深(m)", "流速(m/s)", "流量(m³/s)", "Fr数", "流态"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("QHeaderView::section { background-color: #333; color: white; }")
        layout.addWidget(self.table)
        
        self.db = DatabaseManager()
        self.load_data()

    def load_data(self):
        rows = self.db.get_history(100)
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            # 数据库列: id, time, depth, vel, q, fr, state, float
            self.table.setItem(i, 0, QTableWidgetItem(str(row[1])))
            self.table.setItem(i, 1, QTableWidgetItem(f"{row[2]:.2f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{row[3]:.2f}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{row[4]:.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{row[5]:.2f}"))
            self.table.setItem(i, 5, QTableWidgetItem(str(row[6])))

    def export_data(self):
        path = self.db.export_to_csv()
        QMessageBox.information(self, "导出成功", f"数据已保存至:\n{path}")