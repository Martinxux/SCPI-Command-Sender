"""连接功能相关方法"""

class ConnectionFunctions:
    """连接功能类"""
    
    def is_connected(self):
        """检查是否真正连接到上位机"""
        if not self.instrument:
            return False
        # 使用instrument自身的is_connected方法来检查连接状态，该方法会同时处理TCP/IP和VISA连接
        return self.instrument.is_connected()
    
    def set_connection_ui(self, connected):
        """设置连接状态UI"""
        if connected:
            self._update_connection_status("🟢 已连接", "#e8f5e9", "#2e7d32", True)
        else:
            self._update_connection_status("🔴 未连接", "#ffebee", "#c62828", False)
    
    def _update_connection_status(self, text, bg_color, text_color, enable_execute):
        """统一更新连接状态UI"""
        self.connection_status.setText(text)
        self.connection_status.setStyleSheet(
            f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
            }}
        """
        )
        self.execute_btn.setEnabled(enable_execute)
    
    def toggle_connection(self):
        """切换连接状态"""
        if self.is_connected():
            self.disconnect_instrument()
        else:
            self.show_connection_dialog()
    
    def disconnect_instrument(self):
        """断开仪器连接"""
        if not self.is_connected():
            return
        
        try:
            self.instrument.disconnect()
            self.set_connection_ui(False)
            self.instrument_info.setText("未连接")
            self.update_connection_menu(False)
            self.append_output("已断开与仪器的连接")
            self.instrument = None
        except Exception as e:
            self.append_output(f"断开连接失败: {str(e)}", "ERROR")
    
    def update_connection_menu(self, connected):
        """更新连接菜单状态"""
        if connected:
            self.connect_action.setText("断开连接")
        else:
            self.connect_action.setText("连接配置")