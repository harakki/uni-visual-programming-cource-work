#include "planteditor.hpp"
#include "./ui_planteditor.h"

PlantEditor::PlantEditor(QWidget *parent)
    : QMainWindow(parent), ui(new Ui::PlantEditor)
{
    ui->setupUi(this);

    setWindowTitle("Редактор справочника по уходу за растениями");
    resize(1000, 600);

    // Создаем разделитель
    splitter = new QSplitter(this);
    setCentralWidget(splitter);

    // Редактор Markdown
    editor = new QTextEdit(this);
    splitter->addWidget(editor);

    // Предварительный просмотр
    preview = new QTextBrowser(this);
    splitter->addWidget(preview);

    // Настройка размера
    splitter->setStretchFactor(0, 2); // Редактор занимает больше места
    splitter->setStretchFactor(1, 1); // Превью занимает меньше места

    // Меню
    QMenu *fileMenu = menuBar()->addMenu("Файл");
    QAction *newAction = fileMenu->addAction("Создать");
    QAction *openAction = fileMenu->addAction("Открыть");
    QAction *saveAction = fileMenu->addAction("Сохранить");

    // Панель инструментов
    QToolBar *toolBar = addToolBar("Форматирование");
    toolBar->addAction("Жирный", this, SLOT(makeBold()));
    toolBar->addAction("Курсив", this, SLOT(makeItalic()));
    toolBar->addAction("Код", this, SLOT(makeCode()));
    toolBar->addAction("Изображение", this, SLOT(insertImage()));
    toolBar->addAction("Заголовок", this, SLOT(insertHeader()));
    toolBar->addAction("Список", this, SLOT(insertList()));

    // Добавление подсветки в текстовый редактор
    MarkdownHighlighter *highlighter = new MarkdownHighlighter(editor->document());

    // Соединение сигналов и слотов
    connect(newAction, &QAction::triggered, this, &PlantEditor::newFile);
    connect(openAction, &QAction::triggered, this, &PlantEditor::openFile);
    connect(saveAction, &QAction::triggered, this, &PlantEditor::saveFile);

    // Связываем изменение текста с обновлением превью
    connect(editor, &QTextEdit::textChanged, this, &PlantEditor::updatePreview);

    // Задаем начальное содержимое
    newFile();
}

PlantEditor::~PlantEditor()
{
    delete ui;
}

void PlantEditor::newFile()
{
    editor->clear();

    // Шаблон статьи
    QString templateText = "# Растение\n\n"
                           "## Описание\n"
                           "Краткое описание растения.\n\n"
                           "## Условия для роста\n"
                           "- Температура: \n"
                           "- Влажность: \n\n"
                           "## Полив\n"
                           "- Частота: \n\n"
                           "## Удобрения\n"
                           "- Виды удобрений: \n";

    editor->setPlainText(templateText);
    updatePreview();
}

void PlantEditor::openFile()
{
    QString fileName = QFileDialog::getOpenFileName(this,
                                                    "Открыть файл",
                                                    "",
                                                    "Файл Markdown (*.md)");
    if (!fileName.isEmpty())
    {
        QFile file(fileName);
        if (file.open(QIODevice::ReadOnly))
        {
            editor->setPlainText(file.readAll());
            updatePreview();
        }
    }
}

void PlantEditor::saveFile()
{
    QString fileName = QFileDialog::getSaveFileName(this,
                                                    "Сохранить файл",
                                                    "",
                                                    "Файл Markdown (*.md)");
    if (!fileName.isEmpty())
    {
        QFile file(fileName);
        if (file.open(QIODevice::WriteOnly))
        {
            file.write(editor->toPlainText().toUtf8());
        }
    }
}

void PlantEditor::makeBold()
{
    QTextCursor cursor = editor->textCursor();
    if (cursor.hasSelection())
    {
        QString selectedText = cursor.selectedText();
        cursor.insertText("**" + selectedText + "**");
    }
}

