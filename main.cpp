#include "planteditor.hpp"

#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    PlantEditor w;
    w.show();
    return a.exec();
}
