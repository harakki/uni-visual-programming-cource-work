import os
import sys
import json
from PyQt6.QtWidgets import (QApplication, QWidget, QMainWindow, QVBoxLayout, QTextEdit,
                             QTreeView, QToolBar, QTabWidget, QSplitter, QFileDialog, QLabel, QDialog, QMessageBox)
from PyQt6.QtCore import (Qt, QDir, QEvent, QSettings)
from PyQt6.QtGui import (QFileSystemModel, QTextCursor, QAction, QIcon)


class PlantCareEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.window_width, self.window_height = 800, 600
        self.setMinimumSize(self.window_width, self.window_height)
        self.setWindowTitle('Справочник по уходу за растениями')
        self.setStyleSheet('''QWidget { font-size: 16px; }''')

        self.current_directory = QDir.currentPath()
        self.init_ui()

    def init_ui(self):
        # Создание меню
        self.create_menus()

        # Главный виджет и макет
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.main_layout = QVBoxLayout(self.main_widget)

        # Разделитель для боковой панели и основного контента
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)

        # Боковая панель файловой системы
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(self.current_directory)
        self.file_model.setFilter(
            QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)

        self.file_view = QTreeView()
        self.file_view.setModel(self.file_model)
        self.file_view.setRootIndex(
            self.file_model.index(self.current_directory))
        self.file_view.setColumnHidden(1, True)
        self.file_view.setColumnHidden(2, True)
        self.file_view.setColumnHidden(3, True)
        self.file_view.setHeaderHidden(True)
        self.file_view.setMaximumWidth(self.window_width // 4)
        self.file_view.clicked.connect(self.open_file)
        self.splitter.addWidget(self.file_view)

        # Контейнер для вкладок и редактора с превью
        self.content_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.content_splitter)

        # Вкладки редакторов
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.currentChanged.connect(
            self.update_preview_on_tab_change)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.tabBar().setMouseTracking(True)
        self.tab_widget.tabBar().installEventFilter(self)
        self.content_splitter.addWidget(self.tab_widget)

        # Превью
        self.preview_widget = QTextEdit(readOnly=True)
        self.content_splitter.addWidget(self.preview_widget)

        # Информационный текст, если все панели скрыты
        self.info_label = QLabel(
            "Все панели скрыты. Используйте меню 'Вид', чтобы их вернуть.", self)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("font-size: 16px; color: gray;")
        self.info_label.hide()
        self.main_layout.addWidget(self.info_label)

        self.restore_application_state()

        # Создание тулбара
        self.toolbar = QToolBar("Стиль")
        self.addToolBar(self.toolbar)
        self.add_toolbar_actions()

        # Drag and Drop для открытия файлов/директорий
        self.setAcceptDrops(True)

        self.create_new_tab()

    def create_menus(self):
        # Создание меню
        menu_bar = self.menuBar()

        # Меню "Файл"
        file_menu = menu_bar.addMenu("Файл")

        new_action = QAction("Создать файл", self)
        new_action.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentNew))
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.create_new_tab)
        file_menu.addAction(new_action)

        template_action = QAction("Создать из шаблона...", self)
        template_action.setIcon(QIcon.fromTheme(
            QIcon.ThemeIcon.DocumentPageSetup))
        template_action.setShortcut("Alt+N")
        template_action.triggered.connect(self.select_template)
        file_menu.addAction(template_action)

        file_menu.addSeparator()

        open_project_action = QAction("Открыть проект...", self)
        open_project_action.setIcon(
            QIcon.fromTheme(QIcon.ThemeIcon.FolderOpen))
        open_project_action.triggered.connect(self.change_working_directory)
        file_menu.addAction(open_project_action)

        open_action = QAction("Открыть файл...", self)
        open_action.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen))
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("Сохранить", self)
        save_action.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave))
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Сохранить как...", self)
        save_as_action.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSaveAs))
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        export_action = QAction("Экспорт в HTML...", self)
        export_action.triggered.connect(self.export_to_html)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("Выход", self)
        exit_action.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.WindowClose))
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню "Правка"
        edit_menu = menu_bar.addMenu("Правка")

        cut_action = QAction("Вырезать", self)
        cut_action.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditCut))
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut_text)
        edit_menu.addAction(cut_action)

        copy_action = QAction("Копировать", self)
        copy_action.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditCopy))
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy_text)
        edit_menu.addAction(copy_action)

        paste_action = QAction("Вставить", self)
        paste_action.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditPaste))
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste_text)
        edit_menu.addAction(paste_action)

        # Меню "Вид"
        view_menu = menu_bar.addMenu("Вид")

        toggle_preview_action = QAction("Скрыть превью", self)
        toggle_preview_action.triggered.connect(self.toggle_preview_visibility)
        view_menu.addAction(toggle_preview_action)

        toggle_editor_action = QAction("Скрыть редактор", self)
        toggle_editor_action.triggered.connect(self.toggle_editor_visibility)
        view_menu.addAction(toggle_editor_action)

        # Меню "Справка"
        help_menu = menu_bar.addMenu("Справка")

        about_action = QAction("О программе", self)
        about_action.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.HelpAbout))
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def add_toolbar_actions(self):
        # **Жирный**
        bold_action = QAction("Жирный", self)
        bold_action.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.FormatTextBold))
        bold_action.triggered.connect(lambda: self.toggle_format_text("**"))
        self.toolbar.addAction(bold_action)

        # *Курсивный*
        italic_action = QAction("Курсив", self)
        italic_action.setIcon(QIcon.fromTheme(
            QIcon.ThemeIcon.FormatTextItalic))
        italic_action.triggered.connect(lambda: self.toggle_format_text("*"))
        self.toolbar.addAction(italic_action)

        # _Подчеркнутый_
        emphasized_action = QAction("Подчеркнутый", self)
        emphasized_action.setIcon(QIcon.fromTheme(
            QIcon.ThemeIcon.FormatTextUnderline))
        emphasized_action.triggered.connect(
            lambda: self.toggle_format_text("_"))
        self.toolbar.addAction(emphasized_action)

        # ~~Зачеркнутый~~
        crossed_out_action = QAction("Зачеркнутый", self)
        crossed_out_action.setIcon(QIcon.fromTheme(
            QIcon.ThemeIcon.FormatTextStrikethrough))
        crossed_out_action.triggered.connect(
            lambda: self.toggle_format_text("~~"))
        self.toolbar.addAction(crossed_out_action)

        # > Цитата
        quote_action = QAction("Цитата", self)
        quote_action.triggered.connect(self.insert_quote)
        self.toolbar.addAction(quote_action)

        # [Изображение]()
        image_action = QAction("Изображение", self)
        image_action.triggered.connect(self.insert_image)
        self.toolbar.addAction(image_action)

        # # Заголовки
        h1_action = QAction("H1", self)
        h1_action.triggered.connect(lambda: self.insert_header("# "))
        self.toolbar.addAction(h1_action)

        h2_action = QAction("H2", self)
        h2_action.triggered.connect(lambda: self.insert_header("## "))
        self.toolbar.addAction(h2_action)

        h3_action = QAction("H3", self)
        h3_action.triggered.connect(lambda: self.insert_header("### "))
        self.toolbar.addAction(h3_action)

        h4_action = QAction("H4", self)
        h4_action.triggered.connect(lambda: self.insert_header("#### "))
        self.toolbar.addAction(h4_action)

        h5_action = QAction("H5", self)
        h5_action.triggered.connect(lambda: self.insert_header("##### "))
        self.toolbar.addAction(h5_action)

        h6_action = QAction("H6", self)
        h6_action.triggered.connect(lambda: self.insert_header("###### "))
        self.toolbar.addAction(h6_action)

    def create_new_tab(self, template=""):
        editor = QTextEdit()
        editor.setAcceptRichText(False)
        editor.setPlaceholderText(
            "Начните писать или выберите шаблон для нового документа")
        editor.textChanged.connect(lambda: self.update_preview(editor))

        self.tab_widget.addTab(editor, "Новый файл")
        self.tab_widget.setCurrentWidget(editor)

        if template:
            editor.setPlainText(template)

        editor.setFocus()

    def save_file(self):
        current_editor = self.get_current_editor()
        if current_editor:
            file_path = self.tab_widget.tabToolTip(
                self.tab_widget.currentIndex())
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(current_editor.toPlainText())
                    self.current_directory = os.path.dirname(file_path)
                except Exception as e:
                    QMessageBox.critical(
                        self, "Ошибка", f"Ошибка при сохранении файла: {e}")
            else:
                self.save_file_as()

    def save_file_as(self):
        current_editor = self.get_current_editor()
        if current_editor:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить файл как", self.current_directory, "Markdown Files (*.md)")
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(current_editor.toPlainText())
                    self.tab_widget.setTabText(
                        self.tab_widget.currentIndex(), os.path.basename(file_path))
                    self.current_directory = os.path.dirname(file_path)
                    self.tab_widget.setTabToolTip(
                        self.tab_widget.currentIndex(), file_path)
                except Exception as e:
                    QMessageBox.critical(
                        self, "Ошибка", f"Ошибка при сохранении файла: {e}")

    def select_template(self):
        templates_dir = os.path.join(self.current_directory, "templates")
        if os.path.exists(templates_dir) and os.path.isdir(templates_dir):
            templates = [f for f in os.listdir(
                templates_dir) if f.endswith(".md")]

            if templates:
                template, _ = QFileDialog.getOpenFileName(
                    self, "Выберите шаблон", templates_dir, "Markdown Files (*.md)")
                if template:
                    with open(template, 'r', encoding='utf-8') as file:
                        content = file.read()
                        self.create_new_tab(content)
            else:
                QMessageBox.warning(
                    self, "Ошибка", "В директории нет доступных шаблонов.")
        else:
            QMessageBox.warning(
                self, "Ошибка", "Директория с шаблонами не найдена.")

    def close_tab(self, index):
        self.tab_widget.removeTab(index)

    def update_preview(self, editor):
        if editor:
            self.preview_widget.setMarkdown(editor.toPlainText())

    def update_preview_on_tab_change(self, index):
        editor = self.get_current_editor()
        if editor:
            self.preview_widget.setMarkdown(editor.toPlainText())

    def open_file(self, index):
        file_path = self.file_model.filePath(index)

        for i in range(self.tab_widget.count()):
            tab_text = self.tab_widget.tabText(i)
            if tab_text == os.path.basename(file_path):
                self.tab_widget.setCurrentIndex(i)
                return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.create_new_tab()
                current_editor = self.get_current_editor()
                current_editor.setPlainText(content)
                self.tab_widget.setTabText(
                    self.tab_widget.currentIndex(), os.path.basename(file_path))
                self.tab_widget.setTabToolTip(
                    self.tab_widget.currentIndex(), file_path)
        except Exception as e:
            print(f"Ошибка при открытии файла: {e}")

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл", self.current_directory, "Markdown Files (*.md)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.create_new_tab(content)
                    self.tab_widget.setTabText(
                        self.tab_widget.currentIndex(), os.path.basename(file_path))
                    self.tab_widget.setTabToolTip(
                        self.tab_widget.currentIndex(), file_path)
            except Exception as e:
                print(f"Ошибка при открытии файла: {e}")

    def export_to_html(self):
        current_editor = self.get_current_editor()

        if current_editor:
            html_path, _ = QFileDialog.getSaveFileName(
                self, "Экспортировать в HTML", self.current_directory, "HTML Files (*.html)")
            if html_path:
                try:
                    with open(html_path, 'w', encoding='utf-8') as file:
                        file.write(current_editor.toHtml())
                    self.current_directory = os.path.dirname(html_path)
                except Exception as e:
                    QMessageBox.critical(
                        self, "Ошибка", f"Ошибка при экспорте файла: {e}")

    def get_current_editor(self):
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, QTextEdit):
            return current_widget

    def toggle_format_text(self, wrapper):
        editor = self.get_current_editor()
        if editor:
            cursor = editor.textCursor()
            if cursor.hasSelection():
                selected_text = cursor.selectedText()
                cursor.insertText(f"{wrapper}{selected_text}{wrapper}")
            else:
                cursor.movePosition(QTextCursor.MoveOperation.StartOfWord)
                cursor.insertText(wrapper)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfWord)
                cursor.insertText(wrapper)

    def insert_quote(self):
        editor = self.get_current_editor()
        if editor:
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            current_line = cursor.block().text()
            if current_line.startswith('> '):
                cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                cursor.insertText(current_line[len('> '):])
            else:
                cursor.insertText('> ')

    def insert_header(self, header):
        editor = self.get_current_editor()
        if editor:
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            current_line = cursor.block().text().strip()

            if not current_line.strip():
                cursor.insertText(header)
                return

            if current_line.startswith(header):
                cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                # Удаляем только заголовок, оставляя остальной текст
                cursor.insertText(current_line[len(header):])
            else:
                # Удаляем существующий заголовок, если он есть, и добавляем новый
                for level in ["# ", "## ", "### ", "#### ", "##### ", "###### "]:
                    if current_line.startswith(level):
                        cursor.select(
                            QTextCursor.SelectionType.BlockUnderCursor)
                        cursor.insertText(current_line[len(level):])
                        break

                # Перемещаем курсор в начало строки перед вставкой
                cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                cursor.insertText(header)

    def insert_image(self):
        image_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", self.current_directory, "Images (*.png *.jpg *.jpeg *.gif *.bmp)")
        if image_path:
            relative_path = os.path.relpath(image_path, self.current_directory)

            if '..' in relative_path.split(os.sep):
                QMessageBox.warning(
                    self, "Предупреждение", "Файл не включен в проект. При перемещении проекта изображение не будет отрисовано.")

            markdown_image_tag = f"![Изображение](<{relative_path}>)\n"
            editor = self.get_current_editor()
            if editor:
                cursor = editor.textCursor()
                cursor.insertText(markdown_image_tag)

    def toggle_editor_visibility(self):
        is_visible = self.tab_widget.isVisible()
        self.tab_widget.setVisible(not is_visible)
        action = self.sender()
        action.setText(
            "Скрыть редактор" if not is_visible else "Показать редактор")
        self.update_info_label_visibility()

    def toggle_preview_visibility(self):
        is_visible = self.preview_widget.isVisible()
        self.preview_widget.setVisible(not is_visible)
        action = self.sender()
        action.setText(
            "Скрыть превью" if not is_visible else "Показать превью")
        self.update_info_label_visibility()

    def change_working_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Выбрать папку проекта", self.current_directory)
        if directory:
            self.current_directory = directory
            self.file_model.setRootPath(directory)
            self.file_view.setRootIndex(self.file_model.index(directory))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if QDir(file_path).exists():
                reply = QMessageBox.question(
                    self, "Смена директории", "Вы действительно хотите сменить рабочую директорию?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.file_model.setRootPath(file_path)
                    self.file_view.setRootIndex(
                        self.file_model.index(file_path))
                    self.current_directory = file_path
            else:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        self.create_new_tab()
                        current_editor = self.get_current_editor()
                        current_editor.setPlainText(content)
                        self.tab_widget.setTabText(
                            self.tab_widget.currentIndex(), os.path.basename(file_path))
                except Exception as e:
                    print(
                        f"Ошибка при открытии файла через drag and drop: {e}")

    def eventFilter(self, source, event):
        if source == self.tab_widget.tabBar() and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.MiddleButton:
                index = self.tab_widget.tabBar().tabAt(event.pos())
                if index >= 0:
                    self.close_tab(index)
                return True
        return super().eventFilter(source, event)

    def show_about_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("О программе")

        # Содержимое диалога
        label = QLabel(
            "Редактор и просмотрщик справочника по уходу за домашними растениями.\n\nАвтор:\nШипилов Дементий ИП-215", dialog)

        layout = QVBoxLayout(dialog)
        layout.addWidget(label)

        # Отображаем диалог
        dialog.exec()

    def cut_text(self):
        editor = self.get_current_editor()
        if editor:
            editor.cut()

    def copy_text(self):
        editor = self.get_current_editor()
        if editor:
            editor.copy()

    def paste_text(self):
        editor = self.get_current_editor()
        if editor:
            editor.paste()

    def close_tab(self, index):
        editor = self.tab_widget.widget(index)
        if isinstance(editor, QTextEdit):
            file_path = self.tab_widget.tabToolTip(index)
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content_on_disk = f.read()
                        if editor.toPlainText() != content_on_disk:

                            reply = QMessageBox.question(self, 'Несохраненные изменения',
                                                         f"В файле '{os.path.basename(file_path)}' имеются несохраненные изменения. Сохранить?",
                                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)

                            if reply == QMessageBox.StandardButton.Yes:
                                self.save_file_by_path(
                                    file_path, editor.toPlainText())
                                self.tab_widget.removeTab(index)
                            elif reply == QMessageBox.StandardButton.No:
                                self.tab_widget.removeTab(index)
                            else:
                                return

                except FileNotFoundError:
                    # Обработка случая, когда файл был удален вне приложения
                    reply = QMessageBox.question(self, 'Файл не найден',
                                                 f"Файл '{os.path.basename(file_path)}' не найден. Сохранить как?",
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
                    if reply == QMessageBox.StandardButton.Yes:
                        self.save_file_as()
                    elif reply == QMessageBox.StandardButton.No:
                        self.tab_widget.removeTab(index)
                    else:
                        return

            elif editor.toPlainText().strip():  # Если файл не существует, но есть текст
                reply = QMessageBox.question(self, 'Несохраненные изменения',
                                             "Имеются несохраненные изменения. Сохранить?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)

                if reply == QMessageBox.StandardButton.Yes:
                    self.save_file_as()
                elif reply == QMessageBox.StandardButton.No:
                    self.tab_widget.removeTab(index)
                else:
                    return  # отмена закрытия вкладки

        # Если файл не был изменен или вкладка пустая
        self.tab_widget.removeTab(index)

    def closeEvent(self, event):
        self.save_application_state()

        unsaved_changes = False
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if isinstance(editor, QTextEdit):
                file_path = self.tab_widget.tabToolTip(i)
                if file_path:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content_on_disk = f.read()
                            if editor.toPlainText() != content_on_disk:
                                unsaved_changes = True
                                break
                    except FileNotFoundError:
                        unsaved_changes = True
                        break
                elif editor.toPlainText().strip():
                    unsaved_changes = True
                    break

        if unsaved_changes:
            reply = QMessageBox.question(self, 'Несохраненные изменения',
                                         "Имеются несохраненные изменения. Сохранить?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Yes:
                for i in range(self.tab_widget.count()):
                    editor = self.tab_widget.widget(i)
                    if isinstance(editor, QTextEdit):
                        file_path = self.tab_widget.tabToolTip(i)
                        if file_path:
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content_on_disk = f.read()
                                    if editor.toPlainText() != content_on_disk:
                                        self.save_file_by_path(
                                            file_path, editor.toPlainText())
                            except FileNotFoundError:
                                # Если файл был удален - предлагаем сохранить как...
                                self.save_file_as()
                        elif editor.toPlainText().strip():  # Если файла не было, сохраняем как...
                            self.save_file_as()
                event.accept()

            elif reply == QMessageBox.StandardButton.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def save_file_by_path(self, file_path, content):
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            self.tab_widget.setTabText(
                self.tab_widget.currentIndex(), os.path.basename(file_path))
            self.current_directory = os.path.dirname(file_path)
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Ошибка при сохранении файла: {e}")

    def save_application_state(self):
        settings = QSettings("harakki", "PlantCareEditor")

        # Сохраняем текущую директорию
        settings.setValue("current_directory", self.current_directory)

        # Сохраняем информацию об открытых файлах
        open_files = []
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if isinstance(editor, QTextEdit):
                file_path = self.tab_widget.tabToolTip(i)
                if file_path:  # Сохраняем только если файл существует
                    open_files.append(
                        {"path": file_path, "content": editor.toPlainText()})
        settings.setValue("open_files", json.dumps(open_files))

        # Сохраняем геометрию окна
        settings.setValue("geometry", self.saveGeometry())
        # Сохраняем состояние окна
        settings.setValue("windowState", self.saveState())

    def restore_application_state(self):
        settings = QSettings("harakki", "PlantCareEditor")

        # Восстанавливаем текущую директорию
        self.current_directory = settings.value(
            "current_directory", QDir.currentPath())
        self.file_model.setRootPath(self.current_directory)
        self.file_view.setRootIndex(
            self.file_model.index(self.current_directory))

        # Восстанавливаем открытые файлы
        open_files = json.loads(settings.value("open_files", "[]"))
        for file_data in open_files:
            file_path = file_data.get("path")  # получаем путь к файлу

            # проверяем, что файл существует
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        self.create_new_tab(content)
                        self.tab_widget.setTabText(
                            self.tab_widget.currentIndex(), os.path.basename(file_path))
                        self.tab_widget.setTabToolTip(
                            self.tab_widget.currentIndex(), file_path)
                except Exception as e:
                    print(f"Ошибка при восстановлении файла: {e}")

            else:
                self.create_new_tab(file_data.get("content"))

        # Восстанавливаем геометрию
        if settings.value("geometry"):
            self.restoreGeometry(settings.value("geometry"))
        # Восстанавливаем состояние
        if settings.value("windowState"):
            self.restoreState(settings.value("windowState"))

        if self.tab_widget.count() == 0:
            self.create_new_tab()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet('QWidget { font-family: Arial; font-size: 14px; }')

    PlantCareEditor = PlantCareEditor()
    PlantCareEditor.show()

    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing Window...')