void PlantEditor::makeItalic()
{
    QTextCursor cursor = editor->textCursor();
    if (cursor.hasSelection())
    {
        QString selectedText = cursor.selectedText();
        cursor.insertText("*" + selectedText + "*");
    }
}

void PlantEditor::makeCode()
{
    QTextCursor cursor = editor->textCursor();
    if (cursor.hasSelection())
    {
        QString selectedText = cursor.selectedText();
        cursor.insertText("`" + selectedText + "`");
    }
}

void PlantEditor::insertImage()
{
    QString filePath = QFileDialog::getOpenFileName(this,
                                                    "Выбрать изображение",
                                                    "",
                                                    "Изображение (*.png *.jpg *.jpeg *.bmp *.gif)");
    if (!filePath.isEmpty())
    {
        QString markdownImage = QString("![Описание изображения](%1)").arg(filePath);
        QTextCursor cursor = editor->textCursor();
        cursor.insertText(markdownImage);
        updatePreview();
    }
}

void PlantEditor::insertHeader()
{
    QTextCursor cursor = editor->textCursor();
    cursor.insertText("# \n");
    updatePreview();
}

void PlantEditor::insertList()
{
    QTextCursor cursor = editor->textCursor();
    cursor.insertText("- \n");
    updatePreview();
}

void PlantEditor::updatePreview()
{
    QString markdownText = editor->toPlainText();

    // Простой рендеринг Markdown через QTextBrowser
    QString html = markdownText;

    html.replace("\n", "<br>");
    html.replace(QRegularExpression("```([^`]*)```"), "<pre><code>\\1</code></pre>");
    html.replace(QRegularExpression("^# (.*)$"), "<h1>\\1</h1>");
    html.replace(QRegularExpression("^## (.*)$"), "<h2>\\1</h2>");
    html.replace(QRegularExpression("^### (.*)$"), "<h3>\\1</h3>");
    html.replace(QRegularExpression("^#### (.*)$"), "<h4>\\1</h4>");
    html.replace(QRegularExpression("^##### (.*)$"), "<h5>\\1</h5>");
    html.replace(QRegularExpression("^###### (.*)$"), "<h6>\\1</h6>");
    html.replace(QRegularExpression("\\*\\*([^*]+)\\*\\*"), "<b>\\1</b>");
    html.replace(QRegularExpression("\\*([^*]+)\\*"), "<i>\\1</i>");
    html.replace(QRegularExpression("^- (.*)$"), "<ul><li>\\1</li></ul>");
    html.replace(QRegularExpression("^\\d+\\. (.*)$"), "<ol><li>\\1</li></ol>");

    // Обработка таблиц
    QRegularExpression tableRegex("\\|(.+)\\|");
    QRegularExpressionMatchIterator tableIterator = tableRegex.globalMatch(markdownText);
    while (tableIterator.hasNext())
    {
        QRegularExpressionMatch match = tableIterator.next();
        QString tableRow = match.captured(1);
        QStringList cells = tableRow.split("|");
        QString htmlRow = "<tr>";
        for (const QString &cell : cells)
        {
            htmlRow += "<td>" + cell.trimmed() + "</td>";
        }
        htmlRow += "</tr>";
        html.replace(match.captured(0), htmlRow);
    }
    html.replace(QRegularExpression("<br><tr>"), "<table><tr>");
    html.replace(QRegularExpression("</tr><br>"), "</tr></table><br>");

    preview->setHtml(html);
}

