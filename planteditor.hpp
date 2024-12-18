#ifndef PLANTEDITOR_HPP
#define PLANTEDITOR_HPP

#include <QAction>
#include <QFileDialog>
#include <QMainWindow>
#include <QMenuBar>
#include <QSplitter>
#include <QTextBrowser>
#include <QTextEdit>
#include <QRegularExpression>
#include <QToolBar>
#include <QSyntaxHighlighter>
#include <QTextCharFormat>

QT_BEGIN_NAMESPACE
namespace Ui
{
    class PlantEditor;
}
QT_END_NAMESPACE

class PlantEditor : public QMainWindow
{
    Q_OBJECT

public:
    PlantEditor(QWidget *parent = nullptr);
    ~PlantEditor();

private slots:
    void newFile();
    void openFile();
    void saveFile();

    void makeBold();
    void makeItalic();
    void makeCode();
    
    void insertImage();
    void insertHeader();
    void insertList();
    void updatePreview();

private:
    Ui::PlantEditor *ui;
    QTextEdit *editor;     // Для редактирования Markdown
    QTextBrowser *preview; // Для отображения HTML
    QSplitter *splitter;   // Для разделения редактора и превью
};

class MarkdownHighlighter : public QSyntaxHighlighter
{
    Q_OBJECT

public:
    MarkdownHighlighter(QTextDocument *parent = nullptr);

protected:
    void highlightBlock(const QString &text) override;

private:
    QTextCharFormat headerFormat;
    QTextCharFormat boldFormat;
    QTextCharFormat italicFormat;
    QTextCharFormat codeFormat;
    QTextCharFormat listFormat;
    QTextCharFormat linkFormat;
};

#endif // PLANTEDITOR_HPP