MarkdownHighlighter::MarkdownHighlighter(QTextDocument *parent)
    : QSyntaxHighlighter(parent)
{
    // Формат заголовков
    headerFormat.setFontWeight(QFont::Bold);
    headerFormat.setForeground(Qt::blue);

    // Формат жирного текста
    boldFormat.setFontWeight(QFont::Bold);
    boldFormat.setForeground(Qt::black);

    // Формат курсивного текста
    italicFormat.setFontItalic(true);
    italicFormat.setForeground(Qt::darkGray);

    // Формат кода
    codeFormat.setFontFamilies({"Courier"});
    codeFormat.setForeground(Qt::darkGreen);

    // Формат списков
    listFormat.setForeground(Qt::darkMagenta);

    // Формат ссылок
    linkFormat.setForeground(Qt::darkCyan);
    linkFormat.setFontUnderline(true);
}

void MarkdownHighlighter::highlightBlock(const QString &text)
{
    // Заголовки (например, # Заголовок 1)
    QRegularExpression headerRegex("^#{1,6} ");
    QRegularExpressionMatch match = headerRegex.match(text);
    if (match.hasMatch())
    {
        int index = match.capturedStart();
        int length = match.capturedLength();
        setFormat(index, length, headerFormat);
    }

    // Жирный текст (**жирный текст**)
    QRegularExpression boldRegex("\\*\\*[^\\*]+\\*\\*");
    QRegularExpressionMatchIterator boldIterator = boldRegex.globalMatch(text);
    while (boldIterator.hasNext())
    {
        QRegularExpressionMatch match = boldIterator.next();
        int index = match.capturedStart();
        int length = match.capturedLength();
        setFormat(index, length, boldFormat);
    }

    // Курсивный текст (*курсивный текст*)
    QRegularExpression italicRegex("\\*[^\\*]+\\*");
    QRegularExpressionMatchIterator italicIterator = italicRegex.globalMatch(text);
    while (italicIterator.hasNext())
    {
        QRegularExpressionMatch match = italicIterator.next();
        int index = match.capturedStart();
        int length = match.capturedLength();
        setFormat(index, length, italicFormat);
    }

    // Инлайн-код (`код`)
    QRegularExpression inlineCodeRegex("`[^`]+`");
    QRegularExpressionMatchIterator codeIterator = inlineCodeRegex.globalMatch(text);
    while (codeIterator.hasNext())
    {
        QRegularExpressionMatch match = codeIterator.next();
        int index = match.capturedStart();
        int length = match.capturedLength();
        setFormat(index, length, codeFormat);
    }

    // Многострочный код (```код```)
    QRegularExpression codeBlockRegex("```[^`]*```");
    QRegularExpressionMatchIterator codeBlockIterator = codeBlockRegex.globalMatch(text);
    while (codeBlockIterator.hasNext())
    {
        QRegularExpressionMatch match = codeBlockIterator.next();
        int index = match.capturedStart();
        int length = match.capturedLength();
        setFormat(index, length, codeFormat);
    }

    // Списки (- пункт)
    QRegularExpression listRegex("^-\\s");
    QRegularExpressionMatchIterator listIterator = listRegex.globalMatch(text);
    while (listIterator.hasNext())
    {
        QRegularExpressionMatch match = listIterator.next();
        int index = match.capturedStart();
        int length = match.capturedLength();
        setFormat(index, length, listFormat);
    }

    // Нумерованные списки (1. пункт)
    QRegularExpression numberedListRegex("^\\d+\\.\\s");
    QRegularExpressionMatchIterator numberedListIterator = numberedListRegex.globalMatch(text);
    while (numberedListIterator.hasNext())
    {
        QRegularExpressionMatch match = numberedListIterator.next();
        int index = match.capturedStart();
        int length = match.capturedLength();
        setFormat(index, length, listFormat);
    }

    // Ссылки ([текст](url))
    QRegularExpression linkRegex("\\[.*\\]\\(.*\\)");
    QRegularExpressionMatchIterator linkIterator = linkRegex.globalMatch(text);
    while (linkIterator.hasNext())
    {
        QRegularExpressionMatch match = linkIterator.next();
        int index = match.capturedStart();
        int length = match.capturedLength();
        setFormat(index, length, linkFormat);
    }
}
